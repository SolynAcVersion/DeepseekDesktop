import platform
import os
import sys
import json

def get_system_info() -> dict:
    """
    获取当前系统的基本信息
    
    Returns:
        dict: 包含系统信息的字典，包括：
            - os_name: 操作系统名称
            - os_version: 操作系统版本
            - os_release: 操作系统发行版
            - architecture: 系统架构
            - machine: 机器类型
            - processor: 处理器信息
            - python_version: Python版本
            - python_compiler: Python编译器信息
            - python_implementation: Python实现（CPython、PyPy等）
            - cwd: 当前工作目录
            - user: 当前用户名
            - cpu_count: CPU核心数
            - memory_info: 内存信息（仅Linux/Mac）
            
    Note:
        这个函数仅使用Python标准库，不依赖第三方包
    """
    system_info = {}
    
    try:
        # 操作系统信息
        system_info['os_name'] = platform.system()  # Windows, Linux, Darwin (Mac)
        system_info['os_version'] = platform.version()
        system_info['os_release'] = platform.release()
        
        # 系统架构信息
        system_info['architecture'] = platform.architecture()[0]  # 32bit, 64bit
        system_info['machine'] = platform.machine()  # x86_64, AMD64等
        system_info['processor'] = platform.processor() or "Unknown"
        
        # Python信息
        system_info['python_version'] = sys.version
        system_info['python_compiler'] = platform.python_compiler()
        system_info['python_implementation'] = platform.python_implementation()
        
        # 运行时信息
        system_info['cwd'] = os.getcwd()
        system_info['user'] = os.getenv('USERNAME') or os.getenv('USER') or "Unknown"
        system_info['cpu_count'] = os.cpu_count() or 0
        
        # 平台特定信息
        if platform.system() == "Windows":
            system_info['platform_info'] = platform.platform()
        elif platform.system() == "Linux":
            # 尝试获取Linux发行版信息
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            system_info['linux_distro'] = line.split('=')[1].strip().strip('"')
                            break
            except:
                system_info['linux_distro'] = "Unknown"
            
            # 尝试获取内存信息（仅Linux）
            try:
                with open('/proc/meminfo', 'r') as f:
                    mem_lines = f.readlines()[:3]
                    system_info['memory_info'] = [line.strip() for line in mem_lines]
            except:
                system_info['memory_info'] = "Not available"
        elif platform.system() == "Darwin":  # Mac OS
            system_info['mac_version'] = platform.mac_ver()[0]
    
    except Exception as e:
        # 如果获取信息过程中出错，记录错误但继续返回已获取的信息
        system_info['error'] = f"部分信息获取失败: {str(e)}"
    
    return system_info


def format_system_info(system_info: dict, format_type: str = 'text') -> str:
    """
    格式化系统信息输出
    
    Args:
        system_info: get_system_info()返回的系统信息字典
        format_type: 输出格式，可选 'text'、'json' 或 'html'
        
    Returns:
        str: 格式化后的系统信息字符串
        
    Raises:
        ValueError: 格式类型不支持
    """
    if format_type == 'text':
        lines = []
        lines.append("=" * 50)
        lines.append("系统信息报告")
        lines.append("=" * 50)
        
        for key, value in system_info.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        
        lines.append("=" * 50)
        return "\n".join(lines)
    
    elif format_type == 'json':
        return json.dumps(system_info, indent=2, ensure_ascii=False)
    
    elif format_type == 'html':
        html = "<html><head><title>系统信息</title></head><body>"
        html += "<h1>系统信息报告</h1>"
        html += "<table border='1' cellpadding='5'>"
        
        for key, value in system_info.items():
            if isinstance(value, list):
                html += f"<tr><td><b>{key}</b></td><td>"
                for item in value:
                    html += f"{item}<br>"
                html += "</td></tr>"
            else:
                html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
        
        html += "</table></body></html>"
        return html
    
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")
