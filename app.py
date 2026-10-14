from __future__ import annotations

import base64
import secrets
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import gradio as gr
import requests
from PIL import Image

# 现有 Rapid-MLX 服务；仅调用 API，不会重复加载模型
API_URL = "http://127.0.0.1:8000/v1/images/generations"
MODEL_NAME = "qwen-image-2.1"
PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RESOLUTIONS = {
    "512 × 512（首次测试推荐）": (512, 512),
    "768 × 512（横图）": (768, 512),
    "512 × 768（竖图）": (512, 768),
    "768 × 768": (768, 768),
    "1024 × 768（横图）": (1024, 768),
    "768 × 1024（竖图）": (768, 1024),
    "1024 × 1024（占用较大）": (1024, 1024),
    "自定义宽高": None,
}


def choose_size(choice: str, width: float, height: float) -> str:
    if choice != "自定义宽高":
        if choice not in RESOLUTIONS:
            raise gr.Error("请选择有效的分辨率。")
        w, h = RESOLUTIONS[choice]
    else:
        if width is None or height is None:
            raise gr.Error("请输入自定义宽度和高度。")
        w, h = int(width), int(height)
        if not (128 <= w <= 1536 and 128 <= h <= 1536):
            raise gr.Error("自定义宽高须在 128～1536 像素之间。")
        if w % 16 != 0 or h % 16 != 0:
            raise gr.Error("自定义宽高建议均为 16 的倍数。")
    return f"{w}x{h}"


def show_custom_size(choice: str):
    show = choice == "自定义宽高"
    return gr.update(visible=show), gr.update(visible=show)


def extract_image(result: dict) -> Image.Image:
    items = result.get("data")
    if not isinstance(items, list) or not items:
        raise ValueError("API 响应中找不到 data[0]。")

    item = items[0]
    if item.get("b64_json"):
        raw = base64.b64decode(item["b64_json"])
    elif item.get("url"):
        image_response = requests.get(item["url"], timeout=120)
        image_response.raise_for_status()
        raw = image_response.content
    else:
        raise ValueError("API 未返回 b64_json 或 url 图片数据。")

    with Image.open(BytesIO(raw)) as img:
        return img.convert("RGB")


def generate(prompt, resolution, width, height, steps, seed):
    prompt = (prompt or "").strip()
    if not prompt:
        raise gr.Error("请先输入提示词。")

    size = choose_size(resolution, width, height)
    actual_seed = secrets.randbelow(2**31 - 1) if seed is None or int(seed) < 0 else int(seed)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "size": size,
        "steps": int(steps),
        "seed": actual_seed,
        "response_format": "b64_json",
    }

    started = time.perf_counter()
    try:
        response = requests.post(API_URL, json=payload, timeout=(15, 3600))
    except requests.exceptions.ConnectionError as exc:
        raise gr.Error(
            "无法连接 Rapid-MLX。请先在另一个终端启动：\n"
            "rapid-mlx serve qwen-image-2.1 --host 127.0.0.1 --port 8000"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise gr.Error(f"请求模型服务失败：{exc}") from exc

    if not response.ok:
        raise gr.Error(f"Rapid-MLX 生成失败（HTTP {response.status_code}）：{response.text[:1800]}")

    try:
        image = extract_image(response.json())
    except (ValueError, KeyError, TypeError, requests.exceptions.RequestException) as exc:
        raise gr.Error(f"解析模型响应失败：{exc}") from exc

    elapsed = time.perf_counter() - started
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qwen21_{stamp}_{size}_{actual_seed}.png"
    output_path = OUTPUT_DIR / filename
    image.save(output_path, format="PNG")

    status = (
        "### 生成成功\n"
        f"- **分辨率：** {size}\n"
        f"- **推理步数：** {int(steps)}\n"
        f"- **随机种子：** {actual_seed}\n"
        f"- **耗时：** {elapsed:.1f} 秒\n"
        f"- **保存位置：** `{output_path}`"
    )
    return image, status, str(output_path)


with gr.Blocks(title="Qwen-Image-2.1 · 本地图像生成") as demo:
    gr.Markdown(
        "# Qwen-Image-2.1 本地 WebUI\n"
        "使用已有的 Rapid-MLX 服务生成图片，PNG 自动保存到 `outputs/`。\n"
        "建议 Mac 16GB 首次用 512×512 / 20 步。"
    )

    with gr.Row():
        with gr.Column(scale=1):
            prompt_input = gr.Textbox(
                label="提示词 / Prompt",
                lines=6,
                placeholder="例如：一只橘猫坐在窗台上，窗外是金黄色银杏树，柔和自然光，电影摄影，写实风格",
            )
            resolution_input = gr.Dropdown(
                choices=list(RESOLUTIONS.keys()),
                value="512 × 512（首次测试推荐）",
                label="分辨率",
            )
            with gr.Row():
                width_input = gr.Number(label="自定义宽度", value=512, precision=0, visible=False)
                height_input = gr.Number(label="自定义高度", value=512, precision=0, visible=False)
            steps_input = gr.Slider(
                minimum=4, maximum=60, value=20, step=1,
                label="推理步数（更多步数通常更慢）",
            )
            seed_input = gr.Number(label="随机种子（-1 代表随机）", value=-1, precision=0)
            generate_button = gr.Button("生成图片", variant="primary")

        with gr.Column(scale=1):
            image_output = gr.Image(label="生成结果", type="pil", interactive=False)
            status_output = gr.Markdown()
            download_output = gr.File(label="下载 PNG 图片")

    resolution_input.change(
        fn=show_custom_size,
        inputs=resolution_input,
        outputs=[width_input, height_input],
    )
    generate_button.click(
        fn=generate,
        inputs=[prompt_input, resolution_input, width_input, height_input, steps_input, seed_input],
        outputs=[image_output, status_output, download_output],
        concurrency_limit=1,
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch(server_name="127.0.0.1", server_port=7862, inbrowser=True, share=False)
