import os, shutil
raw = os.path.expanduser("~/project/data/raw")
for name in os.listdir(raw):
    label = name.rstrip("0123456789")
    os.makedirs(f"{raw}/{label}", exist_ok=True)
    shutil.move(f"{raw}/{name}", f"{raw}/{label}/{name}")
    with open(f"{raw}/../labels.csv", "a") as f:
        f.write(f"{name},{label}\n")
print("分类完成")
