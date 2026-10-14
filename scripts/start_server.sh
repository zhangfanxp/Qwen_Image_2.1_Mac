#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  echo "[错误] 未找到 .venv。请先按 README 完成 uv 安装。" >&2
  exit 1
fi
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
cd "$ROOT_DIR"
echo "[Rapid-MLX] 启动 Qwen-Image-2.1: http://127.0.0.1:8000"
exec rapid-mlx serve qwen-image-2.1 --host 127.0.0.1 --port 8000
