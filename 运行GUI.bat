@echo off
REM ====================================
REM 校园网自动登录工具 - 快速启动脚本
REM 版本: v2.6
REM ====================================

chcp 65001 >nul
echo.
echo ====================================
echo   校园网自动登录工具 v2.6
echo ====================================
echo.
echo 正在启动程序...
echo.

python campus_login_gui.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo   运行失败！
    echo ====================================
    echo.
    echo 请确保：
    echo 1. 已安装 Python 3.8 或更高版本
    echo 2. 已安装依赖: pip install -r requirements.txt
    echo.
    echo 如需帮助，请查看 README.md
    echo.
    pause
)

