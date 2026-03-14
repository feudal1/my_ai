@echo off
chcp 65001 >nul
REM ============================================================================
REM MyTools 统一启动脚本 - UTF-8 版本
REM ============================================================================

setlocal enabledelayedexpansion

set "TOOLS_DIR=%~dp0"
set "PTOOL=%TOOLS_DIR%ptool.exe"
set "CTOOL=%TOOLS_DIR%ctool.exe"

if "%1"=="" goto show_help
if "%1"=="/?" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="help" goto show_help

REM Python 工具
if "%1"=="p" (
    shift
    if exist "%PTOOL%" (
        "%PTOOL%" %*
    ) else (
        echo 错误：未找到 ptool.exe
    )
    goto :eof
)

REM C# 工具
if "%1"=="c" (
    shift
    if exist "%CTOOL%" (
        "%CTOOL%" %*
    ) else (
        echo 错误：未找到 ctool.exe
    )
    goto :eof
)

REM 直接调用（尝试自动识别）
if exist "%PTOOL%" (
    "%PTOOL%" %*
    goto :eof
)

if exist "%CTOOL%" (
    "%CTOOL%" %*
    goto :eof
)

:show_help
echo ============================================
echo MyTools - 统一工具集
echo ============================================
echo.
echo 用法：tools ^<命令^> [参数...]
echo.
echo 可用命令:
echo   p ^<command^>     - 调用 Python 工具 (ptool)
echo   c ^<command^>     - 调用 C# 工具 (ctool)
echo   help              - 显示此帮助信息
echo.
echo 示例:
echo   tools p pdf merge --files a.pdf b.pdf
echo   tools c export-dwg
echo.
echo 或直接使用:
echo   ptool ^<command^>
echo   ctool ^<command^>
echo ============================================
