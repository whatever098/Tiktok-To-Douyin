# TikTok 视频搬运助手

一个帮助你将 TikTok 视频自动搬运到抖音的工具。通过自动化操作实现视频的下载和发布,提高搬运效率。

它能够监听 Tiktok 上的某个账号的更新，当有更新时，自动下载最新的视频，并上传到抖音。

这个项目需要你具有 VPN 环境，请自行解决。

# 操作步骤

你需要安装 Python 3.12 版本，并安装相关的依赖，一些依赖我可能并没有写到 requirements.txt 中，出现模块未找到的情况，请手动安装。

1. 安装 Python 3.12 版本

这个请自行安装。

2. 安装相关依赖

依赖的安装可能需要你具有 VPN 环境，请自行解决。

```bash
pip install -r requirements.txt
```

3. 配置 uploader/config.py 文件

你需要将你的本地的浏览器路径配置到 config.py 文件中。也可以通过 playwright 下载浏览器，不过我发现下载的浏览器无法配置视频封面。

```python
chrome_driver_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

4. 运行 monitor.py 文件

```bash
python monitor.py
```

5. 之后你需要扫码登录抖音账号，你有十分钟的时间扫码登录，如果十分钟内没有登录成功，则程序会自动退出。

6. 就介绍到这里，目前要更改要监听的 Tiktok 账号，需要修改源码，因为这是我针对某个账号进行搬运的代码，暂时不会考虑修改，暂时不会考虑程序的扩展性。能运行就行，哈哈~
