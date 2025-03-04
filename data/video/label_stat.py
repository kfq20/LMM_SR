from collections import Counter

# 读取文件并统计标签数量
label_counts = Counter()

with open("/Users/fancy/Desktop/project/social_relation/data/video/labels_all.txt", "r") as f:
    for line in f:
        _, label = line.strip().split("\t")  # 按 tab 分割
        label_counts[label] += 1

# 输出每个标签的数量
for label, count in sorted(label_counts.items(), key=lambda x: int(x[0])):
    print(f"标签 {label}: {count} 个")
# 打开文件并查找标签为 9 的行
with open("/Users/fancy/Desktop/project/social_relation/data/video/labels_all.txt", "r") as f:
    for line_number, line in enumerate(f, start=1):  # 记录行号
        parts = line.strip().split("\t")  # 按 Tab 分割
        if len(parts) == 2 and parts[1] == "9":  # 检查标签是否为 9
            print(f"第 {line_number} 行: {line.strip()}")
