# Qwen-Image-2.1 Mac 本地 WebUI（MLX 4-bit）

> 在 Apple Silicon Mac 上使用 **uv + Rapid-MLX + Gradio** 运行 Qwen-Image-2.1 量化版。浏览器输入中文/英文提示词、选择分辨率、设置推理步数与随机种子，一键生成图片并保存 PNG。
>
> 本仓库**仅提供 WebUI / 启动脚本**；模型权重不随仓库分发，也**不需要**复制到 GitHub。

[模型（MLX 4-bit）](https://huggingface.co/mlx-community/Qwen-Image-2.1-mflux-q4) · [基础模型](https://huggingface.co/Qwen/Qwen-Image-2.1) · [Rapid-MLX](https://github.com/raullenchai/Rapid-MLX) · [Rapid-MLX Qwen Image 文档](https://rapidmlx.com/docs/models/families/qwen-image)

## 1. 功能介绍

- 文生图：中文或英文提示词（Prompt）。
- 预设尺寸：`512×512`、`768×512`、`512×768`、`768×768`、`1024×768`、`768×1024`、`1024×1024`。
- 自定义尺寸：宽高各 `128–1536` 像素，且必须是 `16` 的倍数（按当前 `app.py` 校验规则）。
- 推理步数：`4–60`，默认 `20`；随机种子：`-1` 为随机，其余非负整数为指定种子。
- 在线预览、下载 PNG；自动保存到 `outputs/`。
- 请求由本地 Rapid-MLX 的 HTTP API 处理，Gradio **不会再额外加载一份模型**。
- 同一时间只允许 1 个 WebUI 生成任务执行，避免并发增加内存压力。

> 当前 WebUI 实现的是**文生图**。虽然部分底层模型/服务支持图像编辑，但此项目尚未提供参考图上传或图生图界面；也没有负向提示词或透明背景开关。

## 2. 推荐硬件与运行方式

| 项目 | 建议 / 当前默认值 |
| --- | --- |
| 电脑 | Apple Silicon Mac（例如 M5 / 16GB 统一内存） |
| 操作系统 | macOS，原生 `arm64` 终端 |
| Python | `3.12` |
| 虚拟环境 | `uv`，目录 `.venv/` |
| 推理服务 | Rapid-MLX `0.16.1`，`127.0.0.1:8000` |
| 模型名称（API alias） | `qwen-image-2.1` |
| 模型仓库（HF repo ID） | `mlx-community/Qwen-Image-2.1-mflux-q4` |
| Gradio 页面 | `http://127.0.0.1:7862` |
| 模型默认缓存 | `~/.cache/huggingface/hub/` |

该模型约有 8.9 GB 权重，Transformer 与文本编码器采用 MLX 4-bit 量化。上游的内存测量是在 Mac Studio 上进行的，**不能保证每台 16GB Mac 在高分辨率下都不触发内存压力**。建议先用 `512×512 / 20 步` 验证。此项目只面向 Mac；不能直接把 MLX 权重部署到 NVIDIA T4 环境。详见[上游模型卡](https://huggingface.co/mlx-community/Qwen-Image-2.1-mflux-q4)。

## 3. 项目结构

```text
qwen-image-2.1-mac-webui/
├── app.py                         # Gradio 页面 + HTTP API 调用
├── requirements.txt               # Python 依赖
├── .gitignore                     # 排除模型、虚拟环境、图片及密钥等
├── .gitattributes                 # 文本换行规范
├── README.md                      # 本说明书
├── README_EN.md                   # English quick start
├── THIRD_PARTY_NOTICES.md         # 第三方项目与许可说明
├── scripts/
│   ├── start_server.sh            # 启动 Rapid-MLX（终端 A）
│   └── start_webui.sh             # 启动 Gradio（终端 B）
└── outputs/
    └── .gitkeep                   # 占位文件；实际 PNG 不上传 GitHub
```

模型权重**不在**项目目录：

```text
~/.cache/huggingface/hub/
└── models--mlx-community--Qwen-Image-2.1-mflux-q4/
    ├── blobs/
    ├── refs/
    └── snapshots/
        └── <commit-id>/
```

`snapshots` 下实际文件通常是指向 `blobs` 的链接，**不要将它们手动复制进 Git 仓库**。

## 4. 完整部署步骤（Mac + uv）

### 步骤 1：检查 Apple Silicon / 安装 uv

终端执行：

```bash
uname -m                   # 预期：arm64
sw_vers
uv --version
```

若未安装 uv（已安装 Homebrew 的情况）：

```bash
brew install uv
```

也可参照 [uv 官方安装文档](https://docs.astral.sh/uv/getting-started/installation/)。若 `uname -m` 显示 `x86_64`，请确认 Terminal 没有以 Rosetta 运行。

### 步骤 2：获取本仓库

从 GitHub 克隆（发布后将下面地址改为你的实际仓库）：

```bash
git clone https://github.com/YOUR_USERNAME/qwen-image-2.1-mac-webui.git
cd qwen-image-2.1-mac-webui
```

如果已经把文件放在 `~/Documents/Qwen-Image-2.1`，可以直接进入现有目录，**无需再次克隆**：

```bash
cd ~/Documents/Qwen-Image-2.1
```

确保 `app.py`、`requirements.txt`、`scripts/` 同在项目根目录。

### 步骤 3：创建 Python 3.12 虚拟环境

```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
python --version          # 预期：Python 3.12.x
```

安装依赖：

```bash
uv pip install -r requirements.txt
```

包含 `rapid-mlx[image]==0.16.1`、`gradio`、`requests`、`Pillow`、`huggingface_hub[hf_xet]`。`requirements.txt` 是直接依赖清单（部分依赖使用兼容范围），不是完全锁定所有传递依赖的 `uv.lock`。如需团队跨机器严格复现，可在验证可用后单独生成锁文件。

快速检查：

```bash
rapid-mlx --help
hf --help
python -c "import gradio, requests, PIL; print('WebUI 依赖正常')"
python -m py_compile app.py
```

### 步骤 4：用 `hf` 命令下载模型（保存在默认缓存）

**重点：不要加 `--local-dir`，也不要把模型下载到 Git 仓库。**

先查看当前 Hugging Face 缓存位置：

```bash
python -c "from huggingface_hub import constants; print(constants.HF_HUB_CACHE)"
```

未设置自定义 `HF_HOME` / `HF_HUB_CACHE` 时，典型输出：

```text
/Users/你的用户名/.cache/huggingface/hub
```

下载完整的 MLX 量化模型：

```bash
hf download mlx-community/Qwen-Image-2.1-mflux-q4
```

该命令默认下载当前仓库默认分支版本，并返回本地 `snapshots/<commit-id>` 路径。后续执行同样命令一般复用有效缓存文件；如果上游分支更新，新修订版可能产生额外下载。需要固定特定模型版本时，可显式指定已确认的 `--revision <commit-id>`。

检查下载位置和大小：

```bash
ls -lah ~/.cache/huggingface/hub/models--mlx-community--Qwen-Image-2.1-mflux-q4/
du -sh ~/.cache/huggingface/hub/models--mlx-community--Qwen-Image-2.1-mflux-q4/
```

可选：检查缓存条目：

```bash
hf cache ls
```

网络慢时可提高下载超时后重试：

```bash
export HF_HUB_DOWNLOAD_TIMEOUT=60
hf download mlx-community/Qwen-Image-2.1-mflux-q4
```

**缓存路径说明：** `HF_HOME` / `HF_HUB_CACHE` 或旧版本工具配置可能更改默认位置，应以上面 Python 命令输出为准。Rapid-MLX 若使用不同的模型修订版，可能仍会下载缺失的修订文件。

### 步骤 5：启动模型服务（终端 A）

在已激活虚拟环境的终端中运行：

```bash
rapid-mlx serve qwen-image-2.1 --host 127.0.0.1 --port 8000
```

或者在项目根目录使用启动脚本（脚本自动激活 `.venv`）：

```bash
./scripts/start_server.sh
```

`qwen-image-2.1` 是 Rapid-MLX 的**模型别名**，它指向 `mlx-community/Qwen-Image-2.1-mflux-q4`，不是 BF16 全精度模型。启动后保持终端 A 打开。

尝试在**另一个终端**检查服务：

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
```

你也可以访问 `http://127.0.0.1:8000/docs` 查看接口（取决于所安装服务版本暴露的 API）。如果服务尚在加载模型，请观察终端 A 的日志再确认。

### 步骤 6：启动 WebUI（终端 B）

```bash
cd ~/Documents/Qwen-Image-2.1       # 或你的实际项目目录
source .venv/bin/activate
python app.py
```

也可以从仓库根目录运行：

```bash
./scripts/start_webui.sh
```

浏览器访问：**http://127.0.0.1:7862**。首次启动 `inbrowser=True` 会尝试自动打开浏览器。关闭任一服务时，在对应终端按 `Control + C`。

### 步骤 7：生成第一张图片

1. 在 Prompt 中输入：`一只橘猫坐在窗台上，窗外是金黄色银杏树，柔和自然光，电影摄影，写实风格`。
2. 分辨率选择 **512 × 512（首次测试推荐）**。
3. 推理步数设为 **20**；随机种子设为 **-1**。
4. 点击**生成图片**，完成后可在线预览、下载 PNG。
5. 自动生成文件在：`项目根目录/outputs/qwen21_日期时间_尺寸_种子.png`。

如果 16GB Mac 在较大分辨率出现显著的内存压力，先关闭其他占用统一内存的模型进程，再降低分辨率；不要把“8GB+”标称最低门槛误解为任何参数下都稳定。

## 5. 使用 Rapid-MLX API（不启动 WebUI 也可调用）

WebUI 发送请求到：

```text
POST http://127.0.0.1:8000/v1/images/generations
Content-Type: application/json
```

JSON 请求示例：

```json
{
  "model": "qwen-image-2.1",
  "prompt": "A cute orange cat by a window, warm autumn light, photorealistic",
  "size": "512x512",
  "steps": 20,
  "seed": 42,
  "response_format": "b64_json"
}
```

可用 `curl` 测试（响应可能包含很长的 Base64 图片字符串）：

```bash
curl -sS http://127.0.0.1:8000/v1/images/generations \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen-image-2.1","prompt":"an orange cat by the window","size":"512x512","steps":20,"seed":42,"response_format":"b64_json"}' \
  -o test_response.json
```

`app.py` 会负责将 `data[0].b64_json` 解码并保存 PNG；接口若返回图片 URL，也有回退处理。

## 6. 核心代码说明（按当前 `app.py`）

### 6.1 服务配置和文件位置

```python
API_URL = "http://127.0.0.1:8000/v1/images/generations"
MODEL_NAME = "qwen-image-2.1"
PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

- `API_URL`：仅调用已经启动的模型服务，不在 Gradio 进程加载权重。
- `MODEL_NAME`：与 Rapid-MLX 服务注册的模型 alias 相同。
- `PROJECT_DIR`：永远以 `app.py` 所在目录作为保存基准，避免从其他工作目录启动时找不到输出文件。
- `OUTPUT_DIR`：自动创建 `outputs/`；`.gitignore` 已忽略其 PNG。

### 6.2 分辨率预设与校验：`RESOLUTIONS` / `choose_size()`

```python
size = choose_size(resolution, width, height)
```

如果选择预设尺寸，返回预设 `(宽, 高)`；如果选择 `自定义宽高`，要求两个值都已填写、介于 `128` 与 `1536` 之间且都能被 `16` 整除。最终构造 `"512x512"` 一类字符串交给 API。注意大尺寸是否可生成仍取决于模型/内存，并非前端验证通过即可保证成功。

### 6.3 显示/隐藏自定义尺寸输入：`show_custom_size()`

```python
resolution_input.change(
    fn=show_custom_size,
    inputs=resolution_input,
    outputs=[width_input, height_input],
)
```

仅在分辨率选择为 `自定义宽高` 时，显示宽度和高度的输入框。

### 6.4 推理请求：`generate()`

函数按照以下流程执行：

1. 清理 Prompt，拒绝空提示词。
2. 通过 `choose_size()` 获取尺寸。
3. 将随机种子 `-1` 换成 `secrets.randbelow(...)` 生成的整数；其他整数原样传递。
4. 组合请求 JSON：`model`、`prompt`、`size`、`steps`、`seed`、`response_format`。
5. 使用 `requests.post(API_URL, json=payload, timeout=(15, 3600))` 请求 Rapid-MLX；连接超时 15 秒，读取超时 3600 秒。
6. 非 2xx 状态提示错误，成功时解析返回图片、写入 PNG，并将图片、生成信息和文件路径返回给 Gradio。

核心片段：

```python
payload = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "size": size,
    "steps": int(steps),
    "seed": actual_seed,
    "response_format": "b64_json",
}
response = requests.post(API_URL, json=payload, timeout=(15, 3600))
```

### 6.5 图片解码：`extract_image()`

优先解析 `data[0].b64_json`，使用 `base64.b64decode()` 解码；如果 API 返回 `data[0].url`，改用 `requests.get()` 获取图片字节，然后 Pillow `Image.open()`、`convert("RGB")`，最终得到 `PIL.Image.Image`。

### 6.6 保存 PNG、状态信息和下载按钮

```python
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"qwen21_{stamp}_{size}_{actual_seed}.png"
output_path = OUTPUT_DIR / filename
image.save(output_path, format="PNG")
return image, status, str(output_path)
```

函数返回三个值，对应页面中的生成预览、Markdown 状态信息和 `gr.File` 下载组件。保存文件名包含时间、尺寸和种子；如果在同一秒使用完全相同尺寸与种子生成，当前实现可能覆盖前一个同名文件。

### 6.7 WebUI 布局和并发限制

- `gr.Blocks()`：页面容器。
- `gr.Textbox()`：提示词。
- `gr.Dropdown()` / `gr.Number()`：尺寸选择及自定义宽高。
- `gr.Slider()`：推理步数。
- `gr.Button.click()`：将输入组件映射到 `generate()`。
- `concurrency_limit=1`：一次处理一个生成任务，降低 16GB Mac 并发压力。
- `demo.queue()`：开启 Gradio 请求队列。
- `demo.launch(server_name="127.0.0.1", server_port=7862, inbrowser=True, share=False)`：仅本机访问，不生成公网分享链接。

**端口修改：** 如果将 Rapid-MLX 改为 8001，需要修改 `app.py` 顶部的 `API_URL`，并同步修改启动脚本。WebUI 端口变更只需修改 `app.py` 末尾 `server_port`。

## 7. 常见问题与排查

| 现象 | 原因与处理 |
| --- | --- |
| `SyntaxError` | 先运行 `python -m py_compile app.py`；确认拷贝的是完整 Python 文件，不要把 Markdown 代码围栏一同粘贴进去。 |
| `ModuleNotFoundError: gradio` | 未激活项目 `.venv`，或尚未运行 `uv pip install -r requirements.txt`。 |
| `ModuleNotFoundError: mflux` / MLX 依赖问题 | 检查 `rapid-mlx[image]` 安装是否完整、是否在 Apple Silicon 原生 `arm64` 环境。 |
| WebUI 显示“无法连接 Rapid-MLX” | 终端 A 的模型服务没有启动、启动失败或监听端口与 `API_URL` 不一致。 |
| 7862 或 8000 端口被占用 | `lsof -nP -iTCP:7862 -sTCP:LISTEN` / 把端口换成 `8000` 检查。停止旧进程或改端口。 |
| 下载中断 | 重复 `hf download` 会复用已完成缓存；先检查磁盘空间/网络/下载超时。 |
| 加载或生成中内存不足 | 降到 `512×512 / 20 步`，关闭其他大模型、浏览器重负载进程；Mac 统一内存是系统共享的。 |
| `outputs/` 没有图片 | 查看 WebUI 提示和终端 A 错误日志；模型 API 成功返回图像后才会写入 PNG。 |
| 浏览器打不开 | 检查 `python app.py` 是否还在运行，并访问 `http://127.0.0.1:7862`。 |

诊断命令：

```bash
python --version
uname -m
rapid-mlx doctor
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:7862 -sTCP:LISTEN
memory_pressure
sysctl vm.swapusage
```

## 8. 上传到 GitHub（不上传模型和生成图）

在**项目根目录**执行下面的操作；上传前请仔细检查 `git status` 与 `git ls-files`，避免把本机路径、密钥、权重和个人图片公开。

```bash
# 如果原目录还没有初始化 Git 仓库
git init

# 检查会纳入仓库的文件
git status --short

git add app.py README.md README_EN.md requirements.txt .gitignore .gitattributes \
  THIRD_PARTY_NOTICES.md scripts/start_server.sh scripts/start_webui.sh outputs/.gitkeep

git status --short
git commit -m "Initial commit: Qwen Image 2.1 Mac WebUI"
git branch -M main
```

在 GitHub 网站新建一个**空仓库**（不要自动初始化 README），例如 `qwen-image-2.1-mac-webui`。再把下面的 `YOUR_USERNAME` 替换为自己的 GitHub 用户名：

```bash
git remote add origin https://github.com/YOUR_USERNAME/qwen-image-2.1-mac-webui.git
git push -u origin main
```

如已有 `origin`，先使用 `git remote -v` 检查，而不是重复执行 `git remote add origin`。GitHub HTTPS 推送需要按平台提示使用合适的身份认证（例如浏览器认证或 Personal Access Token），**不要把 Token 写在仓库文件中**。

### `.gitignore` 的作用

- `.venv/`、缓存及 Python 临时文件不会上传。
- `outputs/*` 不会上传（保留 `outputs/.gitkeep`）。
- `models/`、`*.safetensors`、`*.gguf` 等权重文件不会上传。
- `.env`、`.env.*`、常见密钥文件不会上传。
- 默认 Hugging Face 缓存本来就在项目目录之外。

`.gitignore` 只影响**尚未跟踪**的文件：如果此前已经 `git add` 过模型或敏感文件，应先取消跟踪；如果已经推送并泄露密钥，需要立即撤销/轮换密钥，并视情况清理 Git 历史。

## 9. 安全、版权与上游许可

- 默认仅监听本机 `127.0.0.1`，`share=False`；不要不经鉴权将本地 7862 / 8000 服务直接映射到公共互联网。
- 本仓库**不提供模型文件**，最终使用者需自行在 Hugging Face 下载量化模型，遵守上游许可及适用规定。
- 当前模型卡注明 Apache-2.0；仓库自己的 UI 源代码许可需要仓库所有者另行决定并添加 `LICENSE`。详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
- 如果打算通过 Cloudflare Tunnel 等方式向外提供服务，建议增加身份认证、访问速率限制及请求队列保护。

## 10. 官方参考

- [Qwen-Image-2.1-mflux-q4 · Hugging Face](https://huggingface.co/mlx-community/Qwen-Image-2.1-mflux-q4)
- [Qwen-Image-2.1 · Hugging Face](https://huggingface.co/Qwen/Qwen-Image-2.1)
- [Rapid-MLX · GitHub](https://github.com/raullenchai/Rapid-MLX)
- [Rapid-MLX Qwen Image family](https://rapidmlx.com/docs/models/families/qwen-image)
- [Hugging Face CLI / hf download](https://huggingface.co/docs/huggingface_hub/guides/cli)
- [uv 官方文档](https://docs.astral.sh/uv/)

---

*说明：本文记录当前项目架构及 Mac 运行方案。用户的实际生成成功结果说明其本机环境已能跑通基本流程；这里没有重新在另一台 Mac 上进行端到端的模型推理测试。*
