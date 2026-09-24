import json, urllib.request, urllib.error, sys

class InferClient:
    def __init__(self, url):
        self.url = url

    def predict(self, img):
        try:
            req = urllib.request.Request(
                self.url, data=json.dumps({"image": img}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                return json.loads(r.read().decode())
        except urllib.error.URLError as e:
            print("请求失败:", e)
            return None

client = InferClient("http://127.0.0.1:8080/predict")
imgs = ["a.jpg", "b.jpg", "c.jpg"]
for i, img in enumerate(imgs):
    pct = int((i) / len(imgs) * 100)
    print(f"\r进度 [{pct:3d}%] {img}", end="")
    client.predict(img)
print("\r进度 [100%] 完成      ")
