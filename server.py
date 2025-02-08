from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from src.application.TikTokDownloader import TikTokDownloader
from src.application.main_complete import TikTok
import uvicorn
from urllib.parse import quote

app = FastAPI()

class VideoRequest(BaseModel):
    url: str
    download: bool = False

class TikTokLinkService:
    def __init__(self):
        self.downloader = None
        self.example = None
        self.initialized = False
    
    async def _initialize(self):
        if not self.initialized:
            self.downloader = await TikTokDownloader().__aenter__()
            self.downloader.check_config()
            await self.downloader.check_settings(False)
            self.example = TikTok(self.downloader.parameter, self.downloader.database)
            self.initialized = True
    
    async def get_video_url(self, url: str, download: bool = False):
        await self._initialize()
        
        # 获取视频ID
        link_obj = self.example.links_tiktok
        ids = await link_obj.run(url)
        
        if not any(ids):
            raise HTTPException(status_code=400, detail="无法提取视频ID")
        
        # 获取记录器实例
        root, params, logger = self.example.record.run(self.example.parameter)
        async with logger(root, console=self.example.console, **params) as record:
            # 获取视频详情
            detail_data = await self.example._handle_detail(
                ids=ids,
                tiktok=True,
                api=True,
                record=record
            )
            
            if not detail_data or not detail_data[0].get("downloads"):
                raise HTTPException(status_code=404, detail="无法获取视频下载地址")
            
            video_info = {
                "video_url": detail_data[0]["downloads"],
                "title": detail_data[0].get("desc", ""),
                "author": detail_data[0].get("nickname", "")
            }
            
            if download:
                # 对文件名进行 URL 编码
                filename = quote(f"{video_info['author']}-{video_info['title']}.mp4")
                return RedirectResponse(
                    url=video_info["video_url"],
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            
            # 否则返回视频信息
            return video_info

service = TikTokLinkService()

@app.post("/api/video_url")
async def get_video_url(request: VideoRequest):
    return await service.get_video_url(request.url, request.download)

# 添加一个便于浏览器访问的 GET 接口
@app.get("/download")
async def download_video(url: str):
    return await service.get_video_url(url, download=True)

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "test:app",
        host="0.0.0.0",  # 允许外部访问
        port=8000,       # 端口号
    )