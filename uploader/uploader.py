from playwright.async_api import Playwright, async_playwright
import asyncio
import os
from uploader.douyin_uploader import DouYinVideo, cookie_auth, douyin_login
from uploader.config import douyin_cookies_path
from logging import getLogger

logger = getLogger(__name__)

async def upload_douyin(video_path: str, tags: list, account_file: str = douyin_cookies_path, title: str = "", preview_path: str = ""):
    if not os.path.exists(douyin_cookies_path) or not await cookie_auth(douyin_cookies_path):
        logger.info("需要登录抖音...")
        await douyin_login(douyin_cookies_path)
        logger.info("登录抖音成功")

    app = DouYinVideo(
        title=title,
        file_path=video_path,
        preview_path=preview_path,
        tags=tags,
        publish_date=0,  # 0表示立即发布
        account_file=account_file
    )
    
    async with async_playwright() as playwright:
        await app.upload(playwright)
        
    logger.info("上传抖音成功")

async def main():
    title = "测试视频"
    video_path = "video/2.mp4"  # 替换为实际视频路径
    preview_path = "image/1.png"  # 替换为实际封面图路径
    tags = ["测试", "视频"]
    
    # 检查cookie是否存在且有效
    if not os.path.exists(douyin_cookies_path) or not await cookie_auth(douyin_cookies_path):
        print("需要登录...")
        await douyin_login(douyin_cookies_path)
    
    app = DouYinVideo(
        title=title,
        file_path=video_path,
        preview_path=preview_path,
        tags=tags,
        publish_date=0,  # 0表示立即发布
        account_file=douyin_cookies_path
    )
    
    async with async_playwright() as playwright:
        await app.upload(playwright)

if __name__ == "__main__":
    asyncio.run(main())