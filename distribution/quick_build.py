#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyTools 快速打包工具 - 一键生成所有分发格式
自动检测依赖并给出提示
"""

import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BUILD_SCRIPT = SCRIPT_DIR / "build_distribution.py"

def check_dependencies():
    """检查依赖软件"""
    print("=" * 70)
    print("检查依赖项...")
    print("=" * 70)
    
    deps = {
        ".NET SDK": check_dotnet(),
        "Python 3.8+": check_python(),
        "WiX Toolset (可选)": check_wix(),
        "7-Zip (可选)": check_7zip(),
    }
    
    print()
    all_ok = True
    for name, status in deps.items():
        icon = "✓" if status else "✗"
        optional = " (可选)" if "(可选)" in name else ""
        print(f"  {icon} {name.split(' (')[0]}{optional}")
        if not status and "(可选)" not in name:
            all_ok = False
    
    print()
    if not all_ok:
        print("⚠ 缺少必需依赖，请先安装后再运行")
        return False
    
    print("✓ 所有必需依赖已就绪")
    print()
    return True

def check_dotnet():
    """检查 .NET SDK"""
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"    版本：{result.stdout.strip()}")
            return True
    except:
        pass
    return False

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"    版本：{version.major}.{version.minor}.{version.micro}")
    return version.major >= 3 and version.minor >= 8

def check_wix():
    """检查 WiX Toolset"""
    wix_path = os.environ.get("WIX") or r"C:\Program Files (x86)\WiX Toolset v3.14"
    if os.path.exists(wix_path):
        candle = os.path.join(wix_path, "bin", "candle.exe")
        light = os.path.join(wix_path, "bin", "light.exe")
        if os.path.exists(candle) and os.path.exists(light):
            print(f"    路径：{wix_path}")
            return True
    print("    未找到 (将跳过 MSI 生成)")
    return False

def check_7zip():
    """检查 7-Zip"""
    paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            print(f"    路径：{path}")
            return True
    print("    未找到 (将跳过 SFX 生成)")
    return False

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  MyTools 快速打包工具")
    print("=" * 70 + "\n")
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 运行打包脚本
    print("启动打包流程...\n")
    try:
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)],
            cwd=str(SCRIPT_DIR)
        )
        return result.returncode
    except Exception as e:
        print(f"\n✗ 打包失败：{e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
