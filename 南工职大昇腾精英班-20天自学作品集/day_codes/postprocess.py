import json

def load_result(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def to_report(data):
    lines = ["文件名,类别,置信度"]
    for item in data:
        lines.append(f"{item['name']},{item['label']},{item['score']}")
    return "\n".join(lines)

data = load_result("~/project/data/result.json")
with open("~/project/data/report.txt", "w", encoding="utf-8") as f:
    f.write(to_report(data))
print("报表已生成")
