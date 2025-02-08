import asyncio
from datetime import datetime
from typing import Callable, Any
import logging
from monitor.data import TikTokData
import traceback
from downloadVideo import TikTokVideoDownloader
from monitor.fetch import TikTokAPI
from src.application.TikTokDownloader import TikTokDownloader
from src.tools import Browser
from logging import getLogger
from uploader.uploader import upload_douyin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log', encoding='utf-8'),  # 指定 utf-8 编码
        logging.StreamHandler()
    ]
)

logger = getLogger(__name__)

class TikTokMonitor:
    def __init__(self, username: str, sec_uid: str, interval: int = 600):  # 默认600秒 = 10分钟
        """初始化监控器
        Args:
            interval: 检查间隔，单位为秒
        """
        self.interval = interval
        self.is_running = False
        self.username = username
        self.sec_uid = sec_uid

        self.data_manager = TikTokData()
        logger.info("TiktokData 初始化完成")

        self.downloader = TikTokDownloader()
        logger.info("TikTokDownloader 初始化完成")

        self.tiktok_api = None
        self.video_downloader = None

    async def __aenter__(self):
        """进入异步上下文时初始化"""
        await self.downloader.__aenter__()

        # 更新免责声明状态
        await self.downloader.database.update_config_data("Disclaimer", 1)
        
        # 初始化基本配置
        self.downloader.check_config()
        await self.downloader.check_settings(False)
        
        if Browser(self.downloader.parameter, self.downloader.cookie).run(
                True,
                select="2",
        ):
            await self.downloader.check_settings()
        
        # 初始化 API 和下载器
        self.tiktok_api = TikTokAPI(self.downloader)
        logger.info("TikTokAPI 初始化完成")

        self.video_downloader = TikTokVideoDownloader(self.downloader)
        logger.info("TikTokVideoDownloader 初始化完成")

        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出异步上下文时清理"""
        if self.downloader:
            await self.downloader.__aexit__(exc_type, exc_val, exc_tb)

    async def monitor_task(self, task_func: Callable[..., Any], *args, **kwargs) -> None:
        """执行定时监控任务
        Args:
            task_func: 要执行的任务函数
            args: 传递给任务函数的位置参数
            kwargs: 传递给任务函数的关键字参数
        """
        self.is_running = True
        while self.is_running:
            try:
                logger.info("开始执行监控任务")
                await task_func(*args, **kwargs)
                logger.info(f"任务执行完成，等待 {self.interval} 秒后重新执行")
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(traceback.format_exc())
                # 发生错误后等待一段时间再重试
                await asyncio.sleep(60)
    
    def up_updated(self, res):
        """
        判断是否更新
        param:
            res: 响应结果
        return:
            Dict: 更新视频信息
        """
        itemList = res['itemList']

        for item in itemList:
            # 跳过置顶视频
            if item.get('isPinnedItem', False):
                continue
            
            createTime = item['createTime']
            id = item['id']
            desc = item['desc']

            author = item['author']
            sec_uid = author['secUid']
            nickname = author['nickname']
            unique_id = author['uniqueId']

            # 判断是否更新
            if not self.data_manager.is_post_updated(sec_uid, createTime):
                return None

            # 有更新则保存最新的信息
            self.data_manager.save_user_info(nickname, sec_uid, unique_id)
            self.data_manager.save_latest_post(sec_uid, {
                'create_time': createTime,
                'id': id,
                'desc': desc
            })

            return {
                'unique_id': unique_id,
                'nickname': nickname,
                'sec_uid': sec_uid,
                'create_time': createTime,
                'id': id,
                'desc': desc
            }

        return None

    # 使用示例
    async def fetch_tiktok(self):
        """获取用户视频"""
        response = await self.tiktok_api.get_user_posts(self.sec_uid)

        if not response:
            logger.error(f"{self.username} 请求失败")
            return
        
        res = self.up_updated(response)
        if not res:
            logger.info(f"{self.username} 没有更新")
            return
        
        logger.info(f"{self.username} 更新了新的视频: {res['id']}")
        
        file_name, file_path = await self.video_downloader.download(f"https://www.tiktok.com/@{self.username}/video/{res['id']}")

        if not file_name:
            logger.error(f"{self.username} 的视频 {res['id']} 下载失败")
            return
        
        logger.info(f"{self.username} 的视频 {res['id']} 下载成功")

        logger.info(f"开始上传抖音: file_name={file_name}, file_path={file_path}")

        await upload_douyin(video_path=f"{file_path}.mp4", tags=["日向优奈", "fyp", "推荐"])
            
        logger.info("Tiktok [依田华澄]最新视频，搬运抖音号[日向优奈]成功！")

async def main():
    username = "kasumi.yoda"
    sec_uid = "MS4wLjABAAAAKUQx295x3iK3PH5rNfM7f5gzZHhty4GrbTVZsHCKG4FMIzrhDStqz4bUkiU-gxoA"
    interval = 600
    
    async with TikTokMonitor(username, sec_uid, interval) as monitor:
        try:
            await monitor.monitor_task(monitor.fetch_tiktok)
        except KeyboardInterrupt:
            monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())
