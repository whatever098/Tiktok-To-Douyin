from src.application.TikTokDownloader import TikTokDownloader
from src.application.main_complete import TikTok
from asyncio import run
from logging import getLogger

logger = getLogger(__name__)

class TikTokVideoDownloader:
    def __init__(self, downloader: TikTokDownloader):
        """初始化TikTok下载器"""
        self.downloader = downloader
        # 初始化TikTok实例
        self.example = TikTok(self.downloader.parameter, self.downloader.database)

    async def _download(self, url: str):
        """下载指定TikTok视频"""
        
        # 获取记录器实例
        root, params, logger = self.example.record.run(self.example.parameter)
        async with logger(root, console=self.example.console, **params) as record:
            # 获取视频ID
            link_obj = self.example.links_tiktok
            ids = await link_obj.run(url)
            
            if not any(ids):
                logger.error(f"无法提取视频ID: {url}")
                return False
                
            # 处理下载
            _xx, file_name, file_path = await self.example._handle_detail(
                ids=ids,
                tiktok=True,
                record=record
            )
            return file_name, file_path
    
    async def download(self, url: str) -> tuple[str, str]:
        """同步方法下载视频"""
        return await self._download(url)
    
# 使用示例
if __name__ == "__main__":
    # 方式1: 直接使用
    downloader = TikTokVideoDownloader()
    video_url = "https://www.tiktok.com/@kasumi.yoda/video/7429084129561431314"
    file_name, file_path = downloader.download(video_url)
    print(f"下载成功: {file_name} {file_path}")
    
    # 方式2: 使用异步上下文管理器
    # async def download_videos():
    #     async with TikTokVideoDownloader() as downloader:
    #         await downloader._download(video_url)
    
    # run(download_videos()) 