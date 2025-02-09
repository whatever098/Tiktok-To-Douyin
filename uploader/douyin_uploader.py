from playwright.async_api import Playwright, async_playwright
import asyncio
import os
from uploader.config import upload_url, public_url, manage_url, chrome_driver_path
from logging import getLogger

logger = getLogger(__name__)

async def douyin_login(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(url="https://creator.douyin.com/", timeout=20000)
        
        img_element = page.locator('div.account-qrcode-QvXsyd div.qrcode-image-QrGzx7 img:first-child')
        await img_element.wait_for()
        logger.info("请扫码登录...")
        
        num = 1
        while True:
            await asyncio.sleep(3)
            logger.info(f"等待扫码... {page.url}")
            if 'creator.douyin.com/creator-micro/home' in page.url:
                logger.info("登录成功!")
                break
            if num > 600:  # 设置最大等待时间
                raise Exception("登录超时")
            num += 1
            
        await context.storage_state(path=account_file)
        logger.info("Cookie已保存")
        await context.close()
        await browser.close()

async def cookie_auth(account_file):
    """验证 cookie 是否有效"""
    if not os.path.exists(account_file):
        return False
        
    async with async_playwright() as playwright:
        logger.info("验证 cookie 是否有效")
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=account_file)
        page = await context.new_page()
        await page.goto(upload_url)
        try:
            await page.wait_for_selector("div.boards-more h3:text('抖音排行榜')", timeout=5000)
            logger.warn("cookie 已失效")
            return False
        except:
            logger.info("cookie 有效")
            return True

class DouYinVideo(object):
    def __init__(self, title, file_path, preview_path, tags, account_file, publish_date=0, location="重庆市"):
        self.title = title
        self.file_path = file_path
        self.preview_path = preview_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.location = location

    async def set_schedule_time(self, page, publish_date):
        """设置定时发布"""
        label_element = page.locator("label.radio-d4zkru:has-text('定时发布')")
        await label_element.click()
        await asyncio.sleep(1)
        
        publish_date_hour = publish_date.strftime("%Y-%m-%d %H:%M")
        await page.locator('.semi-input[placeholder="日期和时间"]').click()
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date_hour))
        await page.keyboard.press("Enter")
        await asyncio.sleep(1)

    async def handle_upload_error(self, page):
        """处理上传错误"""
        logger.warn("视频出错了，重新上传中")
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        """上传视频的主要逻辑"""
        browser = await playwright.chromium.launch(headless=False, executable_path=chrome_driver_path)
        context = await browser.new_context(storage_state=self.account_file)
        page = await context.new_page()

        await page.goto(upload_url)
        logger.info(f'正在上传-------{self.title}')
        logger.debug('正在打开主页...')
        await page.wait_for_url(upload_url)
        logger.debug('正在上传视频中...')
        await page.wait_for_timeout(2000)

        if await page.locator('div.progress-div > div:has-text("上传失败")').count():
            logger.warn("发现上传出错了...")
            await self.handle_upload_error(page)

        # 点击 "上传视频" 按钮
        upload_div_loc = page.locator("div.container-drag-info-Tl0RGH").first
        async with page.expect_file_chooser() as video_fc_info:
            await upload_div_loc.click()
        video_file_chooser = await video_fc_info.value
        if not os.path.exists(self.file_path):
            logger.error(f"上传的视频文件不存在，路径是{self.file_path}")
            # 关闭浏览器上下文和浏览器实例
            await context.close()
            await browser.close()
            await playwright.stop()
            return False
            
        await video_file_chooser.set_files(self.file_path)
        # 等待页面跳转到指定的 URL
        target_url = public_url
        while True:
            # 判断是是否进入视频发布页面，没进入，则自动等待到超时
            try:
                await page.wait_for_url(target_url)
                break
            except:
                logger.debug(f"当前页面 URL：{page.url}, 期待的 URL：{target_url}")
                await page.wait_for_timeout(100)

        await page.wait_for_timeout(2000)
        logger.info("正在填充标题和话题...")
        # 根据 placeholder 属性定位 input 元素
        title_container = page.get_by_placeholder('填写作品标题，为作品获得更多流量')
        if await title_container.count():
            await title_container.fill(self.title[:30])
            logger.debug("标题填充完毕")

        css_selector = ".zone-container"
        for tag in self.tags:
            await page.type(css_selector, "#" + tag)
            await page.press(css_selector, "Space")
        logger.debug("话题填充完毕")

        while True:
            # 判断重新上传按钮是否存在，如果不存在，代表视频正在上传，则等待
            try:
                #  新版：定位重新上传
                number = await page.locator("label").filter(has_text="重新上传").count()
                if number > 0:
                    logger.debug("视频上传完毕")
                    break
                else:
                    logger.info("正在上传视频中...")
                    await page.wait_for_timeout(2000)

                    if await page.locator('div.progress-div > div:has-text("上传失败")').count():
                        logger.warn("发现上传出错了...")
                        await self.handle_upload_error(page)
            except:
                logger.info("正在上传视频中...")
                await page.wait_for_timeout(1000)

        await page.wait_for_timeout(2000)
        cover_button = page.locator('div.title-wA45Xd:has-text("选择封面")')
        count = await cover_button.count()
        logger.debug(f"cover_button: {count}")
        if count == 1:
            await cover_button.click()
        elif count == 2:
            await cover_button.first.click()
        else:
            logger.error(f"无法选择封面, 封面数量: {count}")

        await page.wait_for_timeout(2000)
        recommend_button = page.locator('div.recommend-bubble-JPbArG')
        recommend_count = await recommend_button.count()
        logger.debug(f"recommend_button: {recommend_count}")
        if recommend_count:
            await recommend_button.first.click(force=True)
        else:
            logger.info("没有推荐封面")
        
        await page.wait_for_timeout(2000)
        
        compile_button = page.locator('button.primary-RstHX_')
        logger.debug(f"compile_button: {await compile_button.count()}")
        for i in range(count):
            await compile_button.click()
            await page.wait_for_timeout(2000)

        # 判断视频是否发布成功
        while True:
            # 判断视频是否发布成功
            try:
                publish_button = page.get_by_role('button', name="发布", exact=True)
                if await publish_button.count():
                    await publish_button.click()
                await page.wait_for_url(manage_url,
                                        timeout=5000)  # 如果自动跳转到作品页面，则代表发布成功
                logger.info("视频发布成功")
                break
            except:
                # 如果页面是管理页面代表发布成功
                current_url = page.url
                if manage_url in current_url:
                    logger.info("视频发布成功")
                    break
                else:        
                    logger.info("视频正在发布中...")
                    await page.wait_for_timeout(500)

        await context.storage_state(path=self.account_file)  # 保存cookie
        logger.info('cookie更新完毕！')
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()
        await playwright.stop()