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


