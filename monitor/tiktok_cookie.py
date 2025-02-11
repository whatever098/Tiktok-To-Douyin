from rookiepy import chrome
from typing import List, Dict

def get_chrome_cookies(domains: List[str]) -> Dict[str, str]:
    """
    从 Chrome 浏览器获取指定域名的 cookies
    
    Args:
        domains: 域名列表，例如 ['www.tiktok.com', '.tiktok.com']
        
    Returns:
        Dict[str, str]: cookie 字典，格式为 {cookie名: cookie值}
        
    Example:
        >>> cookies = get_chrome_cookies(['.tiktok.com', 'www.tiktok.com'])
        >>> print(cookies)
    """
    try:
        # 使用 rookiepy 获取 cookies
        cookies = chrome(domains=domains)
        # 转换为字典格式
        return {cookie["name"]: cookie["value"] for cookie in cookies}
    except Exception as e:
        print(f"获取 Chrome cookies 失败: {e}")
        return {}

if __name__ == "__main__":
    # 使用示例
    domains = ['.tiktok.com', 'www.tiktok.com']
    cookies = get_chrome_cookies(domains)
    print(cookies)