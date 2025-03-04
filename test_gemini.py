from google import genai

client = genai.Client(api_key="")

print("Uploading file...")
# video_file = client.files.upload(file="/Users/fancy/Downloads/ViSR_v1.0/ViSR_v1.0/video/0531.avi")
video_file = client.files.upload(file="/Users/fancy/Desktop/project/social_relation/data/test/0223.avi")
print(f"Completed upload: {video_file.uri}")
# exit()

for file in client.files.list():
    print(file.name)

# video_file = client.files.get(name="files/umd1yuiek59r")

import time

# Check whether the file is ready to be used.
while video_file.state.name == "PROCESSING":
    print('.', end='')
    time.sleep(1)
    video_file = client.files.get(name=video_file.name)

if video_file.state.name == "FAILED":
  raise ValueError(video_file.state.name)

print('Done')
# exit()
prompt = """In your role as a specialist in social relations, you possess the capability to precisely determine the nature of
social relationships shown in this video. The range of your expertise encompasses 8 unique categories of
social relationships, with each duo of individuals categorized under one of these. The relationship type you conclude should be among the following
8 unique categories: {<Leader- subordinate>, <Colleague>, <Service>, <Parent-offspring>, <Sibling>, <Couple>,
<Friend>, <Opponent>}. What are the most likely social relationships between the two main individuals in this video? Choose only one from the list of 8 categories. Then, based on your understanding of social relationships, please evaluate the level of intimacy between the two people in the video. You should categorize the relationship into one of the following five levels: Very Poor, Poor, Average, Good, or Very Good. You are only allowed to choose one category. First, provide your answer.
Then, give a brief explanation for your choice."""
# Pass the video file reference like any other media part.
response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=[
        video_file,
        prompt],
        temperature=0)

# Print the response, rendering any Markdown
print(response.text)