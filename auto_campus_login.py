#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Campus Network Auto Login CLI

Copyright (c) 2025 yushi-xh
License: MIT

This module provides command-line utilities to detect captive portals and perform
login workflows for campus network authentication systems.

Safety:
- Does not upload data to third-party services.
- Accepts credentials via CLI args or environment variables.
- Avoids writing any credentials to disk unless the GUI config is used.
"""
import os
import re
import time
import logging
import argparse
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
import base64
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

# 用于探测认证门户的URL列表（用于 find_captive_portal）
DEFAULT_PROBE_URLS = [
    "http://www.xinhuanet.com/",
    "http://www.163.com/",
    "http://www.baidu.com/",
]

USER_ENV = "CAMPUS_USER"
PASS_ENV = "CAMPUS_PASS"

# Extend common field patterns, including camelCase and vendor-specific
COMMON_USER_FIELDS = [
    "username", "user", "account", "uname", "loginname", "userid", "user_name",
    "userName", "loginName", "userId", "DDDDD"
]
COMMON_PASS_FIELDS = [
    "password", "pass", "passwd", "pwd",
    "userPwd", "passWord", "Password", "upass"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/118.0 Safari/537.36"
}


def setup_logger(verbosity: int):
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler()]
    )


def internet_ok(session: requests.Session, timeout: float = 10.0) -> bool:
    """
    检测网络是否可达（改进版：多URL轮询，降低误判）

    探测策略:
    1. 尝试 multiple endpoints (www.xinhuanet.com, www.163.com, www.baidu.com)
    2. 任意一个成功返回 200 即认为在线
    3. 超时 10 秒，给弱网环境留足够时间
    4. 优化探测地址，提升稳定性

    Args:
        session: requests Session 对象
        timeout: 单次请求超时时间（秒），默认 10 秒

    Returns:
        bool: True 如果网络可达，False 如果判定为离线
    """
    # 探测地址列表（按优先级排序）
    probe_endpoints = [
        ("http://www.xinhuanet.com", 200),  # 新华网
        ("http://www.163.com", 200),  # 网易
        ("http://www.baidu.com", 200),  # 百度
    ]

    for url, expected_status in probe_endpoints:
        try:
            start_time = time.time()
            resp = session.get(url, timeout=timeout, allow_redirects=False, headers=HEADERS)
            elapsed = (time.time() - start_time) * 1000

            logging.debug("[Probe] %s -> %d in %.0f ms", url, resp.status_code, elapsed)

            # 如果返回期望的状态码，说明网络正常
            if resp.status_code == expected_status:
                return True

            # 如果遇到重定向，说明可能遇到认证门户
            if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("Location") or resp.headers.get("location")
                logging.debug("[Probe] Redirect detected to: %s", location)
                return False

        except requests.Timeout:
            logging.debug("[Probe] %s timeout after %d s", url, timeout)
            continue
        except requests.RequestException as e:
            logging.debug("[Probe] %s error: %s", url, e)
            continue

    # 所有探测都失败，认为网络不可达
    logging.debug("[Probe] All endpoints failed, network considered unreachable")
    return False


def find_captive_portal(session: requests.Session, probe_urls=None, timeout: float = 6.0):
    probe_urls = probe_urls or DEFAULT_PROBE_URLS
    for url in probe_urls:
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=False, headers=HEADERS)
            logging.info("Probe %s -> %s", url, resp.status_code)
            if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("Location") or resp.headers.get("location")
                if location:
                    logging.info("Captured captive portal redirect: %s", location)
                    return location
        except requests.RequestException as e:
            logging.debug("Probe %s failed: %s", url, e)
    return None


def pick_login_form(soup: BeautifulSoup):
    forms = soup.find_all("form")
    if not forms:
        return None
    forms_sorted = sorted(forms, key=lambda f: len(f.find_all(["input", "select", "button"])) , reverse=True)
    logging.debug("Found %d forms on page", len(forms))
    return forms_sorted[0]


def extract_form_data(form):
    data = {}
    action = form.get("action") or ""
    method = (form.get("method") or "get").lower()

    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        t = (inp.get("type") or "text").lower()
        value = inp.get("value") if t in ("hidden", "text", "email", "tel") else ""
        data[name] = value

    for sel in form.find_all("select"):
        name = sel.get("name")
        if not name:
            continue
        selected = sel.find("option", selected=True) or sel.find("option")
        if selected and selected.get("value") is not None:
            data[name] = selected.get("value")

    # Keep a pretty-printed snapshot for debugging
    try:
        snippet = str(form)[:1000]
        logging.debug("Form HTML snippet: %s", snippet)
    except Exception:
        pass

    return action, method, data


def guess_field_name(names, candidates):
    for n in candidates:
        if n is None:
            continue
        n_low = n.lower()
        for key in names:
            if re.search(r"(^|[_.-])" + re.escape(key.lower()) + r"($|[_.-])", n_low):
                return n
    for n in candidates:
        if n is None:
            continue
        n_low = n.lower()
        for key in names:
            if key.lower() in n_low:
                return n
    return None


def redact_payload(d: dict, pass_keys=tuple(k.lower() for k in COMMON_PASS_FIELDS)):
    out = {}
    for k, v in d.items():
        if k and k.lower() in pass_keys:
            out[k] = "***"
        else:
            out[k] = v
    return out


def merge_query_params_into_data(url: str, data: dict):
    try:
        q = parse_qs(urlparse(url).query)
        for k, vals in q.items():
            if k not in data and vals:
                data[k] = vals[0]
    except Exception:
        pass


def _save_debug_response(resp, suffix: str = ""):
    """Save response HTML and brief meta to local files for debugging (disabled by default)."""
    # Disabled to avoid cluttering workspace; re-enable if troubleshooting is needed
    pass


def try_direct_submit_without_form(session: requests.Session, page_url: str, username: str, password: str, timeout: float = 8.0):
    # Common fallback pairs
    candidates = [
        ("username", "password"),
        ("userName", "userPwd"),
        ("loginName", "passWord"),
        ("DDDDD", "upass"),
        ("userId", "passwd"),
    ]
    for uf, pf in candidates:
        data = {uf: username, pf: password}
        merge_query_params_into_data(page_url, data)
        headers = HEADERS.copy()
        headers["Referer"] = page_url
        try:
            logging.info("Fallback submit with fields (%s, %s) to %s", uf, pf, page_url)
            resp = session.post(page_url, data=data, timeout=timeout, headers=headers, allow_redirects=True)
            _save_debug_response(resp, suffix=f"_fallback_{uf}_{pf}")
            if internet_ok(session):
                logging.info("Login successful via fallback (%s, %s)", uf, pf)
                return True
            text_low = resp.text.lower()
            failure_keywords = ["error", "failed", "密码", "错误", "失败", "invalid", "认证失败", "请重试"]
            if any(k in text_low for k in failure_keywords):
                continue
            time.sleep(1.0)
            if internet_ok(session):
                return True
        except requests.RequestException:
            continue
    return False


def perform_login(session: requests.Session, login_url: str, username: str, password: str, user_field_override: str = None, pass_field_override: str = None, extra_params: Dict[str, str] = None, timeout: float = 8.0) -> bool:
    logging.info("Opening login page: %s", login_url)
    try:
        page = session.get(login_url, timeout=timeout, headers=HEADERS)
    except requests.RequestException as e:
        logging.error("Failed to open login page: %s", e)
        return False

    soup = BeautifulSoup(page.text, "html.parser")
    _save_debug_response(page, suffix="_page")
    form = pick_login_form(soup)
    if not form:
        logging.warning("No form found on portal page, trying fallback direct submit")
        return try_direct_submit_without_form(session, page.url, username, password, timeout=timeout)

    action, method, data = extract_form_data(form)

    # Log form fields for troubleshooting
    logging.debug("Form action=%s method=%s fields=%s", action, method, list(data.keys()))

    # Determine username/password field names
    all_names = list(data.keys())
    user_field = user_field_override or guess_field_name(COMMON_USER_FIELDS, all_names)
    pass_field = pass_field_override or guess_field_name(COMMON_PASS_FIELDS, all_names)

    if not user_field or not pass_field:
        logging.error("Could not identify username/password fields. Found fields: %s", all_names)
        return False

    # Build base payload
    data[user_field] = username
    data[pass_field] = password

    # Append query params if missing
    merge_query_params_into_data(page.url, data)
    if extra_params:
        data.update(extra_params)

    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}

    submit_url = urljoin(page.url, action) if action else page.url
    headers = HEADERS.copy()
    headers["Referer"] = page.url
    parsed = urlparse(submit_url)
    headers["Origin"] = f"{parsed.scheme}://{parsed.hostname}" if parsed.scheme and parsed.hostname else headers.get("Origin", "")

    logging.info("Submitting credentials to: %s (method=%s)", submit_url, method.upper())
    logging.debug("Payload keys=%s", list(data.keys()))
    logging.debug("Payload sample=%s", redact_payload(data))

    # Try multiple password encodings and loginType variants if needed
    attempts = []

    def add_attempt(name, base):
        attempts.append((name, base.copy()))

    # base variants for loginType
    base_variants = []
    for lt in [data.get("loginType"), "1", "0", ""]:
        d0 = data.copy()
        if lt is not None:
            d0["loginType"] = lt
        base_variants.append(d0)

    # tokens possibly required by portal JS
    echostr = str(data.get("echostr") or "")
    distoken = str(data.get("distoken") or "")

    # assemble attempts
    for base in base_variants:
        add_attempt("plain", base)
        # md5(password)
        try:
            d = base.copy(); d[pass_field] = hashlib.md5(password.encode("utf-8")).hexdigest(); add_attempt("md5", d)
        except Exception:
            pass
        # base64(password)
        try:
            d = base.copy(); d[pass_field] = base64.b64encode(password.encode("utf-8")).decode("ascii"); add_attempt("b64", d)
        except Exception:
            pass
        # md5(password+echostr)
        if echostr:
            try:
                d = base.copy(); d[pass_field] = hashlib.md5((password + echostr).encode("utf-8")).hexdigest(); add_attempt("md5_pwd_echostr", d)
            except Exception:
                pass
            try:
                d = base.copy(); d[pass_field] = hashlib.md5((hashlib.md5(password.encode()).hexdigest() + echostr).encode()).hexdigest(); add_attempt("md5_md5pwd_echostr", d)
            except Exception:
                pass
        # md5(password+distoken)
        if distoken:
            try:
                d = base.copy(); d[pass_field] = hashlib.md5((password + distoken).encode("utf-8")).hexdigest(); add_attempt("md5_pwd_distoken", d)
            except Exception:
                pass
        # uppercase MD5 variants
        try:
            d = base.copy(); d[pass_field] = hashlib.md5(password.encode("utf-8")).hexdigest().upper(); add_attempt("md5_upper", d)
        except Exception:
            pass

    # De-duplicate attempts by payload keys+hash
    seen = set()
    uniq_attempts = []
    for name, pl in attempts:
        key = (name, tuple(sorted(pl.items())))
        if key in seen:
            continue
        seen.add(key)
        uniq_attempts.append((name, pl))

    for mode, payload in uniq_attempts:
        logging.debug("Trying mode=%s loginType=%s", mode, payload.get("loginType"))
        try:
            if method == "post":
                resp = session.post(submit_url, data=payload, timeout=timeout, headers=headers, allow_redirects=True)
            else:
                resp = session.get(submit_url, params=payload, timeout=timeout, headers=headers, allow_redirects=True)
        except requests.RequestException as e:
            logging.error("Login submit failed (mode=%s): %s", mode, e)
            continue

        # log brief response clue
        try:
            title = re.search(r"<title>(.*?)</title>", resp.text, re.I|re.S)
            if title:
                logging.debug("Response title (mode=%s): %s", mode, title.group(1).strip())
        except Exception:
            pass

        _save_debug_response(resp, suffix=f"_{mode}")
        if internet_ok(session):
            logging.info("Login successful: internet access restored (mode=%s)", mode)
            return True

        text_low = resp.text.lower()
        failure_keywords = ["error", "failed", "密码", "错误", "失败", "invalid", "login again", "认证失败", "请重试"]
        if any(k in text_low for k in failure_keywords):
            logging.debug("Portal suggests failure (mode=%s)", mode)
            continue
        time.sleep(1.0)
        if internet_ok(session):
            logging.info("Login likely successful after delay (mode=%s).", mode)
            return True

    logging.warning("All login attempts failed with multiple modes and variants.")
    return False


def main():
    parser = argparse.ArgumentParser(description="校园网 Web 认证自动登录脚本")
    parser.add_argument("-u", "--username", default=os.getenv(USER_ENV), help=f"用户名（也可用环境变量 {USER_ENV}）")
    parser.add_argument("-p", "--password", default=os.getenv(PASS_ENV), help=f"密码（也可用环境变量 {PASS_ENV}）")
    parser.add_argument("--user-field", dest="user_field", default=None, help="表单中用户名字段名覆盖，如 username")
    parser.add_argument("--pass-field", dest="pass_field", default=None, help="表单中密码字段名覆盖，如 password")
    parser.add_argument("--probe", nargs="*", default=None, help="探测URL（空格分隔），默认使用内置列表")
    parser.add_argument("--portal", dest="portal", default=None, help="指定固定认证入口URL，跳过探测")
    parser.add_argument("--extra", dest="extra", action="append", default=[], help="附加表单字段，格式 k=v，可重复")
    parser.add_argument("--retries", type=int, default=3, help="登录重试次数")
    parser.add_argument("--interval", type=float, default=3.0, help="重试间隔秒")
    parser.add_argument("--watch", action="store_true", help="监控网络：当检测到无法联网时自动尝试登录")
    parser.add_argument("--watch-interval", type=float, default=5.0, help="监控模式下检测间隔秒")
    parser.add_argument("-v", action="count", default=0, help="日志详细程度，-v 或 -vv")

    args = parser.parse_args()
    setup_logger(args.v)

    if not args.username or not args.password:
        logging.error("缺少用户名或密码。请使用 -u/-p 或设置环境变量 %s/%s", USER_ENV, PASS_ENV)
        return 2

    # parse extras k=v
    extras: Dict[str, str] = {}
    for item in args.extra:
        if item and "=" in item:
            k, v = item.split("=", 1)
            extras[k] = v

    session = requests.Session()

    if args.watch:
        logging.info("进入监控模式：每 %.1f 秒检测一次网络可达性", args.watch_interval)
        fail_count = 0  # 连续失败计数器
        FAIL_THRESHOLD = 3  # 达到此阈值才认为真正断网

        while True:
            try:
                if internet_ok(session):
                    if fail_count > 0:
                        logging.debug("[Network] Recovered from %d consecutive failures", fail_count)
                    fail_count = 0  # 网络正常，重置计数器
                    logging.debug("网络正常，无需登录。")
                    time.sleep(args.watch_interval)
                    continue

                # 探测失败，增加计数
                fail_count += 1
                logging.debug("[Network] Detection failed %d/%d times", fail_count, FAIL_THRESHOLD)

                if fail_count < FAIL_THRESHOLD:
                    # 还没达到阈值，继续观察
                    logging.debug("网络探测失败，但尚未达到阈值 (%d/%d)，继续观察...",
                                 fail_count, FAIL_THRESHOLD)
                    time.sleep(args.watch_interval)
                    continue

                # 达到失败阈值，真正认为网络断开
                logging.warning("[Network] %d consecutive failures detected, network considered down",
                               fail_count)
                logging.info("检测到网络断开，触发自动登录...")

                portal_url = args.portal or find_captive_portal(session, probe_urls=args.probe or DEFAULT_PROBE_URLS)
                if not portal_url:
                    logging.warning("未捕获到认证重定向，稍后重试。")
                    time.sleep(args.watch_interval)
                    continue

                success = False
                for attempt in range(1, args.retries + 1):
                    logging.info("开始登录尝试 %d/%d", attempt, args.retries)
                    ok = perform_login(
                        session,
                        portal_url,
                        args.username,
                        args.password,
                        user_field_override=args.user_field,
                        pass_field_override=args.pass_field,
                        extra_params=extras,
                    )
                    if ok:
                        success = True
                        break
                    if attempt < args.retries:
                        time.sleep(args.interval)

                if success:
                    logging.info("登录流程结束，进入下一轮监控。")
                else:
                    logging.warning("本轮登录失败，将在 %.1f 秒后重试。", args.watch_interval)
                time.sleep(args.watch_interval)
            except Exception as e:
                logging.error("监控循环异常：%s", e)
                time.sleep(args.watch_interval)
    else:
        if internet_ok(session):
            logging.info("已联网，无需登录。")
            return 0

        portal_url = args.portal or find_captive_portal(session, probe_urls=args.probe or DEFAULT_PROBE_URLS)
        if not portal_url:
            logging.error("未捕获到认证重定向。可尝试指定 --probe 自定义探测URL。")
            return 1

        for attempt in range(1, args.retries + 1):
            logging.info("开始登录尝试 %d/%d", attempt, args.retries)
            ok = perform_login(
                session,
                portal_url,
                args.username,
                args.password,
                user_field_override=args.user_field,
                pass_field_override=args.pass_field,
                extra_params=extras,
            )
            if ok:
                return 0
            if attempt < args.retries:
                time.sleep(args.interval)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
