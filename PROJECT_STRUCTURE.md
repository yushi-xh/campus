# 项目结构文档

## 📁 目录结构

```
校园网自动登录工具/
├── .github/                          # GitHub 配置
│   ├── ISSUE_TEMPLATE/              # Issue 模板
│   │   ├── bug_report.md           # Bug 报告模板
│   │   └── feature_request.md      # 功能请求模板
│   └── pull_request_template.md    # PR 模板
│
├── dist/                             # 打包输出目录（.gitignore）
│   ├── 校园网登录工具_v2.7.exe     # 打包后的可执行文件
│   └── 使用说明.txt                 # 用户使用说明
│
├── .editorconfig                     # 编辑器配置
├── .gitignore                        # Git 忽略配置
├── auto_campus_login.py              # 核心登录逻辑（命令行版本）
├── campus_login_gui.py               # GUI 程序主文件
├── build_config_optimized.spec       # PyInstaller 优化打包配置
├── CHANGELOG.md                      # 更新日志
├── CONTRIBUTING.md                   # 贡献指南
├── icon.ico                          # 程序图标
├── LICENSE                           # MIT 许可证
├── login_config.json                 # 配置文件（.gitignore，运行时生成）
├── login_config.json.example         # 配置文件示例
├── PROJECT_STRUCTURE.md              # 项目结构文档（本文件）
├── README.md                         # 项目说明文档
├── requirements.txt                  # Python 依赖清单
└── 运行GUI.bat                       # Windows 快速启动脚本
```

## 📄 文件说明

### 核心代码文件

#### `auto_campus_login.py`
- **功能**: 核心登录逻辑，命令行版本
- **主要功能**:
  - 网络连接检测
  - 自动探测校园网认证入口
  - 支持多种密码加密方式（MD5, Base64, 明文）
  - 智能表单字段识别
  - 监控模式
- **使用**: 可独立运行或被 GUI 调用

#### `campus_login_gui.py`
- **功能**: GUI 图形界面主程序
- **主要组件**:
  - `ModernCheckbox`: 自定义复选框组件
  - `ModernButton`: 自定义按钮组件
  - `ThemeManager`: 主题管理器
  - `CampusLoginGUI`: 主应用类
- **特性**:
  - 深色/浅色主题切换
  - 系统托盘支持
  - Windows 开机自启
  - 智能注册表清理

### 配置文件

#### `build_config_optimized.spec`
- **功能**: PyInstaller 打包配置
- **特点**:
  - 单文件打包
  - UPX 压缩
  - 隐藏导入优化
  - 资源文件包含

#### `requirements.txt`
- **功能**: Python 依赖清单
- **依赖**:
  - requests: HTTP 请求
  - beautifulsoup4: HTML 解析
  - pystray: 系统托盘
  - pillow: 图像处理
  - pyinstaller: 打包工具

#### `login_config.json`
- **功能**: 用户配置文件（自动生成）
- **内容**:
  - username: 用户名
  - password: 密码（明文，注意安全）
  - remember: 是否记住密码
  - auto_reconnect: 开机自启
  - retry: 重试次数
  - theme: 主题（dark/light）
- **安全**: 已加入 .gitignore，不会提交到仓库

### 文档文件

#### `README.md`
- **功能**: 项目主文档
- **内容**:
  - 功能介绍
  - 快速开始
  - 使用指南
  - 常见问题
  - 系统要求

#### `CHANGELOG.md`
- **功能**: 版本更新日志
- **格式**: 遵循 Keep a Changelog 标准
- **内容**: 记录每个版本的更改

#### `CONTRIBUTING.md`
- **功能**: 贡献指南
- **内容**:
  - 如何贡献
  - 代码规范
  - 提交流程
  - 开发指南

#### `LICENSE`
- **功能**: 开源许可证
- **类型**: MIT License
- **权限**: 允许商业使用、修改、分发

### 辅助文件

#### `.gitignore`
- **功能**: Git 忽略配置
- **忽略内容**:
  - 配置文件（包含敏感信息）
  - Python 缓存
  - 打包输出
  - IDE 配置
  - 临时文件

#### `.editorconfig`
- **功能**: 编辑器配置
- **规范**:
  - 字符编码: UTF-8
  - 换行符: CRLF (Windows)
  - Python 缩进: 4 空格
  - 最大行长: 100

#### `运行GUI.bat`
- **功能**: Windows 快速启动脚本
- **特点**:
  - 自动检测 Python
  - 错误提示
  - UTF-8 编码支持

## 🔄 工作流程

### 开发流程

```
1. 修改代码 → 2. 本地测试 → 3. 提交代码 → 4. 创建 PR → 5. 代码审查 → 6. 合并
```

### 打包流程

```
1. 更新版本号 → 2. 更新 CHANGELOG → 3. 运行打包命令 → 4. 测试 exe → 5. 创建 Release
```

### 发布流程

```
1. 打包 → 2. 测试 → 3. 更新文档 → 4. 创建 Tag → 5. GitHub Release → 6. 上传文件
```

## 📦 打包说明

### 打包命令

```bash
# 清理旧文件并打包
pyinstaller build_config_optimized.spec --clean
```

### 输出位置

- **可执行文件**: `dist/校园网登录工具_v2.7.exe`
- **大小**: 约 22 MB
- **包含**: 所有依赖和资源

### 分发内容

发布时应包含：
1. `校园网登录工具_v2.7.exe` - 主程序
2. `使用说明.txt` - 用户手册
3. `login_config.json.example` - 配置示例（可选）

**不应包含**:
- `login_config.json` - 包含敏感信息
- `build/` - 临时文件
- 源代码（除非单独发布）

## 🔐 安全注意事项

### 敏感文件

以下文件包含敏感信息，不应提交到仓库：
- `login_config.json` - 用户账号密码
- 任何包含真实凭证的配置文件

### .gitignore 保护

已配置忽略：
```gitignore
login_config.json
*.log
.env
```

### 发布前检查

1. ✅ 确认 login_config.json 未被提交
2. ✅ 检查代码中无硬编码密码
3. ✅ 验证 .gitignore 配置
4. ✅ 审查所有文档中的示例数据

## 🧪 测试指南

### 手动测试

1. **基本登录测试**
   - 输入正确账号密码
   - 点击"立即登录"
   - 验证登录成功

2. **监控功能测试**
   - 开启监控
   - 断开网络
   - 等待 5 秒
   - 验证自动重连

3. **开机自启测试**
   - 勾选开机自启
   - 保存配置
   - 重启电脑
   - 验证程序自动启动并隐藏

4. **注册表清理测试**
   - 取消勾选开机自启
   - 关闭程序
   - 检查注册表是否清理

### 回归测试

每次发布前应测试：
- ✅ 所有核心功能
- ✅ 主题切换
- ✅ 托盘菜单
- ✅ 配置保存和加载
- ✅ 开机自启
- ✅ 不同 Windows 版本兼容性

## 📊 代码统计

- **总行数**: ~1500 行
- **Python 文件**: 2 个
- **配置文件**: 6 个
- **文档文件**: 5 个
- **模板文件**: 3 个

## 🔗 相关链接

- GitHub 仓库: https://github.com/yourusername/campus-auto-login
- 问题追踪: https://github.com/yourusername/campus-auto-login/issues
- 发布页面: https://github.com/yourusername/campus-auto-login/releases

---

**最后更新**: 2025-11-07
**维护者**: yushi-xh
