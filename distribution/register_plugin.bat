@echo off
chcp 65001 >nul
REM ============================================================================
REM 注册 SolidWorks 插件 (MSI 安装程序使用) - UTF-8 版本
REM ============================================================================

setlocal enabledelayedexpansion

:: 获取脚本所在目录
set SCRIPT_DIR=%~dp0

:: 尝试多个可能的位置查找 plugin.dll
if exist "%SCRIPT_DIR%plugin_files\plugin.dll" (
    set PLUGIN_DLL=%SCRIPT_DIR%plugin_files\plugin.dll
) else if exist "%SCRIPT_DIR%plugin.dll" (
    set PLUGIN_DLL=%SCRIPT_DIR%plugin.dll
) else (
    echo 错误：未找到 plugin.dll
    echo 请确保 plugin.dll 在以下位置之一:
    echo   - %SCRIPT_DIR%plugin_files\
    echo   - %SCRIPT_DIR%
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
