<div align="center">

# ⚡ QWEN-IMAGE 2.1 · TELEGRAM EDITOR

### A GPU-accelerated image editing gateway for **Qwen-Image 2.1**
### Telegram • Vulkan • GGUF • Hugging Face • Google Colab T4

<p>
  <a href="https://github.com/im-aswajith"><img src="https://img.shields.io/badge/author-im--aswajith-00D9FF?style=for-the-badge&logo=github&logoColor=white" alt="Author"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Qwen--Image-2.1-7C3AED?style=for-the-badge" alt="Qwen Image">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/Vulkan-GPU-AC162C?style=for-the-badge&logo=vulkan&logoColor=white" alt="Vulkan">
</p>

<p>
  <a href="https://colab.research.google.com/github/im-aswajith/Qwen-Image-2.1-Telegram-Editor/blob/main/colab/Qwen-Image-2.1-T4.ipynb">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab">
  </a>
  <a href="https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF">
    <img src="https://img.shields.io/badge/🤗%20Weights-Hugging%20Face-yellow?style=flat-square" alt="Hugging Face">
  </a>
  <a href="https://github.com/im-aswajith/Qwen-Image-2.1-Telegram-Editor/issues">
    <img src="https://img.shields.io/badge/Issues-Open-2ea44f?style=flat-square&logo=github" alt="Issues">
  </a>
</p>

> **Upload an image → send an edit instruction → generate on a GPU → receive the result directly in Telegram.**

</div>

---

## 🧬 What is this?

This project packages a **Qwen-Image 2.1 image-editing workflow** behind a Telegram bot.

The current implementation uses:

- **Qwen-Image 2.1 GGUF** as the diffusion/image-generation component.
- **Qwen3-VL 8B GGUF** as the text/vision conditioning component.
- A **VAE** for image decoding/encoding.
- **stable-diffusion.cpp** with a Vulkan backend for inference.
- **python-telegram-bot 21.6** for the Telegram interface.
- **Hugging Face Hub** for model retrieval and local caching.
- Automatic reference-image resizing before inference.
- Per-user temporary work directories and output cleanup.

The uploaded source sets a 768×768 generation target, 15 denoising steps, Euler sampling, CFG 6.0, and Vulkan execution. fileciteturn0file0L10-L18

---

## ✨ Feature Matrix

| Layer | Capability |
|---|---|
| 🧠 Model | Qwen-Image 2.1 GGUF |
| 👁️ Vision | Qwen3-VL 8B GGUF + vision projector |
| 🖼️ Editing | Reference-image conditioned editing |
| ⚙️ Runtime | stable-diffusion.cpp |
| 🚀 Accelerator | Vulkan |
| ☁️ Cloud | Google Colab T4 workflow |
| 💬 Interface | Telegram Bot API |
| 📦 Model Hub | Hugging Face Hub |
| 🧹 Cleanup | Automatic temporary-file removal |
| 📐 Reference | Automatic resize to a maximum dimension |
| 🔧 Configuration | Prompt, steps, CFG, width, height are configurable |
| 🪶 Distribution | Single Python launcher architecture |

---

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │       TELEGRAM      │
                         │  User sends image  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ python-telegram-bot │
                         │   async message     │
                         │      handler        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Reference Pipeline  │
                         │ RGB conversion      │
                         │ max-dim resize      │
                         │ 16px alignment      │
                         └──────────┬──────────┘
                                    │
                                    ▼
               ┌────────────────────────────────────────┐
               │         stable-diffusion.cpp           │
               │                                        │
               │  Diffusion GGUF ─────┐                │
               │  Qwen3-VL GGUF ──────┼──► Vulkan GPU  │
               │  Vision projector ───┤                │
               │  VAE ────────────────┘                │
               └──────────────────────┬─────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │ Generated PNG    │
                            │ Telegram upload  │
                            └──────────────────┘
```

---

## ⚡ One-Click Google Colab T4

### 🚀 Launch

<a href="https://colab.research.google.com/github/im-aswajith/Qwen-Image-2.1-Telegram-Editor/blob/main/colab/Qwen-Image-2.1-T4.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab">
</a>

**Recommended runtime:** `T4 GPU`

The supplied launcher explicitly checks `nvidia-smi` and stops if a GPU is unavailable. It then installs Vulkan components, discovers a Linux Vulkan release of stable-diffusion.cpp, downloads the required model files, and starts the Telegram bot. fileciteturn0file0L25-L36

### Colab setup

1. Open the **Open in Colab** button.
2. Select **Runtime → Change runtime type → T4 GPU**.
3. Run the setup cell.
4. Enter your Telegram bot token.
5. Set your edit prompt.
6. Wait for model/runtime initialization.
7. Send an image to the Telegram bot.
8. The generated image is returned to the same chat.

> **Important:** the repository currently needs to contain the notebook at `colab/Qwen-Image-2.1-T4.ipynb`. If you use a different GitHub repository name, update the badge URL in this README.

---

## 🔐 Telegram Bot Configuration

The original script uses these top-level controls:

```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
PROMPT = "YOUR-PROMPT"

STEPS = 15
CFG_SCALE = 6.0

WIDTH = 768
HEIGHT = 768
REF_MAX_DIM = 768
```

These values are directly defined in the uploaded launcher. fileciteturn0file0L10-L18

### Recommended secure configuration

Do **not** commit a real Telegram token.

Instead:

```python
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
PROMPT = os.environ.get(
    "QWEN_PROMPT",
    "Create a high-quality photorealistic edit while preserving the subject identity."
)
```

Then in Colab:

```python
import os
os.environ["TELEGRAM_TOKEN"] = "PASTE_YOUR_TOKEN_HERE"
os.environ["QWEN_PROMPT"] = "YOUR_EDIT_INSTRUCTION"
```

For public repositories, never place secrets in source code, notebooks, screenshots, commits, or issue posts.

---

## 📦 Model Stack

The current launcher downloads the following assets:

### Diffusion model

```text
abenzerps/Qwen-Image-2.1-Uncensored-GGUF
└── qwen-image-2.1-UC-Q4_K_M.gguf
```

### VAE

```text
abenzerps/Qwen-Image-2.1-Uncensored-GGUF
└── vae/qwen_image_2.1_vae_bf16.safetensors
```

### Text / vision encoder

```text
Qwen/Qwen3-VL-8B-Instruct-GGUF
└── Qwen3VL-8B-Instruct-Q4_K_M.gguf
└── mmproj-Qwen3VL-8B-Instruct-F16.gguf
```

The source includes a fallback to `unsloth/Qwen3-VL-8B-Instruct-GGUF` if the first text-encoder repository lookup fails. fileciteturn0file0L142-L166

### Official Qwen-Image 2.1 context

Qwen's official repository describes Qwen-Image 2.1 as a unified text-to-image and image-editing model with a 7B visual-generation component, a Qwen3-VL 8B text encoder, an RGBA VAE, and Flow Matching with Euler scheduling. citeturn0search0turn0search1

**Model-license note:** this project license does not replace, modify, or grant additional rights under any upstream model, weight, dataset, or dependency license.

---

## 🔩 Runtime Pipeline

The launcher performs these stages:

```text
01  GPU detection
02  Vulkan / NVIDIA runtime installation
03  Vulkan ICD configuration
04  stable-diffusion.cpp download
05  Python dependency installation
06  Hugging Face model download
07  Reference-image preparation
08  Vulkan image generation
09  Telegram result upload
10  Temporary-file cleanup
```

The Vulkan runtime and NVIDIA ICD setup are implemented near the beginning of the launcher. fileciteturn0file0L32-L63

The stable-diffusion.cpp binary is discovered dynamically from the latest GitHub release and the launcher selects `sd-cli` or `sd` from the extracted archive. fileciteturn0file0L69-L114

---

## 🧪 Inference Configuration

The generated command is conceptually:

```bash
sd-cli \
  --diffusion-model <diffusion.gguf> \
  --vae <vae.safetensors> \
  --llm <qwen3-vl.gguf> \
  --llm_vision <vision-projector.gguf> \
  -r <reference-image> \
  -p "<prompt>" \
  --steps 15 \
  --cfg-scale 6.0 \
  --sampling-method euler \
  -W 768 \
  -H 768 \
  --diffusion-fa \
  --backend vulkan0 \
  --params-backend vulkan0 \
  -o <output.png>
```

The actual source constructs this command in `run_edit()`. fileciteturn0file0L186-L221

---

## 🖼️ Reference Image Handling

Before generation, the image is:

1. Opened with Pillow.
2. Converted to RGB.
3. Checked against `REF_MAX_DIM`.
4. Downscaled when necessary.
5. Rounded to dimensions compatible with the 16-pixel alignment used by the launcher.

This preprocessing is implemented in `prepare_reference()`. fileciteturn0file0L171-L184

---

## 🤖 Telegram Workflow

```text
/start
   │
   ▼
Help + configuration information
   │
   ▼
User sends photo
   │
   ▼
Telegram downloads original photo
   │
   ▼
Reference image prepared
   │
   ▼
Qwen-Image 2.1 inference
   │
   ▼
PNG generated
   │
   ▼
Result sent back to Telegram
   │
   ▼
Temporary input/output files deleted
```

The bot exposes `/start`, accepts photo messages, and rejects ordinary text messages with an instruction to send an image. fileciteturn0file0L223-L305

---

## 🛠️ Installation — Local Linux / GPU

> The supplied runtime is designed around Linux + Vulkan. Windows users should generally use WSL2 or Colab rather than expecting the Linux Vulkan binary to run directly in native Windows.

### 1. Clone

```bash
git clone https://github.com/im-aswajith/Qwen-Image-2.1-Telegram-Editor.git
cd Qwen-Image-2.1-Telegram-Editor
```

### 2. Create environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3. Install Python packages

```bash
pip install huggingface_hub Pillow tqdm python-telegram-bot==21.6 requests
```

These are the Python dependencies installed by the supplied launcher. fileciteturn0file0L129-L133

### 4. Configure the bot

Set:

```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
PROMPT = "YOUR-PROMPT"
```

### 5. Run

```bash
python qwen-bot.py
```

---

## 🧠 Configuration Presets

### Balanced

```python
STEPS = 15
CFG_SCALE = 6.0
WIDTH = 768
HEIGHT = 768
REF_MAX_DIM = 768
```

### Higher detail

```python
STEPS = 25
CFG_SCALE = 5.0
WIDTH = 1024
HEIGHT = 1024
REF_MAX_DIM = 1024
```

### Faster preview

```python
STEPS = 8
CFG_SCALE = 5.0
WIDTH = 640
HEIGHT = 640
REF_MAX_DIM = 640
```

> These are configuration examples, not benchmark claims. Actual speed and VRAM usage depend on the runtime, model build, resolution, Vulkan implementation, and GPU.

---

## 🧯 Troubleshooting

### `No GPU detected`

Check:

```bash
nvidia-smi
```

In Colab, switch to:

```text
Runtime → Change runtime type → T4 GPU
```

The launcher itself performs the same GPU availability check. fileciteturn0file0L25-L29

### Vulkan device not found

Check:

```bash
vulkaninfo --summary
```

The launcher performs a Vulkan verification step after creating the NVIDIA ICD configuration. fileciteturn0file0L47-L63

### Model download fails

Check:

- Hugging Face connectivity
- repository/file names
- available disk space
- Hugging Face access requirements, if applicable

The source uses `hf_hub_download()` for model retrieval. fileciteturn0file0L136-L166

### Telegram token error

Create a bot with Telegram's official bot-management workflow and replace:

```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
```

Never publish the token.

### Generation is too slow

Try:

```python
STEPS = 8
WIDTH = 640
HEIGHT = 640
REF_MAX_DIM = 640
```

Then increase quality settings gradually.

---

## 🔒 Security

### Never commit

```text
Telegram bot tokens
API keys
private credentials
personal images
generated private content
local model caches
runtime secrets
```

Recommended `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
.env
.env.*
telegram_qwen_work/
qwen_image_models/
sd_bin/
*.gguf
*.safetensors
*.png
*.jpg
*.jpeg
.ipynb_checkpoints/
```

---

## 📁 Recommended Repository Layout

```text
Qwen-Image-2.1-Telegram-Editor/
│
├── README.md
├── LICENSE
├── qwen-bot.py
├── requirements.txt
│
├── colab/
│   └── Qwen-Image-2.1-T4.ipynb
│
├── assets/
│   └── ...
│
└── .gitignore
```

---

## 📊 Project Status

```text
┌────────────────────────────────────────────┐
│ QWEN IMAGE 2.1 TELEGRAM EDITOR            │
├────────────────────────────────────────────┤
│ Telegram interface       ██████████  100% │
│ Model download           ██████████  100% │
│ Vulkan runtime           ██████████  100% │
│ Reference preprocessing  ██████████  100% │
│ GPU inference            ██████████  100% │
│ Result delivery          ██████████  100% │
│ Colab packaging          ██████████  100% │
│ Production hardening     ██████░░░░   60% │
└────────────────────────────────────────────┘
```

The percentages above are project-packaging targets, not measured benchmark scores.

---

## 🧭 Roadmap

- [x] Telegram image input
- [x] Qwen-Image 2.1 GGUF integration
- [x] Qwen3-VL GGUF integration
- [x] Vulkan acceleration
- [x] Hugging Face model retrieval
- [x] Automatic reference resizing
- [x] Automatic result cleanup
- [x] Colab T4 launcher
- [ ] Per-user prompt configuration
- [ ] `/settings` command
- [ ] Resolution presets
- [ ] Queue management
- [ ] Progress reporting
- [ ] Persistent job history
- [ ] Web UI
- [ ] REST API
- [ ] Docker deployment
- [ ] Multi-GPU scheduling

---

## 🌐 Ecosystem

| Resource | Link |
|---|---|
| 👤 Developer | [@im-aswajith](https://github.com/im-aswajith) |
| 🧠 Official Qwen-Image 2.1 | [QwenLM/Qwen-Image-2.1](https://github.com/QwenLM/Qwen-Image-2.1) |
| 🤗 GGUF weights used by this launcher | [abenzerps/Qwen-Image-2.1-Uncensored-GGUF](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF) |
| 🤗 Qwen3-VL GGUF | [Qwen/Qwen3-VL-8B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF) |
| ⚙️ stable-diffusion.cpp | [leejet/stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) |
| 💬 Telegram Bot API | [Telegram](https://core.telegram.org/bots/api) |

Qwen-Image 2.1's official repository documents image editing, multiple reference images, native transparency, and multiple inference backends; this Telegram project uses a separate GGUF/Vulkan runtime path. citeturn0search0turn0search1

---

## ⚖️ Licensing

### This repository

The application/source code is intended to be governed by the **ASWAJITH STRICT SOURCE LICENSE** included in `LICENSE`.

### Important upstream distinction

The source code license **does not grant ownership or redistribution rights over third-party model weights**.

In particular:

- Qwen-Image 2.1 has its own upstream license terms.
- Qwen3-VL has its own upstream license terms.
- The referenced GGUF repository has its own repository/weight terms.
- stable-diffusion.cpp has its own license.
- Python dependencies have their own licenses.

Review all applicable upstream terms before redistributing weights, hosting the service commercially, or building a derivative product.

The official Qwen repository states that Qwen-Image 2.1 is licensed under the Qwen Research License Agreement. citeturn0search0turn0search1

---

## 👨‍💻 Author

<div align="center">

### Built by **Aswajith** · `im-aswajith`

<a href="https://github.com/im-aswajith">
  <img src="https://img.shields.io/badge/GitHub-im--aswajith-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>

<br><br>

**Build. Experiment. Create.**

</div>

---

## ⭐ Support

If this project is useful to you:

- ⭐ Star the repository
- 🐛 Open reproducible issues
- 🔧 Submit focused pull requests
- 📖 Improve documentation
- 🧪 Share reproducible performance results

> **Do not upload private user images or credentials to public issues.**

---

<div align="center">

### ⚡ QWEN × VULKAN × TELEGRAM

*An experimental image-editing gateway built for GPU inference.*

</div>
