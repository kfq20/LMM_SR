import cv2
from ultralytics import YOLO

# 视频路径
video_path = 'data/test.mp4'
output_video_path = 'data/test_process.mp4'

# 加载预训练的YOLO模型
model = YOLO("yolov5s.pt")  # 如果你有更大的YOLO模型，可以换成yolov5m.pt、yolov5l.pt等

# 打开视频文件
cap = cv2.VideoCapture(video_path)

# 获取视频帧率和尺寸
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 设置视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (frame_width, frame_height))

# 存储符合条件的帧
person_frames = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 目标检测
    results = model(frame)
    
    # 获取第一个检测结果
    # detections = results[0].pandas().xywh  # 获取第一个帧的检测结果
    person_count = list(results[0].names.values()).count('person')
    # 获取检测到的人物数量
    # person_count = len(detections[detections['name'] == 'person'])
    # person_count = len(results[0].names)  # 获取检测到的所有类别名称
    
    # 如果检测到两个人及以上，保存该帧
    if person_count >= 2:
        person_frames.append(frame)

# 将符合条件的帧写入输出视频
for frame in person_frames:
    out.write(frame)

# 释放资源
cap.release()
out.release()

print("视频处理完毕，输出视频已保存至:", output_video_path)
