import random, json
random.seed(7)

def make_ppm(path, base, noise=25):
    w, h = 32, 32
    with open(path, "wb") as f:
        f.write(f"P6\n{w} {h}\n255\n".encode())
        for _ in range(w * h):
            px = [max(0, min(255, c + random.randint(-noise, noise))) for c in base]
            f.write(bytes(px))

make_ppm("/home/user/project/data/train_red.ppm", (200, 40, 40))
make_ppm("/home/user/project/data/train_blue.ppm", (40, 60, 200))
make_ppm("/home/user/project/data/test1.ppm", (190, 55, 45))
make_ppm("/home/user/project/data/test2.ppm", (50, 70, 190))
print("数据集生成完成")
