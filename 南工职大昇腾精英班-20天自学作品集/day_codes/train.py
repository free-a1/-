import json

def read_ppm(path):
    with open(path, "rb") as f:
        assert f.readline().strip() == b"P6"
        f.readline()
        f.readline()
        data = f.read()
    px = [(data[i], data[i+1], data[i+2]) for i in range(0, len(data), 3)]
    return px

model = {}
for label, path in [("red", "/home/user/project/data/train_red.ppm"),
                    ("blue", "/home/user/project/data/train_blue.ppm")]:
    px = read_ppm(path)
    n = len(px)
    model[label] = [round(sum(p[i] for p in px) / n) for i in range(3)]

with open("/home/user/project/data/model.json", "w") as f:
    json.dump(model, f)
print("模型权重:", model)
