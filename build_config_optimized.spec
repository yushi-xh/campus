# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 优化打包配置文件 v2.0
使用方法: pyinstaller build_config_optimized.spec
"""

import os

block_cipher = None

a = Analysis(
    ['campus_login_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 如果有配置文件或资源，取消注释
        # ('config/*', 'config'),
        # ('assets/*', 'assets'),
    ],
    hiddenimports=[
        # 修复 pkg_resources 错误
        'pkg_resources.py2_warn',
        'pkg_resources.markers',
        
        # HTTP 和网络相关
        'requests',
        'requests.adapters',
        'requests.exceptions',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',
        'urllib3.connection',
        'charset_normalizer',
        'idna',
        'certifi',
        
        # HTML 解析
        'bs4',
        'bs4.builder',
        'bs4.builder._lxml',
        'bs4.builder._html5lib',
        'lxml',
        'lxml.etree',
        
        # GUI 相关
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        '_tkinter',
        
        # 系统托盘
        'pystray',
        'pystray._win32',
        'pystray._util',
        
        # 图像处理
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        
        # 标准库（显式声明）
        'json',
        'threading',
        'logging',
        'datetime',
        'os',
        'sys',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'tornado',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='校园网登录工具_v2.7',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    # version_file='version_info.txt' if os.path.exists('version_info.txt') else None,
)

# 生成单文件
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='校园网登录工具',
# )
