from TikTokApi import TikTokApi
import asyncio
import os
import requests
import time
import urllib.request


ms_token = os.environ.get(
    "WaHv3dZZz0ldCTHbMR_vFjeJzcf1Oxj3GTxmPSCOlQ5xlaCtdfqtxU0oirtTAS02iHNn4a7Kww1Q", None
)  # set your own ms_token, needs to have done a search before for this to work


async def search_users():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, headless=False, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for user in api.search.users("david teather", count=10):
            print(user)

async def get_hashtag_videos(hash_tag, num_data=30):
    save_dir = f"data/tiktok/{hash_tag}"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    cursor = 0
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=False)
        tag = api.hashtag(name=hash_tag)

        i = 0
        while cursor <= num_data:
            async for video in tag.videos(count=30, cursor=cursor):
                video_url = video.as_dict['video']['bitrateInfo'][0]['PlayAddr']['UrlList'][-1]
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Referer": "https://www.tiktok.com/",
                    "Origin": "https://www.tiktok.com",
                    "Accept": "*/*",
                }

                max_retries = 3  # 最大重试次数
                for attempt in range(max_retries):
                    try:
                        response = requests.get(video_url, headers=headers, stream=True)
                        if response.status_code == 200:
                            videoname = f"{save_dir}/video_{i}.mp4"
                            with open(videoname, "wb") as f:
                                for chunk in response.iter_content(1024):
                                    f.write(chunk)
                            print(f"下载完成: {videoname}")
                            break  # 成功后跳出重试循环
                        else:
                            print(f"下载失败: {response.status_code} (尝试 {attempt + 1}/{max_retries})")
                    except requests.RequestException as e:
                        print(f"请求出错: {e} (尝试 {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:  
                        time.sleep(2)  # 等待2秒后重试

                i += 1
            cursor += 30

async def search_and_download(keyword, count=5):
    save_dir = f"data/tiktok/{keyword}"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, headless=False, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        results = api.hashtag(name=keyword).videos(count)
        i = 0
        async for video in results:
            # if video.url is None:
            #     continue
            # video_info = await video.info()
            video_url = video.as_dict['video']['bitrateInfo'][0]['PlayAddr']['UrlList'][-1]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Referer": "https://www.tiktok.com/",
                "Origin": "https://www.tiktok.com",
                "Accept": "*/*",
            }
            response = requests.get(video_url, headers=headers, stream=True)
            videoname = f"{save_dir}/video_{i}.mp4"
            if response.status_code == 200:
                with open(videoname, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print("下载完成")
            else:
                print("下载失败:", response.status_code)
            i += 1

if __name__ == "__main__":
    # asyncio.run(search_and_download("mother daughter talk", count=35))
    asyncio.run(get_hashtag_videos("friend talk", num_data=60))