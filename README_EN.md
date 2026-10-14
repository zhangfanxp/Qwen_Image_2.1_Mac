# Qwen-Image-2.1 Mac WebUI — Quick Start

A lightweight **Gradio** front end for Qwen-Image-2.1 on Apple Silicon using a separate **Rapid-MLX** image-generation server. Model weights are **not** included.

For detailed installation instructions and a code walkthrough in Chinese, see [README.md](README.md).

## Features

- Chinese or English text prompts
- Preset and custom image sizes (custom dimensions must be multiples of 16, 128–1536 pixels)
- Steps (4–60), seed selection (`-1` means random)
- Preview, download, and automatic local PNG saving under `outputs/`
- Sequential generation requests (`concurrency_limit=1`)

## Requirements

- macOS on Apple Silicon (`uname -m` should show `arm64`)
- Python 3.12 via [uv](https://docs.astral.sh/uv/)
- Enough system memory and disk space for the ~8.9 GB 4-bit model; start with 512×512 and 20 steps on a 16 GB Mac

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/qwen-image-2.1-mac-webui.git
cd qwen-image-2.1-mac-webui
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Download the model into the standard Hugging Face cache (`~/.cache/huggingface/hub/` unless overridden):

```bash
hf download mlx-community/Qwen-Image-2.1-mflux-q4
python -c "from huggingface_hub import constants; print(constants.HF_HUB_CACHE)"
```

**Terminal A — Model API**

```bash
./scripts/start_server.sh
# Equivalent to:
# rapid-mlx serve qwen-image-2.1 --host 127.0.0.1 --port 8000
```

**Terminal B — WebUI**

```bash
./scripts/start_webui.sh
# Equivalent to: python app.py
```

Visit **http://127.0.0.1:7862** and enter a prompt. Images are saved in `outputs/` (not committed to Git).

## API flow

`app.py` calls `POST http://127.0.0.1:8000/v1/images/generations` with `model`, `prompt`, `size`, `steps`, `seed`, and `response_format=b64_json`. The UI never loads the model directly. See the Chinese README for explanations of `choose_size()`, `extract_image()`, `generate()`, output handling, troubleshooting, and GitHub publishing.

## Security and licenses

The WebUI is bound to localhost and Gradio sharing is disabled. Do not publish its HTTP ports or expose them via a tunnel without authentication and rate limiting. Model licenses and third-party dependencies are linked in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The application code has no declared repository license until its owner adds one.

## References

- [Quantized model](https://huggingface.co/mlx-community/Qwen-Image-2.1-mflux-q4)
- [Rapid-MLX Qwen Image documentation](https://rapidmlx.com/docs/models/families/qwen-image)
- [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/guides/cli)
