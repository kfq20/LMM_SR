import json
import openai
from openai import AzureOpenAI
import time
from tqdm import tqdm
import re

REGION = "eastus"
MODEL = "gpt-4o-mini-2024-07-18"
API_KEY = ""

API_BASE = "https://api.tonggpt.mybigai.ac.cn/proxy"
ENDPOINT = f"{API_BASE}/{REGION}"

client = AzureOpenAI(
            api_key=API_KEY,
            api_version="2024-02-01",
            azure_endpoint=ENDPOINT,
        )

# 读取 JSON 文件
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_json(text):
    """提取 Markdown 代码块中的 JSON 内容"""
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else text  # 如果找不到，返回原文本


# 解析 `analysis` 数据，处理嵌套和不同的 key 名称
def extract_relevant_info(analysis, keys_to_use):
    """
    从分析数据中提取相关信息，keys_to_use 控制使用哪些部分 (如 ["speaker", "verbal"])
    """
    def find_matching_keys(d, keywords):
        """递归查找包含特定关键词的 key"""
        if len(d) == 1:
            key, value = next(iter(d.items()))
            if isinstance(value, dict):
                return find_matching_keys(value, keywords)
        extracted = {}
        for key, value in d.items():
            key_lower = key.lower()
            for kw in keywords:
                if kw == 'verbal':
                    if kw in key_lower and 'non' not in key_lower:
                        extracted[key] = value
                        break
                else:
                    if kw in key_lower:
                        extracted[key] = value
                        break
        return extracted

    keywords = [k.lower() for k in keys_to_use]
    return find_matching_keys(analysis, keywords)

# 调用 GPT-4 进行分析
def analyze_relationship(video_data, keys_to_use):
    """
    使用 GPT-4 API 进行社交关系分类
    """
    filtered_data = extract_relevant_info(video_data["analysis"], keys_to_use)
    
    prompt = f"""
    You are an expert in social relationships. Analyze the given video and output structured information in JSON format.

    Video Description:
    {json.dumps(filtered_data, indent=4, ensure_ascii=False)}

    Required fields:
    {{
        "relationship_type": "One of [Leader-subordinate, Colleague, Service, Parent-offspring, Sibling, Couple, Friend, Opponent]",
        "intimacy_level": "One of [Very Poor, Poor, Average, Good, Very Good]",
        "justification": "Brief explanation for your choice"
    }}
    Respond only with a valid JSON object. You should choose only one relationship type and one intimacy level.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": f"{prompt}"}
            ],
            temperature=0.0
        )
        result_text = response.choices[0].message.content.strip()
        return json.loads(extract_json(result_text))  # 确保返回 JSON 结构
    
    except Exception as e:
        print(f"Error analyzing video {video_data.get('video_name', 'unknown')}: {e}")
        return None

# 处理整个 JSON 数据集
def process_videos(input_file, output_file, keys_to_use):
    """
    处理 JSON 文件中的所有视频数据，并存储分类结果
    """
    videos = load_json(input_file)
    results = []
    for video in tqdm(videos, desc="Processing videos"):
        relationship_result = {}
        result = analyze_relationship(video, keys_to_use)
        if result:
            relationship_result["relationship_analysis"] = result
            relationship_result["name"] = video["video_name"]
        results.append(relationship_result)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        # 避免 OpenAI API 速率限制
        # time.sleep(1.5)

    # 保存结果
    

# 运行主程序
if __name__ == "__main__":
    input_json = "/Users/fancy/Desktop/project/social_relation/data/analysis_results.json"  # 输入 JSON 文件路径
    
    # keys_to_use = ["speaker", "verbal", "non", "environment"]  # 可控制使用哪些信息
    keys_to_use = ["speaker", "verbal"]
    output_json = f"/Users/fancy/Desktop/project/social_relation/data/language_results_sv.json"  # 输出 JSON 文件路径
    process_videos(input_json, output_json, keys_to_use)
