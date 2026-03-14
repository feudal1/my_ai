#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 服务端：将现有 cmd_wrappers（Python + C#）以 MCP Tools 形式暴露，
供 Cursor / Claude Desktop 等 MCP 客户端调用。

使用前安装: pip install mcp
运行（stdio，供 Cursor 配置）: python -m tools.mcp_server
或: uv run tools.mcp_server（在 my_python 目录下）
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# 确保能 import tools 包
MY_PYTHON = Path(__file__).resolve().parent.parent
if str(MY_PYTHON) not in sys.path:
    sys.path.insert(0, str(MY_PYTHON))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("请先安装 MCP SDK: pip install mcp", file=sys.stderr)
    sys.exit(1)

from tools import get_all_commands
# 触发 cmd_wrappers 注册（与 main.py 一致）
try:
    from tools.cmd_wrappers import blender_commands  # noqa: F401
    from tools.cmd_wrappers import cad_commands  # noqa: F401
    from tools.cmd_wrappers import llm_commands  # noqa: F401
    from tools.cmd_wrappers import memory_commands  # noqa: F401
    from tools.cmd_wrappers import pdf_commands  # noqa: F401
    from tools.cmd_wrappers import ue_commands  # noqa: F401
except Exception:
    pass
from tools.command_search import (
    search_registered_commands,
    _load_csharp_commands_via_export,
    _find_csharp_tools_exe,
)

mcp = FastMCP(
    "my_ai_tools",
)


def _all_commands_with_csharp(project_root: str | None = None) -> dict:
    """获取所有命令（含 C# 导出），与 command_search 逻辑一致。"""
    root = project_root or str(MY_PYTHON)
    all_commands = get_all_commands()
    csharp_export = _load_csharp_commands_via_export(root)
    if csharp_export:
        csharp_cmds = []
        for item in csharp_export:
            if not isinstance(item, dict):
                continue
            name = (item.get("name") or "").strip()
            desc = (item.get("description") or "").strip()
            params = (item.get("parameters") or "").strip()
            if not name:
                continue
            help_text = desc or ""
            if params:
                help_text = f"{help_text} 参数：{params}" if help_text else f"参数：{params}"
            csharp_cmds.append({"name": name, "help": help_text})
        if csharp_cmds:
            all_commands = dict(all_commands)
            all_commands["csharp"] = {"help": "C# tools 导出命令", "commands": csharp_cmds}
    return all_commands


@mcp.tool()
def list_commands() -> str:
    """列出所有已注册的命令（包含 Python 各组与 C# 工具）。返回格式：按组列出，每组下列出 命令名、描述、用法。"""
    all_commands = _all_commands_with_csharp()
    lines = []
    for group_name, group_data in sorted(all_commands.items()):
        lines.append(f"\n{group_name}: {group_data.get('help', '')}")
        for cmd in group_data.get("commands", []):
            name = cmd.get("name", "")
            help_text = cmd.get("help", "")
            prefix = "p " if group_name != "csharp" else "tools.exe "
            usage = f"{prefix}{group_name} {name}"
            lines.append(f"  - {name}: {help_text}")
            lines.append(f"    用法: {usage}")
    return "\n".join(lines) if lines else "暂无已注册命令"


@mcp.tool()
def search_commands(keyword: str, top_k: int = 10) -> str:
    """根据关键词在已注册命令中模糊搜索。返回匹配的命令及用法。"""
    results = search_registered_commands(
        keyword,
        threshold=0.3,
        top_k=top_k,
        include_csharp_export=True,
        project_root_for_csharp=str(MY_PYTHON),
    )
    if not results:
        return f"未找到与「{keyword}」相关的命令"
    lines = [f"关键词: {keyword}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. [{r['group']}] {r['name']} (相似度: {r['score']})")
        lines.append(f"   描述: {r['help']}")
        lines.append(f"   用法: {r['usage']}")
    return "\n".join(lines)


@mcp.tool()
def run_python_command(group: str, command: str, args_json: str = "[]") -> str:
    """执行 Python 侧已注册命令。group 为命令组（如 pdf, memory, cad），command 为子命令名，args_json 为 JSON 数组，元素为 CLI 参数（如 [\"--output\", \"out.pdf\", \"a.pdf\", \"b.pdf\"]）。"""
    try:
        args_list = json.loads(args_json)
        if not isinstance(args_list, list):
            args_list = [str(args_list)]
        else:
            args_list = [str(x) for x in args_list]
    except json.JSONDecodeError as e:
        return f"args_json 解析失败: {e}"

    cmd = [sys.executable, "-m", "tools.main", group, command] + args_list
    try:
        result = subprocess.run(
            cmd,
            cwd=str(MY_PYTHON),
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ},
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if result.returncode != 0:
            return f"退出码 {result.returncode}\nstdout: {out}\nstderr: {err}"
        return out or "(无输出)"
    except subprocess.TimeoutExpired:
        return "执行超时（300s）"
    except Exception as e:
        return f"执行异常: {type(e).__name__}: {e}"


@mcp.tool()
def run_csharp_command(command: str, args_json: str = "[]") -> str:
    """执行 C# 侧命令（如 SolidWorks 相关）。command 为命令名，args_json 为 JSON 数组，元素为 CLI 参数。"""
    exe_path = _find_csharp_tools_exe(str(MY_PYTHON))
    if exe_path is None:
        return "未找到 C# tools.exe，请先编译 my_c#/tools 项目"

    try:
        args_list = json.loads(args_json)
        if not isinstance(args_list, list):
            args_list = [str(args_list)]
        else:
            args_list = [str(x) for x in args_list]
    except json.JSONDecodeError as e:
        return f"args_json 解析失败: {e}"

    cmd = [str(exe_path), command] + args_list
    try:
        result = subprocess.run(
            cmd,
            cwd=str(exe_path.parent),
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='replace',
            timeout=300,
            env={**os.environ},
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if result.returncode != 0:
            return f"退出码 {result.returncode}\nstdout: {out}\nstderr: {err}"
        return out or "(无输出)"
    except subprocess.TimeoutExpired:
        return "执行超时（300s）"
    except Exception as e:
        return f"执行异常: {type(e).__name__}: {e}"


if __name__ == "__main__":
    # stdio 传输，便于 Cursor / Claude 等配置
    print("MCP Server 已启动")
    mcp.run(transport="stdio")
    
