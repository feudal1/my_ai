# MCP 服务说明（my_ai_tools）

本仓库通过 **Model Context Protocol (MCP)** 暴露现有 Python / C# 命令，供 Cursor、Claude Desktop 等客户端调用。

## 依赖

在 `my_python` 环境下安装：

```bash
pip install mcp
```

## 暴露的 MCP 工具

| 工具 | 说明 |
|------|------|
| `list_commands` | 列出所有已注册命令（含 Python 各组 + C# 导出） |
| `search_commands` | 按关键词模糊搜索命令 |
| `run_python_command` | 执行 Python 命令：`group`、`command`、`args_json`（CLI 参数 JSON 数组） |
| `run_csharp_command` | 执行 C# 命令：`command`、`args_json` |

## Cursor 配置

已在本项目 `.cursor/mcp.json` 中配置服务器 `my_ai_tools`，要求：

- **工作区根目录**为仓库根目录（即包含 `my_python`、`my_c#` 的目录）。
- 已安装 `mcp`：在对应 Python 环境中执行 `pip install mcp`。

保存配置后重启 Cursor，在 **设置 → Tools & MCP**（或 `Ctrl+Shift+J`）中可看到并启用该 MCP 服务器。

## 手动运行（stdio）

在仓库根目录下：

```bash
# 设置 PYTHONPATH 后运行
set PYTHONPATH=my_python
python -m tools.mcp_server
```

或在 `my_python` 目录下：

```bash
cd my_python
python -m tools.mcp_server
```

## 与现有 CLI 的对应关系

- Python 命令：对应 `p <group> <command> [args...]`，如 `p pdf merge --output out.pdf a.pdf b.pdf` → `run_python_command("pdf", "merge", "[\"--output\", \"out.pdf\", \"a.pdf\", \"b.pdf\"]")`。
- C# 命令：对应 `tools.exe <command> [args...]`，由 `run_csharp_command` 调用编译后的 `my_c#/tools/bin/.../tools.exe`。
