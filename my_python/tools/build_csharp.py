#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门用于构建 C# tools.exe 的脚本
用法:
    p build-csharp              # 默认构建 (Release 配置)
    p build-csharp --debug      # Debug 配置
    p build-csharp --clean      # 先清理再构建
    p build-csharp --watch      # 监听模式，文件变化时自动重新构建
"""
import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
import time

import typer

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent.parent


def get_csharp_tools_dir(project_root: Path) -> Path:
    """获取 C# tools 项目目录"""
    return project_root / "my_c#" / "tools"


def find_dotnet() -> Optional[Path]:
    """查找 dotnet 命令"""
    try:
        result = subprocess.run(
            ["where", "dotnet"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            dotnet_path = result.stdout.strip().split('\n')[0].strip()
            return Path(dotnet_path)
    except Exception:
        pass
    
    common_paths = [
        Path(r"C:\Program Files\dotnet\dotnet.exe"),
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "dotnet" / "dotnet.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "dotnet" / "dotnet.exe",
    ]
    
    for path in common_paths:
        if path.exists():
            return path
    
    return None


def build_csharp(
    project_dir: Path,
    configuration: str = "Release",
    clean: bool = False,
    verbose: bool = False
) -> bool:
    """构建 C# 项目"""
    dotnet = find_dotnet()
    if not dotnet:
        print("❌ 错误：未找到 dotnet 命令")
        print("请确保已安装 .NET SDK: https://dotnet.microsoft.com/download")
        return False
    
    print(f"🔧 使用 dotnet: {dotnet}")
    print(f"📁 项目目录：{project_dir}")
    print(f"⚙️  配置：{configuration}")
    
    if clean:
        print("\n🧹 清理旧的构建...")
        clean_args = [
            str(dotnet),
            "clean",
            str(project_dir / "tools.csproj"),
            "-c", configuration,
            "--verbosity", "quiet"
        ]
        
        try:
            result = subprocess.run(
                clean_args,
                check=False,
                capture_output=not verbose,
                text=True,
                encoding='gbk',
                errors='replace'
            )
            
            if result.returncode != 0 and verbose:
                print(f"⚠️  清理警告：{result.stderr}")
        except Exception as e:
            print(f"⚠️  清理过程出错：{type(e).__name__}: {e}")
    
    print(f"\n🔨 开始构建...")
    build_args = [
        str(dotnet),
        "build",
        str(project_dir / "tools.csproj"),
        "-c", configuration,
        "--verbosity", "minimal" if not verbose else "detailed"
    ]
    
    build_args.extend(["--runtime", "win-x64"])
    
    try:
        result = subprocess.run(
            build_args,
            check=False,
            capture_output=not verbose,
            text=True,
            encoding='gbk',
            errors='replace',
            cwd=str(project_dir)
        )
        
        if verbose:
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print("\n✅ 构建成功!")
            
            output_dir = project_dir / "bin" / configuration / "net10.0-windows" / "win-x64"
            exe_path = output_dir / "tools.exe"
            
            if exe_path.exists():
                print(f"📦 输出文件：{exe_path}")
                print(f"📊 文件大小：{exe_path.stat().st_size:,} 字节")
            else:
                for runtime in ["net10.0-windows", "net10.0"]:
                    for arch in ["win-x64", ""]:
                        test_path = project_dir / "bin" / configuration / runtime / arch / "tools.exe"
                        if test_path.exists():
                            print(f"📦 输出文件：{test_path}")
                            print(f"📊 文件大小：{test_path.stat().st_size:,} 字节")
                            break
            
            return True
        else:
            print("\n❌ 构建失败!")
            if not verbose:
                print("\n错误信息:")
                print(result.stderr)
            return False
            
    except FileNotFoundError:
        print(f"❌ 错误：找不到 dotnet 命令")
        return False
    except Exception as e:
        print(f"❌ 构建过程出错：{type(e).__name__}: {e}")
        return False


def watch_mode(project_dir: Path, configuration: str = "Release"):
    """监听模式：检测文件变化时自动重新构建"""
    print("👀 进入监听模式...")
    print(f"📁 监控目录：{project_dir}")
    print("按 Ctrl+C 退出\n")
    
    def get_cs_files(proj_dir: Path) -> dict:
        cs_files = {}
        for cs_file in proj_dir.rglob("*.cs"):
            if "obj" not in str(cs_file) and "bin" not in str(cs_file):
                cs_files[cs_file] = cs_file.stat().st_mtime
        return cs_files
    
    last_modified = get_cs_files(project_dir)
    last_build_time = time.time()
    
    try:
        while True:
            time.sleep(2)
            
            current_files = get_cs_files(project_dir)
            
            changed = False
            for cs_file, mtime in current_files.items():
                if cs_file not in last_modified or mtime > last_modified.get(cs_file, 0):
                    changed = True
                    print(f"\n📝 检测到文件变化：{cs_file.relative_to(project_dir)}")
                    break
            
            if changed:
                time.sleep(1)
                
                if time.time() - last_build_time < 5:
                    continue
                
                print("\n🔄 开始自动构建...")
                success = build_csharp(project_dir, configuration, clean=False, verbose=False)
                
                if success:
                    print("✨ 自动构建完成\n")
                else:
                    print("⚠️  自动构建失败，请检查错误信息\n")
                
                last_modified = get_cs_files(project_dir)
                last_build_time = time.time()
                
    except KeyboardInterrupt:
        print("\n\n👋 退出监听模式")


# 创建命令组 app（用于在 main.py 中注册）
app = typer.Typer(
    help="C# tools.exe 构建工具",
    invoke_without_command=True,  # 允许不指定子命令
    no_args_is_help=False  # 没有参数时不显示帮助
)


@app.callback()  # 回调函数，在没有指定子命令时执行
def main_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="使用 Debug 配置 (默认 Release)"),
    clean: bool = typer.Option(False, "--clean", help="构建前先清理"),
    verbose: bool = typer.Option(False, "--verbose", help="显示详细输出"),
    watch: bool = typer.Option(False, "--watch", help="监听模式，文件变化时自动重新构建")
):
    """C# tools.exe 构建工具 - 直接执行构建"""
    if ctx.invoked_subcommand is None:
        # 没有指定子命令时，直接执行构建逻辑
        project_root = get_project_root()
        csharp_dir = get_csharp_tools_dir(project_root)
        
        if not csharp_dir.exists():
            print(f"❌ 错误：找不到 C# 项目目录：{csharp_dir}")
            raise typer.Exit(code=1)
        
        configuration = "Debug" if debug else "Release"
        
        if watch:
            watch_mode(csharp_dir, configuration)
        else:
            success = build_csharp(
                csharp_dir,
                configuration=configuration,
                clean=clean,
                verbose=verbose
            )
            
            if not success:
                raise typer.Exit(code=1)


@app.command("build")  # 使用 'build' 作为默认命令
def build_cmd(
    debug: bool = typer.Option(False, "--debug", help="使用 Debug 配置 (默认 Release)"),
    clean: bool = typer.Option(False, "--clean", help="构建前先清理"),
    verbose: bool = typer.Option(False, "--verbose", help="显示详细输出"),
    watch: bool = typer.Option(False, "--watch", help="监听模式，文件变化时自动重新构建")
):
    """构建 C# tools.exe
    
    示例:
        p build-csharp build                  默认构建 (Release 配置)
        p build-csharp build --debug          Debug 配置
        p build-csharp build --clean          先清理再构建
        p build-csharp build --verbose        显示详细构建信息
        p build-csharp build --watch          监听模式，自动重新构建
    """
    project_root = get_project_root()
    csharp_dir = get_csharp_tools_dir(project_root)
    
    if not csharp_dir.exists():
        print(f"❌ 错误：找不到 C# 项目目录：{csharp_dir}")
        raise typer.Exit(code=1)
    
    configuration = "Debug" if debug else "Release"
    
    if watch:
        watch_mode(csharp_dir, configuration)
    else:
        success = build_csharp(
            csharp_dir,
            configuration=configuration,
            clean=clean,
            verbose=verbose
        )
        
        if not success:
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app()