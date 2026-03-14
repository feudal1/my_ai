from datetime import datetime
import os
import json
from ptools import register_command
# 定义shot_memory.json文件路径
SHOT_MEMORY_FILE = os.path.join(os.path.dirname(__file__), "shot_memory.json")
memory_dir = os.path.join(os.getcwd(), "my_llm", "memory_data")
if not os.path.exists(memory_dir):
    os.makedirs(memory_dir)
def read_txt(file_path):
    """
    读取 memory_server\memory_data\current_program.txt 文件的内容
    
    Returns:
        str: 文件内容，如果文件不存在或读取失败则返回空字符串
    """
    current_program_path = os.path.join(memory_dir, f"{file_path}.txt")
    
    try:
        # 检查文件是否存在
        if not os.path.exists(current_program_path):
            print(f"文件不存在: {current_program_path}")
            return ""
        
        # 读取文件内容
        with open(current_program_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
            return content
            
    except Exception as e:
        print(f"读取 current_program.txt 失败: {e}")
        return ""
@register_command('llm', 'read-work')
def read_work_txt():
    """读取 memory_data\work_memory.txt 文件的内容"""
    current_program_path = os.path.join(memory_dir, f"work_memory.txt")
    
    try:
        # 检查文件是否存在
        if not os.path.exists(current_program_path):
            print(f"文件不存在: {current_program_path}")
            return ""
        
        # 读取文件内容
        with open(current_program_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            print(content)
            return content
            
    except Exception as e:
        print(f"读取 work_memory.txt 失败: {e}")
        return ""
def save_longterm_memory_log(content):
    """
    将内容保存到memory文件夹下的日志文件中
    
    Args:
        content (str): 要保存的内容
    """

    # 确保memory_data文件夹存在
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir)
    # 构建日志文件路径
    log_file_path = os.path.join(memory_dir, f"longterm_memory.txt")
    
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 写入日志文件
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {content}\n")
 
    except Exception as e:
        print(f"保存日志失败: {e}")

def get_sys_prompt_content():
    sys_prompt_content = f"""
        ***你可以通过输出 ```cmd 代码块来执行电脑命令，代码块内容会被系统解析并真实执行***
        ***示例：直接输出 ```cmd 换行 后面一行是真实要执行的命令，最后再用 ``` 结束代码块***
        ***禁止为了举例而输出可执行命令代码块；如需举例，请在命令前加 # 注释，或用自然语言描述而不要放进 ```cmd***
        ***只支持 Windows CMD 命令：请严格输出 CMD 可执行的命令***
        ***安全限制：禁止任何删除/破坏性操作（例如 del / erase / rmdir / rd / format / shutdown 等）***
        ***命令规则：一次只输出一条真实命令；命令要短、可复制、路径要加引号；先查看/列出再改动***
        ***回复风格：优先给结论与下一步，尽可能简短***
        """

    return sys_prompt_content

def save_messages_to_file(messages):
    """将消息历史保存到本地JSON文件"""
    try:
        with open(SHOT_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存消息历史失败: {e}")

def load_messages_from_file():
    """从本地 JSON 文件加载消息历史（不保存 system prompt）"""
    try:
        if os.path.exists(SHOT_MEMORY_FILE):
            with open(SHOT_MEMORY_FILE, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
                # 过滤掉 system 角色的消息
                filtered_messages = [msg for msg in messages if msg.get("role") != "system"]
                return filtered_messages
        else:
            # 如果文件不存在，初始化默认消息（不包含 system）
            messages = []
            save_messages_to_file(messages)
            return messages
    except Exception as e:
        print(f"加载消息历史失败：{e}")
        # 出错时返回空列表
        return []


