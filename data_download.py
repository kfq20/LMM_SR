from googleapiclient.discovery import build
import yt_dlp
import re

# 你需要替换为你的 API 密钥
api_key = "AIzaSyCjlgeHj1QMhjXTlO9c5ioizIP8XPtu3dE"
youtube = build("youtube", "v3", developerKey=api_key)


def download_video(video_url):
    ydl_opts = {
        'outtmpl': 'data/%(title)s.%(ext)s',  # 设置下载的视频文件名格式
    }
    
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

def search_videos(query):
    request = youtube.search().list(
        part="snippet",
        q=query,  # 搜索关键词
        type="video",  # 只返回视频类型
        maxResults=10  # 限制返回结果的数量
    )
    response = request.execute()
    video_items = []
    
    # 获取视频详细信息并筛选时长
    for item in response['items']:
        video_id = item['id']['videoId']
        video_details = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()

        # 获取视频时长
        duration = video_details['items'][0]['contentDetails']['duration']
        
        # 解析视频时长
        duration_seconds = parse_duration(duration)
        
        # 筛选时长小于30秒的视频
        if duration_seconds <= 240:
            video_items.append(item)
    
    return video_items

# # 获取某个视频的信息
# video_id = "dQw4w9WgXcQ"
# video_info = get_video_info(video_id)
# print(video_info)

query = "mother and daughter"
results = search_videos(query)

for item in results:
    title = item['snippet']['title']
    video_id = item['id']['videoId']
    description = item['snippet']['description']
    print(f"Title: {title}")
    print(f"Video Link: https://www.youtube.com/watch?v={video_id}")
    download_video(f"https://www.youtube.com/watch?v={video_id}")
    print(f"Description: {description}")
    print("="*50)
