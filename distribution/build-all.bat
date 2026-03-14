@echo off
chcp 65001 >nul
REM ============================================================================
REM MyTools 快速打包启动器
REM ============================================================================

echo.
echo ============================================
echo   MyTools 分发打包工具
echo ============================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/
    pause
    exit /b 1
)

:: 运行打包脚本
echo 正在启动打包流程...
echo.
python "%~dp0quick_build.py" %*

if errorlevel 1 (
    echo.
    echo ============================================
    echo   打包失败，请检查错误信息
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   打包完成!
    echo ============================================
    echo.
    echo 输出目录：distribution\output\
    echo.
)

pause
