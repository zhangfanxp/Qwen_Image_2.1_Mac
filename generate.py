
import base64
import time
from pathlib import Path

import requests

# Rapid-MLX API 地址
API_URL = "http://127.0.0.1:8000/v1/images/generations"

# 输出目录
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 图像生成参数
payload = {
    "model": "qwen-image-2.1",
    "prompt": (
        "一只可爱的橘猫坐在中国古老的木质窗台上，"
        "窗外是秋天的银杏树，金黄色的阳光，"
        "照片级真实感，电影摄影，自然光线，"
        "细节丰富，画面精美"
    ),
    "size": "512x512",
    "steps": 20,
    "seed": 42,
    "response_format": "b64_json"
}

print("开始生成图片...")
start = time.time()

response = requests.post(
    API_URL,
    json=payload,
    timeout=3600
)

if not response.ok:
    print("API 错误:", response.text)
    response.raise_for_status()

result = response.json()
image_b64 = result["data"][0]["b64_json"]

# 解码 Base64 图片
image_bytes = base64.b64decode(image_b64)

# 保存 PNG
output_path = OUTPUT_DIR / "qwen21_test.png"
output_path.write_bytes(image_bytes)

elapsed = time.time() - start

print(f"生成完成：{output_path.resolve()}")
print(f"耗时：{elapsed:.2f} 秒")

