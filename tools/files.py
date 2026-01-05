"""
MCP 文件操作模块
提供基本的文件操作功能
"""

import os
import shutil

def mv(source, destination):
    """移动文件或目录
    你应该先看看你要移动到的destination目录是否存在，如果没有，应该先自己创建一个。否则会移动失败
    """
    if not os.path.exists(source):
        return f"源文件/目录不存在: {source}"
    
    shutil.move(source, destination)
    return f"已将 {source} 移动到 {destination}"

def cp(source, destination):
    """复制文件或目录"""
    if not os.path.exists(source):
        return f"源文件/目录不存在: {source}"
    
    if os.path.isdir(source):
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)
    
    return f"已将 {source} 复制到 {destination}"

def ls(directory="."):
    """列出目录内容"""
    if not os.path.exists(directory):
        return f"目录不存在: {directory}"
    
    items = os.listdir(directory)
    return f"{directory} 中的内容: {', '.join(items)}"

def mkdir(directory):
    """创建目录"""
    if os.path.exists(directory):
        return f"目录已存在: {directory}"
    
    os.makedirs(directory)
    return f"已创建目录: {directory}"

def rm(path):
    """删除文件或目录"""
    if not os.path.exists(path):
        return f"文件/目录不存在: {path}"
    
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
    
    return f"已删除: {path}"

def cat(filepath):
    """读取文件内容"""
    if not os.path.exists(filepath):
        return f"文件不存在: {filepath}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return f"文件 {filepath} 的内容:\n{content[:500]}..." if len(content) > 500 else content

def echo(text, mode ,filepath=None):
    """将文本内容输出或追加到文件或覆盖文件
    
    参数：
    text: 需要输出的文本内容
    mode：是追加还是覆盖源文本中的文本，追加为 `1` ，覆盖为 `2`
    filepath: 可选的文件路径，如果提供则将文本追加到该文件末尾
    
    这里的text不支持 "\\n" 等转义字符，只会将输入完完全全地输入文件
    如
    EXECUTE: echo ￥| #include <stdio.h>\\n\\nint main() {\\n    printf("Hello, World!\\n");\\n    return 0;\\n} ￥| 1 ￥| C:\\Users\\2300\Desktop\\maaaa.c
    只会在文件中得到
    #include <stdio.h>\\n\\nint main() {\\n    printf("Hello, World!\\n");\\n    return 0;\\n}
    是明显违背要求的
    
    使用样例：
    echo ￥| helloworld ￥| 1 ￥| .\\a.txt
    
    会将"helloworld"追加到 .\\a.txt 文件末尾
    如果文件不存在会自动创建
    """
    if filepath:
        if mode == 1:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
            return f"已将文本追加到 {filepath}"
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text + '\n')
    else:
        return text
    
    
def find_lines_in_file(file_path: str, search_string: str, case_sensitive: bool = True) -> list:
    """
    从文件中查找包含指定字符串的行
    
    Args:
        file_path: 要搜索的文件路径
        search_string: 要查找的字符串
        case_sensitive: 是否区分大小写，默认为True（区分大小写）
        
    Returns:
        list: 包含匹配行的列表，每行包括行号和内容
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件路径无效或搜索字符串为空
        Exception: 文件读取错误
    """
    # 参数验证
    if not file_path or not file_path.strip():
        raise ValueError('文件路径不能为空')
    
    if not search_string or not search_string.strip():
        raise ValueError('搜索字符串不能为空')
    
    # 检查文件是否存在
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'文件不存在: {file_path}')
    
    # 检查是否为文件
    if not os.path.isfile(file_path):
        raise ValueError(f'路径不是文件: {file_path}')
    
    matched_lines = []
    
    try:
        # 打开文件并逐行读取
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                # 根据case_sensitive参数决定搜索方式
                if case_sensitive:
                    if search_string in line:
                        matched_lines.append({
                            'line_number': line_number,
                            'content': line.rstrip('\n'),  # 移除行尾换行符
                            'original_content': line  # 保留原始内容
                        })
                else:
                    if search_string.lower() in line.lower():
                        matched_lines.append({
                            'line_number': line_number,
                            'content': line.rstrip('\n'),
                            'original_content': line
                        })
        
        return matched_lines
    
    except UnicodeDecodeError:
        # 如果UTF-8编码失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as file:
                for line_number, line in enumerate(file, start=1):
                    if case_sensitive:
                        if search_string in line:
                            matched_lines.append({
                                'line_number': line_number,
                                'content': line.rstrip('\n'),
                                'original_content': line
                            })
                    else:
                        if search_string.lower() in line.lower():
                            matched_lines.append({
                                'line_number': line_number,
                                'content': line.rstrip('\n'),
                                'original_content': line
                            })
            return matched_lines
        except Exception as e:
            raise Exception(f'文件读取失败（尝试GBK编码）: {str(e)}')
    
    except Exception as e:
        raise Exception(f'文件读取失败: {str(e)}')
