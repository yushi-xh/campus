#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园网自动登录 GUI 工具（v2.7）

Copyright (c) 2025 yushi-xh
License: MIT

功能概述：
- 现代化扁平设计，支持深浅主题
- 系统托盘运行、静默开机自启
- 网络监控与断网自动重连（默认 5 秒检测）
- 安全提示与注册表清理机制

安全说明：
- 配置文件包含明文密码，仅用于本地存储（可选）
- 不向第三方服务上传数据
- 发布时不包含个人配置文件
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime
import logging
from PIL import Image, ImageDraw
import pystray
import winreg  # Windows注册表操作

# 导入核心登录模块
from auto_campus_login import (
    internet_ok, find_captive_portal, perform_login,
    DEFAULT_PROBE_URLS, setup_logger
)
import requests


class ModernCheckbox(tk.Canvas):
    """现代扁平化自定义勾选框组件"""
    def __init__(self, parent, text="", variable=None, command=None, **kwargs):
        super().__init__(parent, width=18, height=18, highlightthickness=0, **kwargs)
        self.text = text
        self.variable = variable if variable else tk.BooleanVar()
        self.command = command
        self.theme_colors = {}
        
        # 创建文本标签
        self.label = tk.Label(parent, text=text, cursor="hand2")
        
        # 绑定事件
        self.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.label.bind("<Enter>", self.on_hover)
        self.label.bind("<Leave>", self.on_leave)
        
        self.is_hover = False
        self.draw()
        
        # 监听变量变化
        self.variable.trace_add("write", lambda *args: self.draw())
    
    def set_theme(self, colors):
        """设置主题颜色"""
        self.theme_colors = colors
        self.config(bg=colors['card_bg'])
        self.label.config(
            bg=colors['card_bg'],
            fg=colors['text'],
            font=('Microsoft YaHei UI', 9)
        )
        self.draw()
    
    def draw(self):
        """绘制勾选框"""
        self.delete("all")
        colors = self.theme_colors
        
        is_checked = self.variable.get()
        
        # 边框和背景颜色（增强对比度）
        if is_checked:
            fill_color = colors.get('primary', '#4a90e2')
            outline_color = colors.get('primary', '#4a90e2')
        else:
            fill_color = colors.get('card_bg', '#ffffff')
            # 增强未选中状态的边框可见度
            outline_color = colors.get('border_hover', '#d1d5db')
        
        # 悬停效果（更明显）
        if self.is_hover:
            if not is_checked:
                outline_color = colors.get('primary_light', '#6ba3e8')
                # 添加淡淡的背景高亮
                fill_color = colors.get('input_bg', '#f8f9fa')
        
        # 绘制圆角矩形（扁平化设计，边框加粗）
        self.create_rounded_rect(2, 2, 16, 16, radius=3, fill=fill_color, outline=outline_color, width=2.5)
        
        # 绘制勾选标记（更粗更明显）
        if is_checked:
            # 使用白色粗勾号
            self.create_line(5, 9, 8, 12, fill='white', width=2.5, capstyle=tk.ROUND)
            self.create_line(8, 12, 13, 6, fill='white', width=2.5, capstyle=tk.ROUND)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=4, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def toggle(self, event=None):
        """切换勾选状态"""
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()
    
    def on_hover(self, event=None):
        """悬停效果"""
        self.is_hover = True
        self.draw()
    
    def on_leave(self, event=None):
        """离开效果"""
        self.is_hover = False
        self.draw()


class ModernButton(tk.Canvas):
    """现代扁平化按钮"""
    def __init__(self, parent, text="", command=None, style='primary', **kwargs):
        self.btn_text = text
        self.btn_command = command
        self.btn_style = style
        self.theme_colors = {}
        self.is_hover = False
        self.is_pressed = False
        self.is_disabled = False
        
        super().__init__(parent, highlightthickness=0, **kwargs)
        
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_hover_enter)
        self.bind("<Leave>", self.on_hover_leave)
        
        # 绑定Configure事件,确保窗口大小变化时重绘
        self.bind("<Configure>", self.on_configure)
        
    def on_configure(self, event=None):
        """窗口配置改变时重绘"""
        self.draw()
        
    def set_theme(self, colors):
        """设置主题"""
        self.theme_colors = colors
        self.config(bg=colors['bg'])
        self.draw()
    
    def draw(self):
        """绘制按钮"""
        self.delete("all")
        colors = self.theme_colors
        
        # 根据样式选择颜色
        if self.btn_style == 'primary':
            bg_color = colors.get('primary', '#3b82f6')
            hover_color = colors.get('primary_hover', '#2563eb')
        elif self.btn_style == 'success':
            bg_color = colors.get('success', '#10b981')
            hover_color = colors.get('success_hover', '#059669')
        elif self.btn_style == 'danger':
            bg_color = colors.get('danger', '#ef4444')
            hover_color = colors.get('danger_hover', '#dc2626')
        else:
            bg_color = colors.get('primary', '#3b82f6')
            hover_color = colors.get('primary_hover', '#2563eb')
        
        # 应用悬停和按下效果
        if self.is_disabled:
            current_color = colors.get('text_light', '#9ca3af')
        elif self.is_pressed:
            current_color = hover_color
        elif self.is_hover:
            current_color = hover_color
        else:
            current_color = bg_color
        
        # 获取Canvas实际尺寸,如果未渲染则使用配置的尺寸
        width = self.winfo_width()
        height = self.winfo_height()
        
        # 如果canvas还没有渲染,使用配置的width和height
        if width <= 1:
            width = self.winfo_reqwidth()
        if height <= 1:
            height = self.winfo_reqheight()
        
        # 如果仍然没有尺寸,使用默认值
        if width <= 1:
            width = 200
        if height <= 1:
            height = 40
        
        # 绘制圆角矩形按钮
        self.create_rounded_rect(0, 0, width, height, radius=6, fill=current_color, outline='')
        
        # 绘制文字 - 使用anchor='center'确保居中
        self.create_text(
            width/2, height/2,
            text=self.btn_text,
            fill='white',
            font=('Microsoft YaHei UI', 10, 'bold'),
            anchor='center'
        )
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=6, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_press(self, event=None):
        """按下效果"""
        if not self.is_disabled:
            self.is_pressed = True
            self.draw()
    
    def on_release(self, event=None):
        """释放效果"""
        if not self.is_disabled:
            self.is_pressed = False
            self.draw()
            if self.btn_command:
                self.btn_command()
    
    def on_hover_enter(self, event=None):
        """鼠标进入"""
        self.is_hover = True
        self.config(cursor="hand2")
        self.draw()
    
    def on_hover_leave(self, event=None):
        """鼠标离开"""
        self.is_hover = False
        self.is_pressed = False
        self.config(cursor="")
        self.draw()
    
    def set_text(self, text):
        """更新文本"""
        self.btn_text = text
        self.draw()
    
    def set_state(self, state):
        """设置状态"""
        self.is_disabled = (state == 'disabled')
        self.draw()


class ThemeManager:
    """主题管理器"""
    
    THEMES = {
        'light': {
            'name': '浅色',
            'bg': '#f5f7fa',
            'card_bg': '#ffffff',
            'input_bg': '#f8f9fa',
            'text': '#1f2937',
            'text_secondary': '#6b7280',
            'text_light': '#9ca3af',
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'primary_light': '#60a5fa',
            'success': '#10b981',
            'success_hover': '#059669',
            'danger': '#ef4444',
            'danger_hover': '#dc2626',
            'warning': '#f59e0b',
            'border': '#e5e7eb',
            'border_hover': '#d1d5db',
            'status_online': '#10b981',
            'status_offline': '#ef4444',
            'log_bg': '#1e1e1e',
            'log_text': '#d4d4d4'
        },
        'dark': {
            'name': '深色',
            'bg': '#0f172a',           # 更深的背景
            'card_bg': '#1e293b',       # 卡片背景
            'input_bg': '#334155',      # 输入框背景
            'text': '#f1f5f9',          # 主要文字（更亮）
            'text_secondary': '#cbd5e1', # 次要文字
            'text_light': '#94a3b8',    # 辅助文字
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'primary_light': '#60a5fa',
            'success': '#10b981',
            'success_hover': '#059669',
            'danger': '#ef4444',
            'danger_hover': '#dc2626',
            'warning': '#f59e0b',
            'border': '#475569',        # 边框色（更亮）
            'border_hover': '#64748b',  # 悬停边框
            'status_online': '#34d399',
            'status_offline': '#f87171',
            'log_bg': '#0d1117',
            'log_text': '#e6edf3'
        }
    }
    
    @classmethod
    def get_theme(cls, theme_name='light'):
        """获取主题配色"""
        return cls.THEMES.get(theme_name, cls.THEMES['light'])


class CampusLoginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("校园网自动登录")
        self.root.geometry("480x620")
        self.root.minsize(420, 580)
        self.root.resizable(True, True)
        
        # 配置文件路径 - 修复打包后路径问题
        if getattr(sys, 'frozen', False):
            # 打包后的exe运行时,使用exe所在目录
            application_path = os.path.dirname(sys.executable)
        else:
            # 源码运行时,使用脚本所在目录
            application_path = os.path.dirname(__file__)
        self.config_file = os.path.join(application_path, "login_config.json")
        
        # 监控线程控制
        self.monitoring = False
        self.monitor_thread = None
        self.session = requests.Session()
        
        # 系统托盘
        self.tray_icon = None
        self.is_hidden = False
        
        # 主题管理（默认使用深色主题，与截图一致）
        self.current_theme = 'dark'
        self.theme_colors = ThemeManager.get_theme(self.current_theme)
        
        # 存储所有自定义组件
        self.checkboxes = []
        self.buttons = []
        self.widgets_to_theme = []
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
        
        # 设置日志
        self.setup_logging()
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建系统托盘图标
        self.create_tray_icon()
        
    def setup_styles(self):
        """设置现代化扁平样式"""
        colors = self.theme_colors
        self.root.configure(bg=colors['bg'])
        
    def create_widgets(self):
        """创建界面组件"""
        colors = self.theme_colors
        
        # 主容器
        self.main_container = tk.Frame(self.root, bg=colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 标题区域
        self.create_header(self.main_container)
        
        # 网络状态卡片
        self.create_status_card(self.main_container)
        
        # 登录信息卡片
        self.create_login_card(self.main_container)
        
        # 高级设置卡片
        self.create_advanced_card(self.main_container)
        
        # 操作按钮区域
        self.create_action_buttons(self.main_container)
        
        # 日志输出区域
        self.create_log_area(self.main_container)
        
    def create_header(self, parent):
        """创建标题区域"""
        colors = self.theme_colors
        header_frame = tk.Frame(parent, bg=colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        self.widgets_to_theme.append(('frame', header_frame))  # 添加到主题列表
        
        title_label = tk.Label(
            header_frame,
            text="🌐 校园网自动登录",
            font=('Microsoft YaHei UI', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['text']
        )
        title_label.pack(side=tk.LEFT)
        self.widgets_to_theme.append(('label', title_label))
        
        # 主题切换按钮
        theme_btn = tk.Label(
            header_frame,
            text="☀" if self.current_theme == 'light' else "🌙",
            font=('Segoe UI Emoji', 16),
            bg=colors['bg'],
            fg=colors['text'],
            cursor="hand2"
        )
        theme_btn.pack(side=tk.RIGHT, padx=(0, 10))
        theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())
        self.theme_switch_label = theme_btn
        self.widgets_to_theme.append(('label', theme_btn))
        
        version_label = tk.Label(
            header_frame,
            text="v2.7",
            font=('Consolas', 9),
            bg=colors['bg'],
            fg=colors['text_light']
        )
        version_label.pack(side=tk.RIGHT, pady=(6, 0))
        self.widgets_to_theme.append(('label', version_label))
        
    def create_status_card(self, parent):
        """创建网络状态卡片"""
        colors = self.theme_colors
        card = self.create_card(parent, "📡 网络状态")
        
        status_frame = tk.Frame(card, bg=colors['card_bg'])
        status_frame.pack(fill=tk.X, padx=15, pady=10)
        self.widgets_to_theme.append(('frame', status_frame))  # 添加到主题列表
        
        self.status_label = tk.Label(
            status_frame,
            text="● 未检测",
            font=('Microsoft YaHei UI', 10),
            bg=colors['card_bg'],
            fg=colors['text_light']
        )
        self.status_label.pack(side=tk.LEFT)
        self.widgets_to_theme.append(('label', self.status_label))
        
        # 使用自定义按钮
        check_btn = ModernButton(
            status_frame,
            text="检测网络",
            command=self.check_network_status,
            style='primary',
            width=90,
            height=32
        )
        check_btn.pack(side=tk.RIGHT)
        check_btn.set_theme(colors)
        self.buttons.append(check_btn)
        
    def create_login_card(self, parent):
        """创建登录信息卡片"""
        colors = self.theme_colors
        card = self.create_card(parent, "🔐 登录信息")
        
        form_frame = tk.Frame(card, bg=colors['card_bg'])
        form_frame.pack(fill=tk.X, padx=15, pady=10)
        self.widgets_to_theme.append(('frame', form_frame))  # 添加到主题列表
        
        # 用户名
        username_label = tk.Label(
            form_frame,
            text="用户名",
            font=('Microsoft YaHei UI', 9, 'bold'),
            bg=colors['card_bg'],
            fg=colors['text']
        )
        username_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.widgets_to_theme.append(('label', username_label))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            form_frame,
            textvariable=self.username_var,
            font=('Microsoft YaHei UI', 10),
            relief=tk.FLAT,
            bg=colors['input_bg'],
            fg=colors['text'],
            insertbackground=colors['text'],
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=colors['border'],
            highlightcolor=colors['primary']
        )
        self.username_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12), ipady=8)
        self.widgets_to_theme.append(('entry', self.username_entry))
        
        # 密码
        password_label = tk.Label(
            form_frame,
            text="密码",
            font=('Microsoft YaHei UI', 9, 'bold'),
            bg=colors['card_bg'],
            fg=colors['text']
        )
        password_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.widgets_to_theme.append(('label', password_label))
        
        password_frame = tk.Frame(form_frame, bg=colors['input_bg'])
        password_frame.grid(row=3, column=0, sticky=tk.EW, pady=(0, 12))
        self.widgets_to_theme.append(('frame', password_frame))  # 添加到主题列表
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=('Microsoft YaHei UI', 10),
            relief=tk.FLAT,
            bg=colors['input_bg'],
            fg=colors['text'],
            insertbackground=colors['text'],
            show='●',
            borderwidth=0
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), ipady=8)
        self.widgets_to_theme.append(('entry', self.password_entry))
        
        self.show_password_var = tk.BooleanVar()
        show_btn = tk.Label(
            password_frame,
            text="👁",
            font=('Segoe UI Emoji', 10),
            bg=colors['input_bg'],
            fg=colors['text_secondary'],
            cursor="hand2"
        )
        show_btn.pack(side=tk.RIGHT, padx=8)
        show_btn.bind("<Button-1>", lambda e: self.toggle_password())
        self.widgets_to_theme.append(('label', show_btn))
        
        # 记住密码复选框
        remember_frame = tk.Frame(form_frame, bg=colors['card_bg'])
        remember_frame.grid(row=4, column=0, sticky=tk.W, pady=(0, 0))
        self.widgets_to_theme.append(('frame', remember_frame))  # 添加到主题列表
        
        self.remember_var = tk.BooleanVar()
        remember_cb = ModernCheckbox(remember_frame, text="记住密码", variable=self.remember_var)
        remember_cb.pack(side=tk.LEFT)
        remember_cb.label.pack(side=tk.LEFT, padx=(5, 0))
        remember_cb.set_theme(colors)
        self.checkboxes.append(remember_cb)
        
        form_frame.columnconfigure(0, weight=1)
        
    def create_advanced_card(self, parent):
        """创建高级设置卡片"""
        colors = self.theme_colors
        card = self.create_card(parent, "⚙️ 高级设置")
        
        advanced_frame = tk.Frame(card, bg=colors['card_bg'])
        advanced_frame.pack(fill=tk.X, padx=15, pady=10)
        self.widgets_to_theme.append(('frame', advanced_frame))  # 添加到主题列表
        
        # 第一行选项
        row1 = tk.Frame(advanced_frame, bg=colors['card_bg'])
        row1.pack(fill=tk.X, pady=(0, 8))
        self.widgets_to_theme.append(('frame', row1))  # 添加到主题列表
        
        # 开机自启
        self.auto_reconnect_var = tk.BooleanVar()
        auto_cb = ModernCheckbox(row1, text="开机自启", variable=self.auto_reconnect_var)
        auto_cb.pack(side=tk.LEFT)
        auto_cb.label.pack(side=tk.LEFT, padx=(5, 20))
        auto_cb.set_theme(colors)
        self.checkboxes.append(auto_cb)
        
        # 重试次数
        retry_label = tk.Label(
            row1,
            text="重试次数:",
            font=('Microsoft YaHei UI', 9),
            bg=colors['card_bg'],
            fg=colors['text_secondary']
        )
        retry_label.pack(side=tk.LEFT, padx=(0, 8))
        self.widgets_to_theme.append(('label', retry_label))
        
        self.retry_var = tk.StringVar(value="3")
        retry_spin = tk.Spinbox(
            row1,
            from_=1,
            to=10,
            textvariable=self.retry_var,
            width=5,
            font=('Microsoft YaHei UI', 9),
            relief=tk.FLAT,
            bg=colors['input_bg'],
            fg=colors['text'],
            buttonbackground=colors['card_bg'],
            readonlybackground=colors['input_bg']
        )
        retry_spin.pack(side=tk.LEFT)
        self.widgets_to_theme.append(('spinbox', retry_spin))
        
    def create_action_buttons(self, parent):
        """创建操作按钮区域"""
        colors = self.theme_colors
        btn_frame = tk.Frame(parent, bg=colors['bg'])
        btn_frame.pack(fill=tk.X, pady=12)
        self.widgets_to_theme.append(('frame', btn_frame))  # 添加到主题列表
        
        # 登录按钮
        self.login_btn = ModernButton(
            btn_frame,
            text="立即登录",
            command=self.perform_login,
            style='primary',
            width=220,
            height=42
        )
        self.login_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        self.login_btn.set_theme(colors)
        self.buttons.append(self.login_btn)
        
        # 监控按钮
        self.monitor_btn = ModernButton(
            btn_frame,
            text="开始监控",
            command=self.toggle_monitoring,
            style='success',
            width=220,
            height=42
        )
        self.monitor_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.monitor_btn.set_theme(colors)
        self.buttons.append(self.monitor_btn)
        
    def create_log_area(self, parent):
        """创建日志输出区域"""
        colors = self.theme_colors
        log_frame = tk.LabelFrame(
            parent,
            text="📋 运行日志",
            font=('Microsoft YaHei UI', 10, 'bold'),
            bg=colors['card_bg'],
            fg=colors['text'],
            relief=tk.FLAT,
            borderwidth=0,
            labelanchor=tk.NW
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # 日志内容区域
        log_content = tk.Frame(log_frame, bg=colors['log_bg'])
        log_content.pack(fill=tk.BOTH, expand=True, padx=1, pady=(8, 1))
        
        self.log_text = scrolledtext.ScrolledText(
            log_content,
            height=8,
            font=('Consolas', 9),
            bg=colors['log_bg'],
            fg=colors['log_text'],
            relief=tk.FLAT,
            insertbackground=colors['log_text'],
            borderwidth=0,
            padx=10,
            pady=8
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.widgets_to_theme.append(('log', self.log_text))
        
        # 清除日志按钮
        clear_btn_frame = tk.Frame(log_frame, bg=colors['card_bg'])
        clear_btn_frame.pack(anchor=tk.E, padx=10, pady=(0, 8))
        
        clear_btn = tk.Label(
            clear_btn_frame,
            text="清除日志",
            font=('Microsoft YaHei UI', 8),
            bg=colors['card_bg'],
            fg=colors['text_secondary'],
            cursor="hand2"
        )
        clear_btn.pack()
        clear_btn.bind("<Button-1>", lambda e: self.clear_log())
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(fg=colors['primary']))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(fg=colors['text_secondary']))
        self.widgets_to_theme.append(('label', clear_btn))
        
    def create_card(self, parent, title):
        """创建卡片容器"""
        colors = self.theme_colors
        card = tk.LabelFrame(
            parent,
            text=title,
            font=('Microsoft YaHei UI', 10, 'bold'),
            bg=colors['card_bg'],
            fg=colors['text'],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=0,
            labelanchor=tk.NW
        )
        card.pack(fill=tk.X, pady=(0, 12))
        self.widgets_to_theme.append(('card', card))
        return card
    
    def toggle_theme(self):
        """切换主题"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.theme_colors = ThemeManager.get_theme(self.current_theme)
        self.apply_theme()
        
        # 更新主题图标
        self.theme_switch_label.config(text="☀" if self.current_theme == 'light' else "🌙")
        
        # 保存主题设置
        self.save_theme_preference()
    
    def apply_theme(self):
        """应用主题到所有组件"""
        colors = self.theme_colors
        
        # 更新根窗口和主容器
        self.root.configure(bg=colors['bg'])
        self.main_container.configure(bg=colors['bg'])
        
        # 更新所有存储的组件
        for widget_type, widget in self.widgets_to_theme:
            try:
                if widget_type == 'label':
                    # 智能判断标签背景色
                    try:
                        # 获取父组件背景色
                        parent = widget.master
                        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else colors['bg']
                        
                        # 根据父组件背景选择合适的背景色
                        if parent_bg in [colors['card_bg'], self.theme_colors.get('card_bg', '#ffffff')]:
                            widget.configure(bg=colors['card_bg'], fg=colors['text'])
                        elif parent_bg in [colors['input_bg'], self.theme_colors.get('input_bg', '#f8f9fa')]:
                            widget.configure(bg=colors['input_bg'], fg=colors['text_secondary'])
                        else:
                            widget.configure(bg=colors['bg'], fg=colors['text'])
                    except:
                        widget.configure(bg=colors['card_bg'], fg=colors['text'])
                        
                elif widget_type == 'entry':
                    widget.configure(
                        bg=colors['input_bg'],
                        fg=colors['text'],
                        insertbackground=colors['text'],
                        highlightbackground=colors['border'],
                        highlightcolor=colors['primary']
                    )
                    
                elif widget_type == 'spinbox':
                    widget.configure(
                        bg=colors['input_bg'],
                        fg=colors['text'],
                        buttonbackground=colors['card_bg'],
                        readonlybackground=colors['input_bg']
                    )
                    
                elif widget_type == 'card':
                    # LabelFrame 和 卡片
                    if isinstance(widget, tk.LabelFrame):
                        widget.configure(bg=colors['card_bg'], fg=colors['text'])
                    else:
                        widget.configure(bg=colors['card_bg'])
                        
                elif widget_type == 'frame':
                    # Frame 智能判断
                    try:
                        parent = widget.master
                        if hasattr(parent, 'cget'):
                            parent_bg = parent.cget('bg')
                            # 如果父组件是卡片背景，则使用卡片背景
                            if 'card' in str(parent.__class__.__name__).lower() or parent_bg == colors['card_bg']:
                                widget.configure(bg=colors['card_bg'])
                            elif parent_bg == colors['log_bg']:
                                widget.configure(bg=colors['log_bg'])
                            elif parent_bg == colors['input_bg']:
                                widget.configure(bg=colors['input_bg'])
                            else:
                                widget.configure(bg=colors['bg'])
                        else:
                            widget.configure(bg=colors['bg'])
                    except:
                        widget.configure(bg=colors['bg'])
                        
                elif widget_type == 'log':
                    widget.configure(
                        bg=colors['log_bg'],
                        fg=colors['log_text'],
                        insertbackground=colors['log_text']
                    )
                    
            except Exception as e:
                # 静默跳过错误，避免中断主题应用
                pass
        
        # 更新自定义勾选框
        for checkbox in self.checkboxes:
            try:
                checkbox.set_theme(colors)
            except:
                pass
        
        # 更新自定义按钮
        for button in self.buttons:
            try:
                button.set_theme(colors)
            except:
                pass
    
    def save_theme_preference(self):
        """保存主题偏好"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            config['theme'] = self.current_theme
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def toggle_password(self):
        """切换密码显示/隐藏"""
        if self.password_entry.cget('show') == '●':
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='●')
            
    def setup_logging(self):
        """设置日志"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
                
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
    def log(self, message, level='INFO'):
        """添加日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
        
    def check_network_status(self):
        """检测网络状态"""
        def check():
            self.log("正在检测网络状态...")
            colors = self.theme_colors
            if internet_ok(self.session):
                self.status_label.config(
                    text="● 网络正常",
                    fg=colors['status_online']
                )
                self.log("网络连接正常", "INFO")
            else:
                self.status_label.config(
                    text="● 未连接",
                    fg=colors['status_offline']
                )
                self.log("网络未连接或需要认证", "WARNING")
                
        threading.Thread(target=check, daemon=True).start()
        
    def perform_login(self):
        """执行登录"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showwarning("输入错误", "请输入用户名和密码！")
            return
            
        # 保存配置
        if self.remember_var.get():
            self.save_config()
            
        def login_thread():
            self.login_btn.set_state('disabled')
            self.login_btn.set_text("登录中...")
            self.log(f"开始登录，用户名: {username}")
            
            try:
                # 检查网络
                if internet_ok(self.session):
                    self.log("已联网，无需登录", "INFO")
                    messagebox.showinfo("提示", "网络已连接！")
                    return
                    
                # 查找认证入口
                self.log("正在查找认证入口...")
                portal_url = find_captive_portal(self.session, DEFAULT_PROBE_URLS)
                
                if not portal_url:
                    self.log("未找到认证入口", "ERROR")
                    messagebox.showerror("错误", "未找到认证入口！")
                    return
                    
                self.log(f"找到认证入口: {portal_url}")
                
                # 执行登录
                retry_count = int(self.retry_var.get())
                for attempt in range(1, retry_count + 1):
                    self.log(f"第 {attempt}/{retry_count} 次尝试登录...")
                    
                    success = perform_login(
                        self.session,
                        portal_url,
                        username,
                        password
                    )
                    
                    if success:
                        self.log("登录成功！", "INFO")
                        colors = self.theme_colors
                        self.status_label.config(
                            text="● 已连接",
                            fg=colors['status_online']
                        )
                        messagebox.showinfo("成功", "登录成功！")
                        return
                        
                self.log("登录失败，请检查用户名和密码", "ERROR")
                messagebox.showerror("失败", "登录失败！请检查账号密码。")
                
            except Exception as e:
                self.log(f"登录出错: {str(e)}", "ERROR")
                messagebox.showerror("错误", f"登录出错：{str(e)}")
            finally:
                self.login_btn.set_state('normal')
                self.login_btn.set_text("立即登录")
                
        threading.Thread(target=login_thread, daemon=True).start()
        
    def toggle_monitoring(self):
        """切换监控状态"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """开始监控"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showwarning("输入错误", "请先输入用户名和密码！")
            return
        
        # 如果勾选了记住我或开机自启,保存配置
        if self.remember_var.get() or self.auto_reconnect_var.get():
            self.save_config()
            
        self.monitoring = True
        self.monitor_btn.set_text("停止监控")
        self.monitor_btn.btn_style = 'danger'
        self.monitor_btn.draw()
        self.login_btn.set_state('disabled')
        
        self.log("开始网络监控...", "INFO")
        
        def monitor_loop():
            import time
            fail_count = 0  # 连续失败计数器
            FAIL_THRESHOLD = 3  # 达到此阈值才认为真正断网

            while self.monitoring:
                try:
                    if internet_ok(self.session):
                        if fail_count > 0:
                            self.log(f"网络恢复，之前连续失败 {fail_count} 次", "INFO")
                            fail_count = 0
                        else:
                            logging.debug("网络正常，继续监控...")
                    else:
                        # 探测失败，增加计数
                        fail_count += 1
                        logging.debug("[Network] Detection failed %d/%d times",
                                     fail_count, FAIL_THRESHOLD)

                        if fail_count >= FAIL_THRESHOLD:
                            # 达到阈值，真正认为网络断开
                            self.log(f"检测到网络断开（连续{fail_count}次失败），尝试重新登录...",
                                    "WARNING")

                            portal_url = find_captive_portal(self.session, DEFAULT_PROBE_URLS)
                            if portal_url:
                                success = perform_login(
                                    self.session,
                                    portal_url,
                                    username,
                                    password
                                )
                                if success:
                                    self.log("自动登录成功", "INFO")
                                    fail_count = 0  # 登录成功，重置计数
                                else:
                                    self.log("自动登录失败", "WARNING")
                        else:
                            # 还未达到阈值，只是记录日志
                            logging.debug("网络探测失败，但尚未达到阈值 (%d/%d)，继续观察...",
                                         fail_count, FAIL_THRESHOLD)

                    time.sleep(30)  # 每 30 秒检测一次（降低频率，减少资源消耗）
                except Exception as e:
                    self.log(f"监控出错: {str(e)}", "ERROR")
                    time.sleep(30)
                    
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.monitor_btn.set_text("开始监控")
        self.monitor_btn.btn_style = 'success'
        self.monitor_btn.draw()
        self.login_btn.set_state('normal')
        self.log("已停止网络监控", "INFO")
        
    def save_config(self):
        """保存配置"""
        config = {
            'username': self.username_var.get(),
            'password': self.password_var.get(),
            'remember': self.remember_var.get(),
            'auto_reconnect': self.auto_reconnect_var.get(),
            'retry': self.retry_var.get(),
            'theme': self.current_theme
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            self.log("配置已保存", "INFO")
            
            # 设置Windows开机自启
            if config['auto_reconnect']:
                if self.set_windows_startup(True):
                    self.log("已添加到系统开机启动", "INFO")
            else:
                if self.set_windows_startup(False):
                    self.log("已从系统开机启动移除", "INFO")
                    
        except Exception as e:
            self.log(f"保存配置失败: {str(e)}", "ERROR")
            
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.username_var.set(config.get('username', ''))
                self.password_var.set(config.get('password', ''))
                self.remember_var.set(config.get('remember', False))
                self.auto_reconnect_var.set(config.get('auto_reconnect', False))
                self.retry_var.set(config.get('retry', '3'))
                
                # 加载主题设置（默认深色主题）
                theme = config.get('theme', 'dark')
                if theme != self.current_theme:
                    self.current_theme = theme
                    self.theme_colors = ThemeManager.get_theme(theme)
                    self.apply_theme()
                    self.theme_switch_label.config(text="☀" if theme == 'light' else "🌙")
                
                self.log("配置已加载", "INFO")
                
                # 如果开启了开机自启,自动开始监控
                if config.get('auto_reconnect', False):
                    username = config.get('username', '').strip()
                    password = config.get('password', '').strip()
                    if username and password:
                        # 延迟1秒后自动启动监控,确保界面已完全加载
                        self.root.after(1000, self._auto_start_monitoring)
                        self.log("检测到开机自启配置,将自动开始监控...", "INFO")
                    else:
                        self.log("开机自启已启用,但未保存账号密码", "WARNING")
                        
            except Exception as e:
                self.log(f"加载配置失败: {str(e)}", "ERROR")
    
    def _auto_start_monitoring(self):
        """自动启动监控（内部方法）"""
        try:
            if not self.monitoring:
                self.start_monitoring()
                self.log("已自动开启网络监控", "INFO")
        except Exception as e:
            self.log(f"自动启动监控失败: {str(e)}", "ERROR")
    
    def set_windows_startup(self, enable=True):
        """设置Windows开机自启动"""
        try:
            # 获取exe路径
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                # 开发模式下使用Python脚本路径(实际不会用到)
                exe_path = os.path.abspath(__file__)
            
            # 注册表路径
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "校园网自动登录"
            
            # 打开注册表项
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            if enable:
                # 添加到开机启动,带上 --startup 参数让程序启动时隐藏窗口
                startup_cmd = f'"{exe_path}" --startup'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, startup_cmd)
                self.log("已添加到Windows开机启动项", "INFO")
                result = True
            else:
                # 从开机启动移除
                try:
                    winreg.DeleteValue(key, app_name)
                    self.log("已从Windows开机启动项移除", "INFO")
                    result = True
                except FileNotFoundError:
                    # 注册表项不存在,说明本来就没有设置
                    result = True
            
            winreg.CloseKey(key)
            return result
            
        except Exception as e:
            self.log(f"设置开机自启失败: {str(e)}", "ERROR")
            return False
    
    def check_windows_startup(self):
        """检查是否已设置Windows开机自启"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "校园网自动登录"
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        def create_icon_image():
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # 绘制渐变圆形
            draw.ellipse([8, 8, 56, 56], fill='#3b82f6', outline='#2563eb', width=3)
            
            # 绘制网络符号
            draw.arc([20, 24, 44, 40], 180, 360, fill='white', width=3)
            draw.arc([24, 28, 40, 40], 180, 360, fill='white', width=3)
            draw.ellipse([30, 36, 34, 40], fill='white')
            
            return image
        
        menu = pystray.Menu(
            pystray.MenuItem('显示主窗口', self.show_window, default=True),
            pystray.MenuItem('立即登录', self.tray_login),
            pystray.MenuItem(
                lambda text: f'{"停止" if self.monitoring else "开始"}监控',
                self.tray_toggle_monitor
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('检测网络', self.tray_check_network),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('退出程序', self.quit_app)
        )
        
        icon_image = create_icon_image()
        self.tray_icon = pystray.Icon(
            "campus_login",
            icon_image,
            "校园网自动登录",
            menu
        )
    
    def start_tray_icon(self):
        """在后台线程中启动托盘图标"""
        if self.tray_icon:
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def hide_window(self):
        """隐藏窗口到系统托盘"""
        self.root.withdraw()
        self.is_hidden = True
        if self.tray_icon and not self.tray_icon.visible:
            self.start_tray_icon()
        self.log("程序已最小化到系统托盘", "INFO")
    
    def show_window(self, icon=None, item=None):
        """从系统托盘恢复窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_hidden = False
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.monitoring:
            message = """监控正在运行中。

是(Y): 最小化到系统托盘继续运行
否(N): 停止监控并退出程序
取消: 返回"""
            result = messagebox.askyesnocancel("最小化到托盘", message)
            if result is True:
                self.hide_window()
            elif result is False:
                self.quit_app()
        else:
            message = """是否最小化到系统托盘？

是(Y): 最小化到托盘
否(N): 退出程序"""
            result = messagebox.askyesno("提示", message)
            if result:
                self.hide_window()
            else:
                self.quit_app()
    
    def tray_login(self, icon=None, item=None):
        """托盘菜单：立即登录"""
        self.root.after(0, self.perform_login)
    
    def tray_toggle_monitor(self, icon=None, item=None):
        """托盘菜单：切换监控状态"""
        self.root.after(0, self.toggle_monitoring)
    
    def tray_check_network(self, icon=None, item=None):
        """托盘菜单：检测网络"""
        self.root.after(0, self.check_network_status)
    
    def quit_app(self, icon=None, item=None):
        """完全退出应用"""
        if self.monitoring:
            self.stop_monitoring()
        
        # 退出前检查开机自启状态，如果未勾选则清理注册表
        try:
            if not self.auto_reconnect_var.get():
                # 用户没有勾选开机自启，确保注册表中的启动项被清除
                self.set_windows_startup(False)
        except Exception as e:
            # 忽略清理失败的错误，不影响程序退出
            pass
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        self.root.quit()
        self.root.destroy()


def main():
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='校园网自动登录工具')
    parser.add_argument('--startup', action='store_true', help='开机启动模式(隐藏窗口)')
    args = parser.parse_args()
    
    root = tk.Tk()
    
    # 设置应用图标
    try:
        if sys.platform == 'win32':
            root.iconbitmap('icon.ico')
    except:
        pass
        
    app = CampusLoginGUI(root)
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 启动系统托盘
    app.start_tray_icon()
    
    # 如果是开机启动模式且配置了自动启动,则隐藏窗口
    if args.startup:
        # 读取配置检查是否启用了开机自启
        if os.path.exists(app.config_file):
            try:
                with open(app.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('auto_reconnect', False):
                        # 延迟隐藏窗口,确保托盘图标已创建
                        root.after(500, app.hide_window)
                        app.log("开机启动模式:已最小化到系统托盘", "INFO")
            except:
                pass
    
    root.mainloop()


if __name__ == '__main__':
    main()
