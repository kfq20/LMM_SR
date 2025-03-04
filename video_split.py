from google import genai
import os
import json
import re
import time

client = genai.Client(api_key="AIzaSyCjlgeHj1QMhjXTlO9c5ioizIP8XPtu3dE")

prompt = f"""
    Analyze the given video and extract structured information. The conversation mainly involves two speakers.
    
    Required Information:
    1. Speaker Details
       - Age (estimated)
       - Gender
       - Clothing description
       - Physical appearance
    
    2. Verbal Features
       - Full transcript in the format:
         Speaker 1: ...
         Speaker 2: ...
       - Tone and vocal characteristics
    
    3. Non-Verbal Features
       - Facial expressions
       - Body language
       - Physical proximity between speakers
    
    4. Environment Description
       - Scene description
       - Other people present
    
    Output the result in JSON format.
    """

# 处理视频文件的目录
VIDEO_FOLDER = "data/video"  # 这里填写你的视频文件夹路径
OUTPUT_JSON = "data/analysis_results.json"  # 输出的JSON文件

def extract_json(text):
    """提取 Markdown 代码块中的 JSON 内容"""
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else text  # 如果找不到，返回原文本

def process_video(video_path):
    max_retries = 5
    retry_delay = 2

    print(f"Uploading file {video_path}")
    for attempt in range(max_retries):
        try:
            video_file = client.files.upload(file=video_path)
            break
        except Exception as e:
            print(f"Error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    print(f"Completed upload: {video_file.uri}")
 
    print(f"Analyzing video {video_path}")
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    video_file,
                    prompt
                ]
            )
            clean_text = extract_json(response.text)
            return json.loads(clean_text)
        
        except Exception as e:  # 捕获所有错误
            print(f"Error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # 等待后重试
    
    print(f"Final attempt failed for {video_path}")
    return None

def main():
    results = []
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Existing JSON file is corrupted or empty. Starting fresh.")
                results = []
    
    processed_files = {entry["video_name"] for entry in results}  # 记录已处理文件，避免重复处理
    
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.endswith(".mp4") or filename.endswith(".avi") or filename.endswith(".mov"):
            if filename in processed_files:
                print(f"Skipping already processed file: {filename}")
                continue
            
            video_path = os.path.join(VIDEO_FOLDER, filename)
            print(f"Processing: {filename}")
            analysis_result = process_video(video_path)
            if analysis_result:
                results.append({"video_name": filename, "analysis": analysis_result})
                
                # 实时保存结果
                with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Analysis complete. Results saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()