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

def echo(text, filepath=None):
    """将文本内容输出或追加到文件
    
    参数：
    text: 需要输出的文本内容
    filepath: 可选的文件路径，如果提供则将文本追加到该文件末尾
    
    这里的text不支持 "\\n" 等转义字符，只会将输入完完全全地输入文件
    如
    EXECUTE: echo ￥| #include <stdio.h>\\n\\nint main() {\\n    printf("Hello, World!\\n");\\n    return 0;\\n} ￥| C:\\Users\\2300\Desktop\\maaaa.c
    只会在文件中得到
    #include <stdio.h>\\n\\nint main() {\\n    printf("Hello, World!\\n");\\n    return 0;\\n}
    是明显违背要求的
    
    使用样例：
    echo ￥| helloworld ￥| .\\a.txt
    
    会将"helloworld"追加到 .\\a.txt 文件末尾
    如果文件不存在会自动创建
    """
    if filepath:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
        return f"已将文本追加到 {filepath}"
    else:
        return text