from google import genai
from google.genai import types
import os
import json
import time
import re
from tqdm import tqdm

client = genai.Client(api_key="AIzaSyCjlgeHj1QMhjXTlO9c5ioizIP8XPtu3dE")

VIDEO_FOLDER = "/Volumes/XDISK/tiktok/"  # 视频文件夹路径
OUTPUT_JSON = "results/tiktok/gemini_results.json"  # 输出的 JSON 文件

prompt = """
You are tasked with analyzing a video and understanding the social relationship it depicts (like relation type, affinity, and human interactions). Please adhere to the following guidelines:

Primary Relationship Identification: If the video features multiple people or various types of social relationships, select and output the most prominent one.
Performance Consideration: If the video includes elements of performance, determine and describe which social relationship is being portrayed through the performance.
Cameraperson Inference: Be mindful that the person filming may also be involved in the interactions within the video. Use your reasoning skills to infer the possible social relationship between the cameraperson and the individuals in the video.

You should output structured information in JSON format.
    Required fields:
    {
        "relation type": One of [boss-employee, classmate, coach-player, colleagues, couple, elderly-caregiver, friends, grandparent-child, parent-child, service, siblings, sports-teammate, teacher-student],
        "affinity": One of [Very Poor, Poor, Average, Good, Very Good],
        "reason": Explanation for your choice,
        "summary": Summarize the key selling point of this video in one sentence—the core message or main idea that the creator wants to convey about the social relationship,
    }

Here are more detailed explanations of the relationship types:
- boss-employee: A hierarchical work relationship where one person holds authority over the other, such as a manager and their subordinate.
- classmate: A peer relationship between students or individuals in the same educational setting.
- coach-player: A mentorship relationship where one person guides, trains, or instructs the other in a specific skill or activity, such as a sports coach and their athlete. Interactions may involve feedback, encouragement, or skill development.
- colleagues: A professional relationship between coworkers or individuals in the same field.
- couple: A romantic relationship between two people.
- elderly-caregiver: A supportive relationship where one person provides care, assistance, or companionship to an elderly individual.
- friends: A social relationship based on mutual affection, trust, and shared interests.
- grandparent-child: A familial relationship between grandparents and grandchildren.
- parent-child: A familial relationship between parents and their children.
- service: A transactional relationship where one person provides a service or assistance to another.
- siblings: A familial relationship. Siblings share a common parent or guardian.
- sports-teammate: A cooperative relationship between teammates in a sports setting.
- teacher-student: An educational relationship where one person imparts knowledge, guidance, or instruction to the other.

Affinity:
- good affinity: If the main character(s) exhibit kindness, friendliness, warmth, support, encouragement, or cooperation, the affinity level should be considered good.
- poor affinity: If the video contains violence, discrimination, insults, arguments, emotional coldness, neglect, or any negative interactions, the affinity level should be considered poor.

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
                model="gemini-2.0-flash",
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
    else:
        print(f"Creating new output file: {OUTPUT_JSON}")

    
    processed_files = {entry["video_path"] for entry in results}
    
    # 遍历 VIDEO_FOLDER 及所有子目录
    for root, _, files in os.walk(VIDEO_FOLDER):
        for filename in files:
            if filename.startswith("._"):
                continue

            if filename.endswith((".mp4", ".avi", ".mov")):
                video_path = os.path.join(root, filename)

                # 检查是否已处理过
                if video_path in processed_files:
                    continue
                
                print(f"Processing: {video_path}")
                analysis_result = process_video(video_path)

                if analysis_result:
                    results.append({"video_path": video_path, 
                                    # "path": video_path,
                                    "analysis": analysis_result})
                    
                    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Analysis complete. Results saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
