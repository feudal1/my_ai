@echo off
chcp 65001 >nul
REM ============================================================================
REM 注销 SolidWorks 插件 (MSI 卸载程序使用) - UTF-8 版本
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
    echo 警告：未找到 plugin.dll，跳过注销
    exit /b 0
)

:: 执行注销
%windir%\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "%PLUGIN_DLL%" /unregister >nul 2>&1

exit /b 0
