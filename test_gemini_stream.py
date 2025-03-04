from google import genai
from google.genai import types
import os
import json
import time
import re

client = genai.Client(api_key="AIzaSyCjlgeHj1QMhjXTlO9c5ioizIP8XPtu3dE")

VIDEO_FOLDER = "data/video"  # 视频文件夹路径
OUTPUT_JSON = "data/social_relation_results.json"  # 输出的 JSON 文件

prompt = """
    You are an expert in social relationships. Analyze the given video and output structured information in JSON format.
    Required fields:
    {
        "relationship_type": "One of [Leader-subordinate, Colleague, Service, Parent-offspring, Sibling, Couple, Friend, Opponent]",
        "intimacy_level": "One of [Very Poor, Poor, Average, Good, Very Good]",
        "justification": "Brief explanation for your choice"
    }
"""

def extract_json(text):
    """提取 Markdown 代码块中的 JSON 内容"""
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else text

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
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(temperature=0)
            )
            clean_text = extract_json(response.text)
            return json.loads(clean_text)
        except Exception as e:
            print(f"Error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
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
    
    processed_files = {entry["video_name"] for entry in results}
    
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.endswith((".mp4", ".avi", ".mov")):
            if filename in processed_files:
                print(f"Skipping already processed file: {filename}")
                continue
            
            video_path = os.path.join(VIDEO_FOLDER, filename)
            print(f"Processing: {filename}")
            analysis_result = process_video(video_path)
            if analysis_result:
                results.append({"video_name": filename, "analysis": analysis_result})
                with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Analysis complete. Results saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
