import re
from bs4 import BeautifulSoup
from html import unescape


def extract_summary(html_content, max_length=200):
    """
    从HTML内容中提取摘要
    
    Args:
        html_content (str): HTML内容
        max_length (int): 摘要最大长度
    
    Returns:
        str: 提取的摘要
    """
    if not html_content:
        return ""
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 获取纯文本内容
    text = soup.get_text(separator=' ', strip=True)
    
    # 将连续的空白字符替换为单个空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 截取最大长度
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text


def extract_images(html_content, max_count=5):
    """
    从HTML内容中提取图片URL
    
    Args:
        html_content (str): HTML内容
        max_count (int): 最大提取图片数量
    
    Returns:
        list: 图片URL列表
    """
    if not html_content:
        return []
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 获取所有图片标签
    img_tags = soup.find_all('img')
    
    # 提取图片URL
    img_urls = []
    for img in img_tags[:max_count]:
        src = img.get('src')
        if src:
            img_urls.append(src)
    
    return img_urls


def strip_html_tags(html_content):
    """
    去除HTML标签，保留纯文本
    
    Args:
        html_content (str): HTML内容
    
    Returns:
        str: 纯文本内容
    """
    if not html_content:
        return ""
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 获取纯文本
    text = soup.get_text(separator=' ', strip=True)
    
    # 将连续的空白字符替换为单个空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def count_words(text):
    """
    计算文本中的字数
    
    Args:
        text (str): 文本内容
    
    Returns:
        int: 字数
    """
    if not text:
        return 0
    
    # 去除HTML标签
    if '<' in text and '>' in text:
        text = strip_html_tags(text)
    
    # 将连续的空白字符替换为单个空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 简单地按空格分割计算
    words = text.split(' ')
    
    # 过滤空字符串
    words = [w for w in words if w]
    
    return len(words)


def remove_html_tags(html_content):
    """
    移除HTML标签，保留纯文本
    :param html_content: HTML内容
    :return: 纯文本内容
    """
    if not html_content:
        return ""
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 去除所有脚本和样式内容
    for script in soup(["script", "style"]):
        script.extract()
    
    # 获取文本内容
    text = soup.get_text()
    
    # 处理多余的空白字符
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text


def sanitize_html(html_content, allowed_tags=None):
    """
    净化HTML内容，仅保留允许的标签
    :param html_content: HTML内容
    :param allowed_tags: 允许的标签列表
    :return: 净化后的HTML
    """
    if not html_content:
        return ""
    
    if allowed_tags is None:
        allowed_tags = [
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'a', 'span', 'em', 'strong', 'b', 'i', 'u', 'del', 'code', 'pre',
            'ul', 'ol', 'li', 'blockquote', 'hr',
            'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br'
        ]
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 去除所有不允许的标签
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()  # 保留内容，去除标签
    
    return str(soup) 