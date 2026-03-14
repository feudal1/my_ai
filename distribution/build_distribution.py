#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyTools 分发打包工具
生成三种格式：
1. MSI 安装程序（WiX Toolset）
2. 自解压 EXE（7-Zip SFX）
3. 便携 ZIP 包
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "distribution"
BUILD_DIR = DIST_DIR / "build"
OUTPUT_DIR = DIST_DIR / "output"

# 源目录
PLUGIN_BIN = PROJECT_ROOT / "my_c#" / "plugin" / "bin" / "Debug" / "net48"
CTOOLS_BIN = PROJECT_ROOT / "my_c#" / "ctools" / "bin" / "Debug" / "net10.0-windows"
PYTHON_TOOLS = PROJECT_ROOT / "my_python" / "ptools" / "bin"

VERSION = "1.0.0"
PRODUCT_NAME = "MyTools"

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(text):
    print(f"\n[✓] {text}")

def clean_build():
    """清理构建目录"""
    print_header("步骤 1/6: 清理构建目录")
    
    if BUILD_DIR.exists():
        try:
            shutil.rmtree(BUILD_DIR)
            print(f"已删除：{BUILD_DIR}")
        except Exception as e:
            print(f"警告：无法删除 build 目录：{e}")
    
    # 只清理 output 目录内容，不删除目录本身
    if OUTPUT_DIR.exists():
        for item in OUTPUT_DIR.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except Exception as e:
                print(f"警告：无法删除 {item.name}: {e}")
        print(f"已清理：{OUTPUT_DIR}")
    
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    print("已创建构建目录")

def build_projects():
    """编译 C# 项目"""
    print_header("步骤 2/6: 编译 C# 项目")
    
    # 编译 plugin
    print("编译 plugin.dll...")
    plugin_project = PROJECT_ROOT / "my_c#" / "plugin" / "plugin.csproj"
    result = subprocess.run(
        ["dotnet", "build", str(plugin_project), "--configuration", "Release", "/verbosity:quiet"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        print(f"编译失败：{result.stderr}")
        return False
    print("  ✓ plugin.dll 编译完成")
    
    # 编译 ctools
    print("编译 ctool.exe...")
    ctools_project = PROJECT_ROOT / "my_c#" / "ctools" / "ctool.csproj"
    result = subprocess.run(
        ["dotnet", "build", str(ctools_project), "--configuration", "Release", "/verbosity:quiet"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        print(f"编译失败：{result.stderr}")
        return False
    print("  ✓ ctool.exe 编译完成")
    
    return True

def copy_files():
    """复制文件到构建目录"""
    print_header("步骤 3/6: 复制文件到构建目录")
    
    # 复制 plugin 文件
    print("复制 Plugin 文件...")
    plugin_dest = BUILD_DIR / "plugin_files"
    plugin_dest.mkdir(exist_ok=True)
    
    for file in PLUGIN_BIN.glob("*"):
        if file.is_file():
            shutil.copy2(file, plugin_dest)
    print(f"  ✓ 已复制 {len(list(PLUGIN_BIN.glob('*')))} 个文件")
    
    # 复制 ctools 文件
    print("复制 CTools 文件...")
    ctools_dest = BUILD_DIR / "ctools_files"
    ctools_dest.mkdir(exist_ok=True)
    
    for file in CTOOLS_BIN.glob("*"):
        if file.is_file():
            shutil.copy2(file, ctools_dest)
    print(f"  ✓ 已复制 {len(list(CTOOLS_BIN.glob('*')))} 个文件")
    
    # 复制 Python tools 文件
    print("复制 Python Tools 文件...")
    python_dest = BUILD_DIR / "python_tools"
    python_dest.mkdir(exist_ok=True)
    
    if PYTHON_TOOLS.exists():
        for item in PYTHON_TOOLS.iterdir():
            dest = python_dest / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        print(f"  ✓ 已复制 Python 工具")
    else:
        print("  ⚠ Python tools 目录不存在，跳过")
    
    # 复制脚本文件
    print("复制脚本文件...")
    scripts = ["register_plugin.bat", "unregister_plugin.bat", "tools.bat"]
    for script in scripts:
        src = DIST_DIR / script
        if src.exists():
            shutil.copy2(src, BUILD_DIR)
            print(f"  ✓ {script}")
    
    return True

def create_msi():
    """创建 MSI 安装程序"""
    print_header("步骤 4/6: 创建 MSI 安装程序")
    
    # 检查 WiX Toolset
    try:
        wix_path = os.environ.get("WIX") or r"C:\Program Files (x86)\WiX Toolset v3.14"
        if not os.path.exists(wix_path):
            print("⚠ 未找到 WiX Toolset，跳过 MSI 生成")
            print("  下载地址：https://wixtoolset.org/")
            return False
        
        candle_exe = os.path.join(wix_path, "bin", "candle.exe")
        light_exe = os.path.join(wix_path, "bin", "light.exe")
        
        if not os.path.exists(candle_exe):
            print("⚠ 未找到 candle.exe，跳过 MSI 生成")
            return False
        
        # 编译 WiX 源文件
        wxs_file = DIST_DIR / "installer.wxs"
        obj_file = BUILD_DIR / "installer.wixobj"
        msi_file = OUTPUT_DIR / f"{PRODUCT_NAME}_{VERSION}.msi"
        
        print(f"编译 {wxs_file.name}...")
        result = subprocess.run([
            candle_exe,
            "-dPluginDir=" + str(BUILD_DIR / "plugin_files"),
            "-dCToolsDir=" + str(BUILD_DIR / "ctools_files"),
            "-dPythonToolsDir=" + str(BUILD_DIR / "python_tools"),
            "-out", str(obj_file),
            str(wxs_file)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"编译失败：{result.stderr}")
            return False
        
        print("生成 MSI 文件...")
        result = subprocess.run([
            light_exe,
            "-out", str(msi_file),
            str(obj_file)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"生成失败：{result.stderr}")
            return False
        
        print(f"✓ MSI 已生成：{msi_file}")
        return True
        
    except Exception as e:
        print(f"✗ MSI 创建失败：{e}")
        return False

def create_sfx():
    """创建自解压 EXE"""
    print_header("步骤 5/6: 创建自解压 EXE")
    
    try:
        # 检查 7-Zip
        seven_zip = r"C:\Program Files\7-Zip\7z.exe"
        if not os.path.exists(seven_zip):
            seven_zip = r"C:\Program Files (x86)\7-Zip\7z.exe"
        
        if not os.path.exists(seven_zip):
            print("⚠ 未找到 7-Zip，跳过 SFX 生成")
            print("  下载地址：https://www.7-zip.org/")
            return False
        
        # 创建临时压缩包
        temp_7z = BUILD_DIR / "temp.7z"
        sfx_config = BUILD_DIR / "sfx_config.txt"
        sfx_exe = OUTPUT_DIR / f"{PRODUCT_NAME}_{VERSION}_setup.exe"
        
        # 压缩所有文件
        print("创建 7z 压缩包...")
        files_to_compress = list(BUILD_DIR.glob("*"))
        files_to_compress = [f for f in files_to_compress if f.name not in ["temp.7z", "sfx_config.txt"]]
        
        if not files_to_compress:
            print("  ⚠ 没有文件可压缩")
            return False
        
        cmd = [seven_zip, "a", str(temp_7z), "-y"]
        for f in files_to_compress:
            if f.is_dir():
                cmd.append(str(f) + "\\*")
            else:
                cmd.append(str(f))
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"压缩失败：{result.stderr}")
            return False
        
        # 创建 SFX 配置
        sfx_text = """
;@Lang@0
;!@Install@!UTF-8!
Title="MyTools 安装程序"
BeginPrompt="确定要安装 MyTools 吗？"
RunFile="install.bat"
DefaultDirectory="%LOCALAPPDATA%\\MyTools"
ExtractPathText="选择安装位置："
!@InstallEnd@!
""".strip()
        
        with open(sfx_config, "w", encoding="utf-8") as f:
            f.write(sfx_text)
        
        # 合并文件
        print("生成自解压 EXE...")
        sfx_module = r"C:\Program Files\7-Zip\7zSD.sfx"
        if not os.path.exists(sfx_module):
            sfx_module = r"C:\Program Files (x86)\7-Zip\7zSD.sfx"
        
        if not os.path.exists(sfx_module):
            print("⚠ 未找到 7zSD.sfx，跳过 SFX 生成")
            return False
        
        with open(sfx_exe, "wb") as outfile:
            with open(sfx_module, "rb") as sfx_file:
                outfile.write(sfx_file.read())
            with open(sfx_config, "rb") as config_file:
                outfile.write(config_file.read())
            with open(temp_7z, "rb") as archive_file:
                outfile.write(archive_file.read())
        
        print(f"✓ SFX EXE 已生成：{sfx_exe}")
        return True
        
    except Exception as e:
        print(f"✗ SFX 创建失败：{e}")
        return False

def create_portable_zip():
    """创建便携版 ZIP"""
    print_header("步骤 6/6: 创建便携版 ZIP")
    
    try:
        zip_file = OUTPUT_DIR / f"{PRODUCT_NAME}_{VERSION}_portable.zip"
        
        print("创建 ZIP 压缩包...")
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in ["plugin_files", "ctools_files", "python_tools"]:
                folder_path = BUILD_DIR / folder
                if folder_path.exists():
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(BUILD_DIR)
                            zipf.write(file_path, arcname)
            
            # 添加脚本
            for script in ["register_plugin.bat", "unregister_plugin.bat", "tools.bat", "install.bat"]:
                script_path = BUILD_DIR / script
                if script_path.exists():
                    zipf.write(script_path, script)
        
        print(f"✓ 便携版 ZIP 已生成：{zip_file}")
        return True
        
    except Exception as e:
        print(f"✗ ZIP 创建失败：{e}")
        return False

def create_install_bat():
    """创建安装脚本"""
    install_script = r'''@echo off
chcp 65001 >nul
echo ============================================
echo MyTools 安装程序
echo ============================================
echo.

setlocal enabledelayedexpansion

:: 获取当前目录
set SCRIPT_DIR=%~dp0
set INSTALL_DIR=%LOCALAPPDATA%\MyTools

echo 正在安装到：%INSTALL_DIR%
echo.

:: 创建安装目录
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: 复制文件
echo 复制文件...
xcopy "%SCRIPT_DIR%*.*" "%INSTALL_DIR%" /E /Y /Q

:: 注册插件（需要管理员权限）
echo.
echo 注册 SolidWorks 插件...
call "%INSTALL_DIR%\register_plugin.bat"
if errorlevel 1 (
    echo 注意：插件注册失败，可能需要以管理员身份运行此脚本
)

:: 添加到 PATH - 使用 PowerShell
echo.
echo 添加到系统 PATH...
powershell -Command "$installPath = '%INSTALL_DIR%'; $userPath = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($userPath -notlike \"*$installPath*\") { $newPath = \"$userPath;$installPath\"; [Environment]::SetEnvironmentVariable('Path', $newPath, 'User'); Write-Host \"已添加到用户 PATH: $installPath\" } else { Write-Host \"已在 PATH 中\" }"

echo.
echo ============================================
echo 安装完成！
echo ============================================
echo.
echo 请关闭所有窗口，重新打开 CMD，然后运行:
echo   tools help
echo.
echo 注意：如需注册 SolidWorks 插件，请以管理员身份重新运行此脚本
echo.
pause
'''.lstrip()
    
    with open(BUILD_DIR / "install.bat", "w", encoding="gbk") as f:
        f.write(install_script)
    print("✓ 创建 install.bat")

def main():
    """主函数"""
    print_header(f"MyTools 分发打包工具 v{VERSION}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目根目录：{PROJECT_ROOT}")
    
    # 执行打包流程
    clean_build()
    
    if not build_projects():
        print("\n✗ 编译失败，中止打包")
        return 1
    
    if not copy_files():
        print("\n✗ 文件复制失败，中止打包")
        return 1
    
    create_install_bat()
    
    msi_created = create_msi()
    sfx_created = create_sfx()
    zip_created = create_portable_zip()
    
    # 输出结果
    print_header("打包完成")
    print(f"输出目录：{OUTPUT_DIR}\n")
    
    if msi_created:
        print(f"  ✓ MSI 安装程序：{PRODUCT_NAME}_{VERSION}.msi")
    
    if sfx_created:
        print(f"  ✓ 自解压 EXE: {PRODUCT_NAME}_{VERSION}_setup.exe")
    
    if zip_created:
        print(f"  ✓ 便携 ZIP: {PRODUCT_NAME}_{VERSION}_portable.zip")
    
    print("\n" + "=" * 70)
    print("分发建议:")
    print("  - MSI: 企业部署、批量安装")
    print("  - SFX: 个人用户、简单安装")
    print("  - ZIP: 便携使用、无需安装")
    print("=" * 70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
