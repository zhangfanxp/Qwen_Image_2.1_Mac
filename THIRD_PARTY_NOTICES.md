# Third-party software and model notices

This repository contains a small Gradio front end (`app.py`) that calls a locally running Rapid-MLX server. It does **not** contain or redistribute any model weights or code from the linked third-party projects.

| Component | Upstream project | Role |
| --- | --- | --- |
| Qwen-Image-2.1 (base model) | https://huggingface.co/Qwen/Qwen-Image-2.1 | Original image-generation model |
| Qwen-Image-2.1-mflux-q4 | https://huggingface.co/mlx-community/Qwen-Image-2.1-mflux-q4 | MLX/mflux quantized weights; model page lists Apache-2.0 |
| Rapid-MLX | https://github.com/raullenchai/Rapid-MLX | Apple Silicon inference server |
| Gradio | https://github.com/gradio-app/gradio | Web UI |
| MLX | https://github.com/ml-explore/mlx | Apple Silicon ML framework |

Please consult each upstream repository for license terms, model usage restrictions, and notices. Third-party licenses do not automatically establish a license for this repository's own application code; the repository owner should choose and add a `LICENSE` file before declaring their code open source.
