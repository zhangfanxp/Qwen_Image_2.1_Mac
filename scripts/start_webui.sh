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
echo "[WebUI] 浏览器地址: http://127.0.0.1:7862"
exec python app.py
