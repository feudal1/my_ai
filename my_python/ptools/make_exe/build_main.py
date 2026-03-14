#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 main.py 打包成单文件可执行程序
输出位置：tools/bin/ptool.exe
"""
import os
import sys
import subprocess
from pathlib import Path

def build():
    # 项目根目录
    project_root = Path(__file__).parent.parent
    tools_dir = project_root
    bin_dir = tools_dir / "bin"
    main_script = tools_dir / "ptool.py"
    icon_file = Path(__file__).parent / "favicon.ico"
    
    # 确保 bin 目录存在
    bin_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("开始打包 ptool.py...")
    print("=" * 70)
    
    # PyInstaller 命令
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "main",
        "--icon", str(icon_file),
        "--distpath", str(bin_dir),
        "--workpath", str(tools_dir / "build"),
        "--specpath", str(tools_dir),
        "--clean",
        str(main_script)
    ]
    
    print(f"\n执行命令：{' '.join(cmd)}")
    print(f"\n源文件：{main_script}")
    print(f"图标文件：{icon_file}")
    print(f"输出目录：{bin_dir}")
    print("-" * 70)
    
    try:
        # 执行打包
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("\n打包成功!")
        print(f"可执行文件位置：{bin_dir / 'ptool.exe'}")
        
        # 清理临时文件
        build_dir = tools_dir / "build"
        if build_dir.exists():
            print("\n清理临时文件...")
            import shutil
            shutil.rmtree(build_dir)
        
        spec_file = tools_dir / "ptool.spec"
        if spec_file.exists():
            spec_file.unlink()
            
        print("=" * 70)
        
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败！错误信息:")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n打包失败！错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    build()