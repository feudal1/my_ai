@echo off
chcp 65001 >nul
REM ============================================================================
REM 注册 SolidWorks 插件 (MSI 安装程序使用)
REM ============================================================================

setlocal enabledelayedexpansion

:: 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set PLUGIN_DLL=%SCRIPT_DIR%plugin.dll

if not exist "%PLUGIN_DLL%" (
    echo 错误：未找到 plugin.dll
    exit /b 1
)

:: 使用 regasm 注册
%windir%\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "%PLUGIN_DLL%" /codebase >nul 2>&1

if %errorLevel% equ 0 (
    echo 插件注册成功
    exit /b 0
) else (
    echo 插件注册失败
    exit /b 1
)
