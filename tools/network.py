import urllib.request
import os

def download_document(url: str, save_path: str) -> str:
    """
    从指定URL下载文档到本地
    
    Args:
        url: 要下载的文档URL，必须以http://或https://开头
        save_path: 本地保存路径，包括文件名和扩展名
        
    Returns:
        str: 下载成功的文件保存路径
        如果有“\\”符号，必须使用转义符号！！！
        "C:\\Users\\2300\\Desktop\\new.png"是正确的
        
    Raises:
        ValueError: URL格式错误或保存路径无效
        Exception: 下载失败或文件保存失败
    """
    # 参数验证
    if not url.startswith(('http://', 'https://')):
        raise ValueError('URL必须以http://或https://开头')
    
    if not save_path or not save_path.strip():
        raise ValueError('保存路径不能为空')
    
    # 确保保存目录存在
    save_dir = os.path.dirname(save_path)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    try:
        # 下载文件
        urllib.request.urlretrieve(url, save_path)
        
        # 验证文件是否成功下载
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            return save_path
        else:
            raise Exception('文件下载后大小为0或文件不存在')
            
    except Exception as e:
        raise Exception(f'下载失败: {str(e)}')



def save_webpage_with_cookie(url: str, save_path: str, cookie: str) -> str:
    """
    使用指定的Cookie访问网页并保存网页源代码
    
    Args:
        url: 要访问的网页URL
        save_path: 本地保存路径，包括文件名（建议使用.html扩展名）
        cookie: Cookie字符串，格式如 "name=value; name2=value2"
        
    Returns:
        str: 保存成功的文件路径
        
    Raises:
        ValueError: 参数无效
        Exception: 访问失败或保存失败
    """
    # 参数验证
    if not url.startswith(('http://', 'https://')):
        raise ValueError('URL必须以http://或https://开头')
    
    if not save_path or not save_path.strip():
        raise ValueError('保存路径不能为空')
    
    if not cookie or not cookie.strip():
        raise ValueError('Cookie不能为空')
    
    # 确保保存目录存在
    save_dir = os.path.dirname(save_path)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    try:
        # 创建请求对象
        request = urllib.request.Request(url)
        
        # 添加Cookie到请求头
        request.add_header('Cookie', cookie)
        
        # 添加User-Agent，模拟浏览器访问
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # 发送请求并获取响应
        response = urllib.request.urlopen(request)
        
        # 读取网页源代码（二进制数据）
        webpage_content = response.read()
        
        # 将网页源代码保存到文件（二进制写入）
        with open(save_path, 'wb') as file:
            file.write(webpage_content)
        
        # 验证文件是否成功保存
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            return save_path
        else:
            raise Exception('文件保存后大小为0或文件不存在')
            
    except Exception as e:
        raise Exception(f'访问网页失败: {str(e)}')


import urllib.request
import urllib.parse
import socket
import re
from typing import Optional

def extract_links(html_content: str, base_url: str) -> list:
    """
    从HTML内容中提取所有外部链接
    
    Args:
        html_content: HTML内容字符串
        base_url: 基础URL，用于处理相对链接
        
    Returns:
        list: 提取到的所有外链列表
    """
    links = []
    
    # 使用正则表达式提取所有链接（a标签的href属性）
    link_patterns = [
        r'href=["\']([^"\']+)["\']',  # 匹配 href="..." 或 href='...'
        r'href=([^\s>]+)'  # 匹配 href=... (没有引号的情况)
    ]
    
    for pattern in link_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            # 清理链接（去除可能的空格和特殊字符）
            link = match.strip()
            
            # 跳过空链接、锚点链接和JavaScript链接
            if (not link or 
                link.startswith('#') or 
                link.lower().startswith('javascript:') or
                link.lower().startswith('mailto:')):
                continue
            
            # 处理相对链接（转换为绝对链接）
            if not link.startswith(('http://', 'https://', '//')):
                try:
                    # 使用urllib解析并拼接链接
                    link = urllib.parse.urljoin(base_url, link)
                except:
                    # 如果解析失败，跳过这个链接
                    continue
            
            # 去重并添加到列表
            if link not in links:
                links.append(link)
    
    # 返回排序后的链接列表
    return sorted(links)


def validate_url(url: str) -> bool:
    """
    验证URL格式是否正确
    
    Args:
        url: 要验证的URL
        
    Returns:
        bool: URL是否有效
    """
    if not url or not isinstance(url, str):
        return False
    
    # 检查是否以http或https开头
    if not url.startswith(('http://', 'https://')):
        return False
    
    # 尝试解析URL
    try:
        parsed = urllib.parse.urlparse(url)
        # 确保有网络位置（netloc）
        if not parsed.netloc:
            return False
        # 确保有scheme
        if not parsed.scheme:
            return False
        return True
    except:
        return False


def read_page(url: str, timeout: Optional[float] = None) -> str:
    """
    阅读指定URL的所有文本，返回该链接指向网页中的所有的文本、外链。
    添加了超时限制，避免长时间等待。
    
    Args:
        url: 要下载的文档URL，必须以http://或https://开头
        timeout: 超时时间（秒），None表示使用系统默认值
        
    Returns:
        str: 返回该链接指向网页中的所有的文本、外链
        
    Raises:
        ValueError: URL格式错误或无法访问
        TimeoutError: 请求超时
        Exception: 网页读取失败
    """
    # 使用更严格的URL验证
    if not validate_url(url):
        raise ValueError(f'URL格式无效: {url}')
    
    try:
        # 创建请求对象，添加User-Agent模拟浏览器
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        request.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        
        # 设置全局socket超时
        if timeout:
            socket.setdefaulttimeout(timeout)
        
        # 发送请求并获取响应
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except Exception as e:
            # 尝试更详细的错误信息
            raise ConnectionError(f'无法连接到 {url}: {str(e)}')
        
        # 检查响应状态码
        if response.getcode() != 200:
            raise ConnectionError(f'服务器返回状态码: {response.getcode()}')
        
        # 读取网页内容（尝试多种编码）
        html_bytes = response.read()
        
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        html_content = None
        
        for encoding in encodings:
            try:
                html_content = html_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if html_content is None:
            # 如果所有编码都失败，使用'latin-1'（不会失败，但可能乱码）
            html_content = html_bytes.decode('latin-1', errors='ignore')
        
        # 提取所有文本（去除HTML标签）
        # 首先去除script和style标签及其内容
        cleaned_html = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        cleaned_html = re.sub(r'<style.*?>.*?</style>', '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
        
        # 去除所有HTML标签
        text_only = re.sub(r'<[^>]+>', ' ', cleaned_html)
        
        # 去除多余的空白字符（多个空格、换行等）
        text_only = re.sub(r'\s+', ' ', text_only)
        text_only = text_only.strip()
        
        # 提取所有外链
        links = extract_links(html_content, url)
        
        # 格式化输出
        result = []
        result.append("=" * 50)
        result.append(f"网页内容 (URL: {url})")
        result.append(f"超时设置: {timeout if timeout else '默认'}秒")
        result.append("=" * 50)
        result.append("网页文本内容")
        result.append("-" * 30)
        result.append(text_only[:5000])  # 限制文本长度，避免太长
        
        if len(text_only) > 5000:
            result.append(f"\n...（文本过长，已截断，实际长度：{len(text_only)} 字符）")
        
        result.append("\n" + "-" * 30)
        result.append("外链列表")
        result.append("-" * 30)
        
        if links:
            for i, link in enumerate(links[:15], 1):  # 限制显示前15个链接
                result.append(f"{i}. {link}")
            if len(links) > 15:
                result.append(f"...（共{len(links)}个链接，显示前15个）")
        else:
            result.append("未找到外链")
        
        result.append("=" * 50)
        
        return "\n".join(result)
        
    except socket.timeout:
        raise TimeoutError(f'请求超时: 在{timeout}秒内未完成')
    except urllib.error.URLError as e: # pyright: ignore[reportAttributeAccessIssue]
        if isinstance(e.reason, socket.timeout):
            raise TimeoutError(f'请求超时: 在{timeout}秒内未完成')
        else:
            raise ConnectionError(f'无法访问URL: {str(e)}')
    except Exception as e:
        raise Exception(f'网页读取失败: {str(e)}')


def search_baidu(query: str, max_results: int = 5, timeout: float = 10.0) -> str:
    """
    使用百度搜索关键词，返回搜索结果的页面内容
    添加超时限制
    
    Args:
        query: 搜索关键词
        max_results: 每页显示的结果数量
        timeout: 超时时间（秒）
        
    Returns:
        str: 百度搜索结果的页面内容
        
    Raises:
        ValueError: 查询关键词为空或无效
        Exception: 搜索失败
    """
    # 参数验证
    if not query or not query.strip():
        raise ValueError('搜索关键词不能为空')
    
    if timeout <= 0:
        timeout = 10.0  # 默认10秒
    
    try:
        # 对查询词进行URL编码
        encoded_query = urllib.parse.quote(query)
        
        # 构建百度搜索URL
        search_url = f"https://www.baidu.com/s?ie=UTF-8&wd={encoded_query}&rn={max_results}"
        
        # 调用read_page函数，传入超时参数
        search_results = read_page(search_url, timeout)
        
        # 添加搜索信息到返回内容
        result_text = f"百度搜索关键词: {query}\n"
        result_text += f"搜索URL: {search_url}\n"
        result_text += f"超时设置: {timeout}秒\n"
        result_text += search_results
        
        return result_text
        
    except TimeoutError:
        raise TimeoutError(f'百度搜索超时: 在{timeout}秒内未完成')
    except Exception as e:
        raise Exception(f'百度搜索失败: {str(e)}')


def test_connection():
    """测试网络连接"""
    print("=== 测试网络连接 ===")
    
    test_urls = [
        ("百度", "https://www.baidu.com"),
        ("示例网站", "https://example.com"),
        ("Python官网", "https://www.python.org"),
    ]
    
    for name, url in test_urls:
        try:
            print(f"测试连接: {name} ({url})")
            result = read_page(url, timeout=5)
            print(f"  ✓ 连接成功")
            print(f"  文本预览: {result[:100]}...\n")
        except TimeoutError as e:
            print(f"  ✗ 连接超时: {e}\n")
        except ConnectionError as e:
            print(f"  ✗ 连接错误: {e}\n")
        except Exception as e:
            print(f"  ✗ 错误: {e}\n")


