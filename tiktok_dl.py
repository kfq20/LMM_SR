from TikTokApi import TikTokApi
import asyncio
import os
import requests
import urllib.request


ms_token = os.environ.get(
    "WaHv3dZZz0ldCTHbMR_vFjeJzcf1Oxj3GTxmPSCOlQ5xlaCtdfqtxU0oirtTAS02iHNn4a7Kww1Q", None
)  # set your own ms_token, needs to have done a search before for this to work


async def search_users():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, headless=False, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for user in api.search.users("david teather", count=10):
            print(user)

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
    asyncio.run(search_and_download("mother daughter", count=100))