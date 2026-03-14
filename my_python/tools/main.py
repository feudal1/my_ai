#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一工具入口：使用 Typer + 装饰器自动发现命令
用法: 
    p pdf merge --files file1.pdf file2.pdf
    p memory reset
    p cad obb
    p skill-search <关键词>
    p list-all
"""
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher
import json
import subprocess

# 添加项目根目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import typer
from tools import get_all_commands, set_main_app_instance, register_all_main_commands, COMMAND_REGISTRY
from tools.command_search import search_registered_commands

# 导入 cmd_wrappers 模块以注册所有命令包装器
try:
    from tools.cmd_wrappers import blender_commands
    from tools.cmd_wrappers import cad_commands
    from tools.cmd_wrappers import llm_commands
    from tools.cmd_wrappers import pdf_commands
    from tools.cmd_wrappers import ue_commands
    from tools import build_csharp
except (ImportError, ModuleNotFoundError) as e:
    print(f"警告：cmd_wrappers 模块导入失败：{e}")

# 创建主应用
app = typer.Typer(
    help="统一工具入口 - 包含 PDF、UE、CAD、Memory、Blender、SolidWorks 等多种工具",
    invoke_without_command=True,
    no_args_is_help=True
)

# 设置主应用实例引用，以便后续注册命令
set_main_app_instance(app)

# 将所有已注册的命令组添加到主应用
for group_name, group_data in COMMAND_REGISTRY.items():
    app.add_typer(group_data["app"], name=group_name, help=group_data["help"])

# 添加 build-csharp 命令到主应用（作为普通命令，不是命令组）
try:
    from tools import build_csharp
    # 直接从 build_csharp.app 中获取 build 命令并注册到主应用
    app.add_typer(build_csharp.app, name="build", help="C# tools.exe 构建工具")
except (ImportError, ModuleNotFoundError) as e:
    print(f"警告：build_csharp 模块导入失败：{e}")


def _find_csharp_tools_exe() -> Optional[Path]:
    """
    在仓库内定位 my_c#/tools 编译输出的 tools.exe。
    优先选择最近修改的一个（Debug/Release/不同 TFM 都兼容）。
    """
    repo_root = Path(PROJECT_ROOT).resolve().parent
    bin_dir = repo_root / "my_c#" / "tools" / "bin"
    if not bin_dir.exists():
        return None

    candidates = list(bin_dir.rglob("tools.exe"))
    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _load_csharp_commands_via_export() -> List[Dict[str, Any]]:
    """
    调用 C# 导出命令 JSON，并读取返回的命令列表。
    按 group 字段将命令分发到对应的命令组（cad/solidworks）。
    若未找到 tools.exe / 执行失败 / JSON 不存在，则返回空列表（不影响 Python 自己的搜索）。
    """
    exe_path = _find_csharp_tools_exe()
    if exe_path is None:
        print("提示：未找到 C# tools.exe（跳过加载 C# 命令）")
        return []

    try:
        result = subprocess.run(
            [str(exe_path), "--export-commands"],
            check=False,
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='replace',
        )
        if result.returncode != 0:
            err = (result.stderr or "").strip()
            out = (result.stdout or "").strip()
            detail = err or out or f"returncode={result.returncode}"
            print(f"提示：C# 命令导出失败（{detail}）")
            return []
    except Exception as e:
        print(f"提示：执行 C# tools.exe 失败（{type(e).__name__}: {e}）")
        return []

    json_path = exe_path.parent / "csharp_commands.json"
    if not json_path.exists():
        print(f"提示：未发现 C# 命令 JSON：{json_path}")
        return []

    try:
        # C# 默认 UTF8 可能带 BOM，用 utf-8-sig 更稳
        data = json.loads(json_path.read_text(encoding="utf-8-sig"))
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"提示：读取/解析 C# 命令 JSON 失败（{type(e).__name__}: {e}）")
        return []

    return []


# 加载 C# 导出命令并按组分发（cad/solidworks）
csharp_commands_data = _load_csharp_commands_via_export()
if csharp_commands_data:
    # 按 group 字段分组
    cad_cmds = []
    solidworks_cmds = []
    other_cmds = []
    
    for cmd in csharp_commands_data:
        group = cmd.get("group", "csharp")
        if group == "cad":
            cad_cmds.append(cmd)
        elif group == "solidworks":
            solidworks_cmds.append(cmd)
        else:
            other_cmds.append(cmd)
    
    # 辅助函数：创建 C# 命令的执行函数
    def create_csharp_command_executor(cmd_name: str, cmd_params: str, exe_path: Path):
        """创建一个执行 C# 命令的函数"""
        # 根据 parameters 信息决定是否创建带参数的函数
        if cmd_params and cmd_params != "无":
            # 有参数的命令
            def executor_with_params(args: str = typer.Argument("", help=f"命令参数：{cmd_params}")):
                try:
                    args_list = [args] if args else []
                    result = subprocess.run(
                        [str(exe_path), cmd_name] + args_list,
                        check=False,
                        capture_output=False,
                        text=True,
                        encoding='gbk',
                        errors='replace',
                    )
                    if result.returncode != 0:
                        print(f"C# 命令执行失败：{cmd_name}")
                except Exception as e:
                    print(f"执行 C# 命令出错 ({type(e).__name__}: {e})")
            executor_with_params.__name__ = f"csharp_{cmd_name}"
            return executor_with_params
        else:
            # 无参数的命令
            def executor_no_params():
                try:
                    result = subprocess.run(
                        [str(exe_path), cmd_name],
                        check=False,
                        capture_output=False,
                        text=True,
                        encoding='gbk',
                        errors='replace',
                    )
                    if result.returncode != 0:
                        print(f"C# 命令执行失败：{cmd_name}")
                except Exception as e:
                    print(f"执行 C# 命令出错 ({type(e).__name__}: {e})")
            executor_no_params.__name__ = f"csharp_{cmd_name}"
            return executor_no_params
    
    # 获取 tools.exe 路径用于执行
    csharp_exe_path = _find_csharp_tools_exe()
    
    # 如果有 CAD 命令，创建或更新 cad 命令组
    if cad_cmds:
        if "cad" not in COMMAND_REGISTRY:
            # 创建新的 cad 命令组
            from tools import command_group
            cad_app = typer.Typer(help="CAD 工具")
            COMMAND_REGISTRY["cad"] = {
                "help": "CAD 工具",
                "app": cad_app,
                "commands": []
            }
            app.add_typer(cad_app, name="cad", help="CAD 工具")
        
        # 从注册表中获取 cad_app
        cad_app = COMMAND_REGISTRY["cad"]["app"]
        
        # 添加命令信息到注册表（用于显示和搜索）
        for cmd in cad_cmds:
            cmd_name = cmd.get("name", "")
            # 避免重复添加同名命令
            existing_names = [c["name"] for c in COMMAND_REGISTRY["cad"]["commands"]]
            if cmd_name not in existing_names:
                COMMAND_REGISTRY["cad"]["commands"].append({
                    "name": cmd_name,
                    "help": cmd.get("description", "") + (f" 参数：{cmd.get('parameters', '')}" if cmd.get('parameters') else ""),
                    "csharp_export": True
                })
                
                # 动态注册到 Typer 应用，使用 name 参数指定命令名
                if csharp_exe_path:
                    executor_func = create_csharp_command_executor(cmd_name, cmd.get('parameters', ''), csharp_exe_path)
                    cad_app.command(name=cmd_name)(executor_func)
    
    # 如果有 SolidWorks 命令，创建 solidworks 命令组
    if solidworks_cmds:
        if "solidworks" not in COMMAND_REGISTRY:
            from tools import command_group
            sw_app = typer.Typer(help="SolidWorks 工具")
            COMMAND_REGISTRY["solidworks"] = {
                "help": "SolidWorks 工具",
                "app": sw_app,
                "commands": []
            }
            app.add_typer(sw_app, name="solidworks", help="SolidWorks 工具")
        
        # 从注册表中获取 sw_app
        sw_app = COMMAND_REGISTRY["solidworks"]["app"]
        
        # 添加命令信息到注册表
        for cmd in solidworks_cmds:
            cmd_name = cmd.get("name", "")
            # 避免重复添加同名命令
            existing_names = [c["name"] for c in COMMAND_REGISTRY["solidworks"]["commands"]]
            if cmd_name not in existing_names:
                COMMAND_REGISTRY["solidworks"]["commands"].append({
                    "name": cmd_name,
                    "help": cmd.get("description", "") + (f" 参数：{cmd.get('parameters', '')}" if cmd.get('parameters') else ""),
                    "csharp_export": True
                })
                
                # 动态注册到 Typer 应用
                if csharp_exe_path:
                    executor_func = create_csharp_command_executor(cmd_name, cmd.get('parameters', ''), csharp_exe_path)
                    sw_app.command(name=cmd_name)(executor_func)
        
        # 添加 sw 作为 solidworks 的别名
        if "sw" not in COMMAND_REGISTRY:
            COMMAND_REGISTRY["sw"] = {
                "help": "SolidWorks 工具（solidworks 的别名）",
                "app": sw_app,
                "commands": COMMAND_REGISTRY["solidworks"]["commands"]
            }
            app.add_typer(sw_app, name="sw", help="SolidWorks 工具（solidworks 的别名）")


@app.command("search")
@app.command("s", hidden=True)
def skill_search_cmd(
    keyword: str = typer.Argument(..., help="搜索关键词"),
    threshold: float = typer.Option(0.5, "--threshold", "-t", help="相似度阈值")
):
    """从已注册的命令中模糊搜索"""
    print(f"\n搜索关键词：{keyword}\n")

    results = search_registered_commands(
        keyword,
        threshold=threshold,
        include_csharp_export=True,
        project_root_for_csharp=PROJECT_ROOT,
    )
    
    if results:
        print(f"找到 {len(results)} 个匹配结果:\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r['group']}] 相似度：{r['score']}")
            print(f"   命令：{r['name']}")
            print(f"   描述：{r['help']}")
            print(f"   用法：{r['usage']}")
            print('-' * 60)
    else:
        print("未找到相关命令")
    
    print("\n提示：使用 'p <命令组> --help' 查看该组所有可用命令；若修改了 C# 命令描述，需重新编译 my_c#/tools 后搜索结果才会更新")


@app.command("list")
def list_all_cmd():
    """列出所有已注册的命令"""
    # 从全局注册表获取所有命令
    all_commands = get_all_commands()
    
    # 统计命令总数
    total_commands = 0
    for group_name, group_data in all_commands.items():
        commands = group_data.get("commands", [])
        total_commands += len(commands)
    
    print("=" * 70)
    print("已注册的命令列表")
    print("=" * 70)
    
    for group_name, group_data in sorted(all_commands.items()):
        print(f"\n{group_name}: {group_data.get('help', '')}")
        commands = group_data.get("commands", [])
        if commands:
            for cmd in commands:
                print(f"  - {cmd.get('name', '')}: {cmd.get('help', '')}")
        else:
            print("  (暂无详细命令信息)")
        print(f"  用法：p {group_name} --help")
    
    print("\n" + "=" * 70)
    print(f"共 {len(all_commands)} 个命令组，{total_commands} 个具体命令")
    print("使用 'p <命令组> --help' 查看详细帮助")
    print("使用 'p skill-search <关键词>' 搜索命令")
    print("=" * 70)


# 注册所有直接添加到主应用的命令
register_all_main_commands()

print("\n命令系统初始化完成")
print(f"已加载 {len(get_all_commands())} 个命令组\n")


if __name__ == "__main__":
  app()
