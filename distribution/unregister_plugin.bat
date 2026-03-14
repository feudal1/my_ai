@echo off
chcp 65001 >nul
REM ============================================================================
REM 注销 SolidWorks 插件 (MSI 卸载程序使用)
REM ============================================================================

setlocal enabledelayedexpansion

:: 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set PLUGIN_DLL=%SCRIPT_DIR%plugin.dll

if exist "%PLUGIN_DLL%" (
    %windir%\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "%PLUGIN_DLL%" /unregister >nul 2>&1
)

exit /b 0
