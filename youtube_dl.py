from googleapiclient.discovery import build
import yt_dlp
import re
import os
import time

# 你需要替换为你的 API 密钥
api_key = "" 
youtube = build("youtube", "v3", developerKey=api_key)


def download_video(video_url, output_name=None):
    ydl_opts = {
        'outtmpl': output_name,  # 设置下载的视频文件名格式
    }
    
    max_retries = 3  # 最大重试次数
    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            break  # 成功后跳出重试循环
        except yt_dlp.utils.DownloadError as e:
            print(f"下载出错: {e} (尝试 {attempt + 1}/{max_retries})")
        
        if attempt < max_retries - 1:
            time.sleep(2)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def parse_duration(duration_str):
    """解析ISO 8601格式的时长，支持多种时间单位（小时、分钟、秒）"""
    total_seconds = 0
    match = re.match(r'PT((\d+H)?(\d+M)?(\d+S)?)', duration_str)
    if match:
        # 使用正则分组提取小时、分钟、秒数
        hour_part, minute_part, second_part = match.groups()[1:4]
        
        if hour_part:
            total_seconds += int(hour_part[:-1]) * 3600  # 计算小时转换为秒
        if minute_part:
            total_seconds += int(minute_part[:-1]) * 60  # 计算分钟转换为秒
        if second_part:
            total_seconds += int(second_part[:-1])  # 计算秒数

    return total_seconds
def get_video_info(video_id):
    request = youtube.videos().list(part="snippet,contentDetails,statistics", id=video_id)
    response = request.execute()
    return response

def search_videos(query, max_results=60):
    video_items = []  # 存储符合条件的视频
    next_page_token = None  # 初始化分页令牌
    
    while len(video_items) < max_results:
        request = youtube.search().list(
            part="snippet",
            q=query,  # 搜索关键词
            type="video",  # 只返回视频类型
            maxResults=min(50, max_results - len(video_items)),  # 避免超过 50
            pageToken=next_page_token  # 使用分页获取更多数据
        )
        response = request.execute()
        
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_details = youtube.videos().list(
                part="contentDetails",
                id=video_id
            ).execute()
            
            # 获取视频时长
            duration = video_details["items"][0]["contentDetails"]["duration"]
            duration_seconds = parse_duration(duration)  # 解析 ISO 8601 时长格式
            
            # 筛选时长小于 120 秒的视频
            if duration_seconds <= 120:
                video_items.append(item)
                
            # 如果达到 max_results，提前终止
            if len(video_items) >= max_results:
                return video_items
        
        # 获取下一页的 token，若无更多结果，则跳出循环
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return video_items

# # 获取某个视频的信息
# video_id = "dQw4w9WgXcQ"
# video_info = get_video_info(video_id)
# print(video_info)
relation = "grandparent-child"
query = "grandpa child daily life"
output_folder = f"/Volumes/XDISK/youtube/{relation}/{query}"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
results = search_videos(query)
i = 0
for item in results:
    output_name = f"{output_folder}/video_{i}"
    title = item['snippet']['title']
    video_id = item['id']['videoId']
    description = item['snippet']['description']
    print(f"Title: {title}")
    print(f"Video Link: https://www.youtube.com/watch?v={video_id}")
    download_video(f"https://www.youtube.com/watch?v={video_id}", output_name)
    print(f"Description: {description}")
    print("="*50)
    i += 1
