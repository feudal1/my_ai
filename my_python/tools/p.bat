@echo off
REM 统一工具入口，用法：tools <命令> [参数...]  例如：tools merge_pdf   tools reset_memory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM 使用 my_python\venv 虚拟环境
set "PYTHON_EXE=%PROJECT_ROOT%\..\venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" "%PROJECT_ROOT%main.py" %*
) else (
    echo 警告：虚拟环境不存在，使用系统 Python
    python "%PROJECT_ROOT%main.py" %*
)