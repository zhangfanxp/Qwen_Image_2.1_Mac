from gradio_client import Client

client = Client("http://127.0.0.1:7862")

# 查看当前 API 名称及参数
client.view_api()

result = client.predict(
    "一只橘猫坐在窗台上，电影摄影，超清画质",
    "512 × 512（首次测试推荐）",
    512,
    512,
    20,
    -1,
    api_name="/generate"
)

print(result)
