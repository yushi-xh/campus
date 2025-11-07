# 🌐 校园网自动登录工具

一个功能强大的校园网自动登录工具，提供命令行和GUI两种使用方式，支持自动检测、重连和监控。

[![版本](https://img.shields.io/badge/version-2.6-blue.svg)](https://github.com/yourusername/campus-auto-login/releases)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![许可](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![平台](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/yourusername/campus-auto-login)

## ✨ 核心特性

### GUI版本 (推荐)
- 🎨 **现代化界面** - 简洁美观的深色/浅色主题
- 💾 **系统托盘** - 最小化到托盘后台运行
- 🚀 **开机自启** - Windows开机自动启动并隐藏到托盘
- ⚡ **极速响应** - 5秒网络检测间隔，断网快速恢复
- 🔐 **账号管理** - 安全保存登录信息，下次自动填充
- 👁️ **密码可见** - 可切换密码显示/隐藏
- 🔄 **智能重连** - 检测到断网立即自动登录
- 📊 **实时监控** - 持续监控网络状态
- 📝 **运行日志** - 详细的操作日志输出
- 🛡️ **智能清理** - 退出时自动清理注册表启动项
- ⚙️ **灵活配置** - 可自定义重试次数等参数
- 🖱️ **托盘菜单** - 右键快捷操作，支持后台运行

### 命令行版本
- 🚀 **快速登录** - 一行命令完成登录
- 🔍 **自动探测** - 智能查找认证入口
- 🔁 **多次重试** - 支持多种密码加密方式
- 👀 **监控模式** - 后台守护，断网自动重连
- 📊 **详细日志** - 支持多级日志输出
- 🛠️ **高级选项** - 支持自定义字段、探测URL等

## 📸 界面预览

### GUI界面
```
┌────────────────────────────────────────────┐
│  🌐 校园网自动登录              v2.6  🌙   │
├────────────────────────────────────────────┤
│  登录信息                                   │
│  用户名: ________________________________  │
│  密码:   ________________________________ 👁│
│  ☑ 记住我      ☑ 开机自启                 │
│  重试次数: [3▼]                            │
├────────────────────────────────────────────┤
│  [   立即登录   ]  [   开始监控   ]       │
├────────────────────────────────────────────┤
│  运行日志                         [清除]   │
│  [12:00:00] [INFO] 正在登录...            │
│  [12:00:02] [SUCCESS] 登录成功            │
│  [12:00:02] [INFO] 已添加到开机启动        │
└────────────────────────────────────────────┘
```

## 🚀 快速开始

### 方法一：直接使用可执行文件（推荐）

1. 从 [Releases](https://github.com/yourusername/campus-auto-login/releases) 下载最新版本
2. 下载 `校园网登录工具_v2.6.exe`（约 22 MB）
3. 双击运行
4. 输入账号密码，勾选"开机自启"
5. 点击"开始监控"

### 方法二：从源码运行

#### Windows

```bash
# 克隆项目
git clone https://github.com/yourusername/campus-auto-login.git
cd campus-auto-login

# 安装依赖
pip install -r requirements.txt

# 运行GUI版本
python campus_login_gui.py

# 或双击运行
运行GUI.bat
```

#### Linux/macOS

```bash
# 克隆项目
git clone https://github.com/yourusername/campus-auto-login.git
cd campus-auto-login

# 安装依赖
pip3 install -r requirements.txt

# 运行GUI版本
python3 campus_login_gui.py
```

## 📦 自己打包

### Windows平台

```bash
# 安装打包工具（固定版本便于复现）
pip install "pyinstaller>=5.13,<6.1"

# 使用优化配置打包（名称已对齐 v2.6）
pyinstaller build_config_optimized.spec --clean

# 打包后的 exe 在 dist/ 目录下
```

### Linux/macOS平台

```bash
# 安装打包工具
pip3 install pyinstaller

# 打包
pyinstaller --name="CampusLogin" \
            --windowed \
            --onefile \
            --icon=icon.ico \
            campus_login_gui.py
```

**打包说明：**
- 单文件模式：约 22 MB
- 包含所有依赖，无需安装Python
- 支持 UPX 压缩（已启用）

## 📖 使用指南

### GUI版本详细说明

#### 1. 首次使用
1. 输入校园网账号和密码
2. 勾选 ☑ "记住我"（保存账号密码）
3. 勾选 ☑ "开机自启"（添加到Windows启动项）
4. 点击"立即登录"或"开始监控"
5. 查看日志确认配置已保存

#### 2. 开机自启功能
- 勾选后会添加到 Windows 注册表
- 开机时自动启动并隐藏到系统托盘
- 自动开始网络监控
- 静默运行，无窗口打扰

#### 3. 网络监控
- 每 5 秒检测一次网络状态
- 检测到断网立即自动登录
- 支持后台运行
- 可在系统托盘查看状态

#### 4. 系统托盘功能
右键点击托盘图标可以：
- 显示/隐藏主窗口
- 立即登录
- 开始/停止监控
- 检测网络状态
- 退出程序

#### 5. 主题切换
- 点击右上角 🌙/☀ 图标
- 支持深色和浅色两种主题
- 主题设置自动保存

#### 6. 取消开机自启
- 取消勾选"开机自启"
- 点击"立即登录"或"开始监控"保存配置
- 或直接关闭程序（退出时自动清理注册表）

### 命令行版本详细说明

#### 基本用法

```bash
# 使用参数登录
python auto_campus_login.py -u 用户名 -p 密码

# 使用环境变量
export CAMPUS_USER=用户名
export CAMPUS_PASS=密码
python auto_campus_login.py
```

#### 监控模式

```bash
# 启动监控模式（5秒间隔）
python auto_campus_login.py -u 用户名 -p 密码 --watch

# 自定义检测间隔（60秒）
python auto_campus_login.py -u 用户名 -p 密码 --watch --watch-interval 60
```

#### 高级选项

```bash
# 详细日志
python auto_campus_login.py -u 用户名 -p 密码 -vv

# 指定重试次数
python auto_campus_login.py -u 用户名 -p 密码 --retries 5

# 指定认证URL（跳过探测）
python auto_campus_login.py -u 用户名 -p 密码 --portal http://portal.example.com

# 自定义表单字段名
python auto_campus_login.py -u 用户名 -p 密码 --user-field userId --pass-field userPwd

# 附加表单字段
python auto_campus_login.py -u 用户名 -p 密码 --extra loginType=1 --extra service=internet
```

#### 查看帮助

```bash
python auto_campus_login.py --help
```

## 🔧 配置文件

GUI版本会在程序同目录生成 `login_config.json` 配置文件：

```json
{
  "username": "your_username",
  "password": "your_password",
  "remember": true,
  "auto_reconnect": true,
  "retry": "3",
  "theme": "dark"
}
```

**安全提示：**
- ⚠️ 配置文件包含明文密码，请妥善保管
- 建议设置文件权限，防止他人访问
- 不要将配置文件上传到公共仓库
- 项目已配置 `.gitignore` 忽略该文件

## ❓ 常见问题

### Q: 开机后看不到程序窗口？
**A:** 这是正常的！开机启动时程序会直接隐藏到系统托盘。
- 在任务栏右下角托盘区查找程序图标
- 右键点击 → "显示主窗口"
- 或双击托盘图标

### Q: 网络检测速度如何？
**A:** v2.6 版本每 5 秒检测一次，断网后 5 秒内自动重连，比旧版本（30秒）快 6 倍！

### Q: 取消开机自启后忘记保存就关闭了？
**A:** 没问题！v2.6 会在退出时自动检测并清理注册表，即使忘记保存，注册表也会被正确清理。

### Q: 登录失败怎么办？
**A:**
1. 检查账号密码是否正确
2. 查看日志获取详细错误信息
3. 增加重试次数
4. 使用命令行版本的 `-vv` 参数查看详细调试信息

### Q: 程序无法运行？
**A:**
1. 确认 Python 版本 >= 3.8
2. 安装所有依赖：`pip install -r requirements.txt`
3. 检查是否在校园网环境

### Q: 如何移动程序位置？
**A:**
1. 先取消勾选"开机自启"并保存
2. 移动exe到新位置
3. 运行程序，重新勾选"开机自启"
4. 注册表会自动更新为新路径

### Q: 配置文件在哪？
**A:** 与 exe/py 文件同一目录下的 `login_config.json`

## 🔐 安全说明

1. **密码存储**
   - 配置文件中密码为明文存储
   - 建议设置文件权限（仅所有者可读写）
   - 不要分享配置文件给他人

2. **网络安全**
   - 程序仅在本地运行
   - 不上传任何信息到第三方服务器
   - 所有网络请求仅与校园网认证系统通信

3. **源码审查**
   - 完全开源，可自行审查代码
   - 欢迎安全专家提出建议

4. **分发建议**
   - 分发 exe 时不包含 `login_config.json`
   - 提供 `login_config.json.example` 作为模板

## 📋 系统要求

- **操作系统**：Windows 7+, Linux, macOS
- **Python**：3.8 或更高版本（源码运行）
- **依赖库**：
  - requests >= 2.31.0
  - beautifulsoup4 >= 4.12.2
  - pystray >= 0.19.5
  - pillow >= 10.0.0
- **网络环境**：校园网环境

## 🗂️ 项目结构

```
校园网自动登录工具/
├── auto_campus_login.py          # 核心登录逻辑（命令行版本）
├── campus_login_gui.py           # GUI程序主文件
├── build_config_optimized.spec   # PyInstaller优化打包配置
├── requirements.txt              # Python依赖清单
├── 运行GUI.bat                   # Windows快速启动脚本
├── icon.ico                      # 程序图标
├── login_config.json.example     # 配置文件示例
├── LICENSE                       # MIT许可证
├── README.md                     # 项目文档（本文件）
└── .gitignore                    # Git忽略配置
```

## 🤝 贡献指南

欢迎提交问题和改进建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

**代码规范：**
- 遵循 PEP 8 风格指南
- 添加适当的注释和文档字符串
- 确保代码通过测试

## 📝 更新日志

### v2.6 (2025-11-07) ⭐⭐⭐ 最新版本
- ⚡ **网络检测间隔优化**：30秒 → 5秒（提升6倍速度）
- 🛡️ **智能注册表清理**：退出时自动检测并清理启动项
- ✅ **双重保障机制**：保存时清理 + 退出时清理
- 📝 **完善文档**：更新使用说明和常见问题

### v2.5 (2025-11-06)
- 🚀 **静默开机启动**：开机时直接隐藏到托盘
- 📌 **命令行参数**：添加 `--startup` 参数支持
- 🎯 **真正的后台运行**：无窗口打扰

### v2.4 (2025-11-06)
- 🎨 **UI优化**：修复按钮文字偏移问题
- ✨ **界面美化**：提升视觉体验

### v2.3 (2025-11-06)
- 💻 **Windows开机自启**：添加注册表启动功能
- ⚙️ **自动监控**：启动后自动开始监控

### v2.2 (2025-11-06)
- 🐛 **Bug修复**：修复配置文件路径问题
- 📁 **路径处理**：支持打包后正确读取配置

### v2.1 (2025-11-06)
- 🔧 **打包优化**：修复 pkg_resources 打包错误

### v2.0 (2025-11-06)
- 🎉 **首次打包版本**
- ✅ 完整的 GUI 界面
- ✅ 系统托盘支持
- ✅ 主题切换功能

### v1.0 (2025-11-06)
- ✨ 初始版本发布
- ✅ 命令行版本实现
- ✅ 自动探测认证入口
- ✅ 多种密码加密支持
- ✅ 监控模式
- ✅ 配置持久化

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

本项目采用 MIT 许可证，您可以自由使用、修改和分发本软件。

## ⚠️ 免责声明

本工具仅供学习交流使用，请遵守学校网络使用规定。

- 使用本工具产生的任何后果由使用者自行承担
- 请确保使用符合当地法律法规
- 不得用于非法用途

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/campus-auto-login&type=Date)](https://star-history.com/#yourusername/campus-auto-login&Date)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/yourusername/campus-auto-login?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/campus-auto-login?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/campus-auto-login?style=social)

---

**Made with ❤️ for Campus Network Users**

**作者**: yushi-xh

*最后更新：2025-11-07*
