from types import SimpleNamespace
from src.application.TikTokDownloader import TikTokDownloader
from src.application.main_complete import TikTok
from src.interface.template import API, APITikTok
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TikTokAPI:
    def __init__(self, downloader: TikTokDownloader):
        self.downloader = downloader

    def generate_params(self) -> dict:
        # 继承基类参数
        params = {
            "aid": "1988",
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": "Win32",
            "browser_version": "5.0",
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": "5",
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "os": "windows",
            "priority_region": "",
            "region": "US",
            "screen_height": "1080",
            "screen_width": "1920",
            "tz_name": "Asia/Shanghai",
        }
        return params

    async def get_user_posts(self, sec_uid: str):
        """获取用户发布的视频列表"""
        try:
            # 创建API实例
            api = APITikTok(
                self.downloader.parameter,
                proxy=self.downloader.parameter.proxy_tiktok
            )
        
            # 设置API地址和参数
            api.api = "https://www.tiktok.com/api/post/item_list/"
            params = api.generate_params()
            params.update({
                "secUid": sec_uid,
                "count": "35",
                "cursor": "0"
            })
            
            # 发起请求
            response = await api.request_data(
                url=api.api,
                params=params,
                method="GET"
            )
            
            return response
        except Exception as e:
            logger.error(f"请求失败: {e}")
            return None
            
            
# 使用示例
async def main():
    sec_uid = "MS4wLjABAAAAKUQx295x3iK3PH5rNfM7f5gzZHhty4GrbTVZsHCKG4FMIzrhDStqz4bUkiU-gxoA"
    response = await TikTokAPI(TikTokDownloader()).get_user_posts(sec_uid)
    if not response:
        logger.error("请求失败")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 