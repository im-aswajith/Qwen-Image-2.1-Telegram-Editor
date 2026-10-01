import os
import sys
import subprocess
import time
import zipfile
import io
import json
from pathlib import Path

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
PROMPT = "YOUR-PROMPT"
STEPS = 15
CFG_SCALE = 6.0
WIDTH = 768
HEIGHT = 768
REF_MAX_DIM = 768

WORK_DIR = Path("/content/telegram_qwen_work")
WORK_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Qwen-Image-2.1 Uncensored GGUF Editor — Telegram Bot (Vulkan)")
print("=" * 60)

print("\n[0/7] Checking GPU...")
gpu_check = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
if gpu_check.returncode != 0:
    print("No GPU detected. Go to Runtime -> Change runtime type -> T4 GPU.")
    sys.exit(1)
print(gpu_check.stdout)

print("\n[1/7] Installing Vulkan runtime, NVIDIA ICD, and downloading sd-cli...")
subprocess.run(
    "apt-get update -qq && apt-get install -y -qq "
    "libvulkan1 vulkan-tools libglvnd0 libgl1 libglx0 libegl1 libgles2 "
    "libnvidia-gl-580",
    shell=True, check=True
)

nvidia_icd = {
    "file_format_version": "1.0.0",
    "ICD": {
        "library_path": "libGLX_nvidia.so.0",
        "api_version": "1.3.277"
    }
}
Path("/usr/share/vulkan/icd.d").mkdir(parents=True, exist_ok=True)
with open("/usr/share/vulkan/icd.d/nvidia_icd.json", "w") as f:
    json.dump(nvidia_icd, f, indent=2)

nvidia_egl = {
    "file_format_version": "1.0.0",
    "ICD": {
        "library_path": "libEGL_nvidia.so.0"
    }
}
Path("/usr/share/glvnd/egl_vendor.d").mkdir(parents=True, exist_ok=True)
with open("/usr/share/glvnd/egl_vendor.d/10_nvidia.json", "w") as f:
    json.dump(nvidia_egl, f, indent=2)

print("Verifying Vulkan devices...")
vk_check = subprocess.run(["vulkaninfo", "--summary"], capture_output=True, text=True)
print(vk_check.stdout[-2000:] if vk_check.stdout else "")
if vk_check.stderr:
    print(vk_check.stderr[-1000:])

import requests

api_url = "https://api.github.com/repos/leejet/stable-diffusion.cpp/releases/latest"
api_resp = requests.get(api_url)
api_resp.raise_for_status()
release = api_resp.json()

sd_url = None
for asset in release["assets"]:
    name = asset["name"]
    if "Linux" in name and "vulkan" in name.lower() and name.endswith(".zip"):
        sd_url = asset["browser_download_url"]
        print(f"Found release asset: {name}")
        break

if sd_url is None:
    raise RuntimeError("Could not find a Linux Vulkan asset in the latest release.")

r = requests.get(sd_url)
r.raise_for_status()
z = zipfile.ZipFile(io.BytesIO(r.content))

print("Archive contents:")
for n in z.namelist():
    print("   ", n)

EXTRACT_DIR = Path("/content/sd_bin")
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
z.extractall(EXTRACT_DIR)

all_files = {}
for root, dirs, files in os.walk(EXTRACT_DIR):
    for f in files:
        all_files[f] = Path(root) / f

SD_BIN = None
for preferred in ("sd-cli", "sd"):
    if preferred in all_files:
        SD_BIN = str(all_files[preferred])
        break

if SD_BIN is None:
    raise RuntimeError(
        "Could not find sd-cli in the archive. Available files: "
        + ", ".join(sorted(all_files.keys()))
    )

os.chmod(SD_BIN, 0o755)
print(f"Selected binary: {SD_BIN}")

so_dirs = set()
for root, dirs, files in os.walk(EXTRACT_DIR):
    for f in files:
        if f.endswith(".so") or ".so." in f:
            so_dirs.add(root)

ld_path = ":".join(so_dirs) if so_dirs else ""
env = os.environ.copy()
if ld_path:
    env["LD_LIBRARY_PATH"] = ld_path + ":" + env.get("LD_LIBRARY_PATH", "")
    print(f"LD_LIBRARY_PATH: {env['LD_LIBRARY_PATH']}")

print("\n[2/7] Installing Python dependencies...")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q",
     "huggingface_hub", "Pillow", "tqdm", "python-telegram-bot==21.6", "requests"],
    check=True
)

print("\n[3/7] Downloading models (cached)...")
from huggingface_hub import hf_hub_download

MODELS_DIR = Path("/content/qwen_image_models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

REPO_UNCENSORED = "abenzerps/Qwen-Image-2.1-Uncensored-GGUF"
diffusion = hf_hub_download(repo_id=REPO_UNCENSORED,
                            filename="qwen-image-2.1-UC-Q4_K_M.gguf",
                            local_dir=MODELS_DIR)
vae = hf_hub_download(repo_id=REPO_UNCENSORED,
                      filename="vae/qwen_image_2.1_vae_bf16.safetensors",
                      local_dir=MODELS_DIR)
print("Diffusion + VAE ready")

TEXT_ENCODER_REPO = "Qwen/Qwen3-VL-8B-Instruct-GGUF"
TEXT_ENCODER_FILE = "Qwen3VL-8B-Instruct-Q4_K_M.gguf"
VISION_FILE = "mmproj-Qwen3VL-8B-Instruct-F16.gguf"

try:
    text_encoder = hf_hub_download(repo_id=TEXT_ENCODER_REPO,
                                   filename=TEXT_ENCODER_FILE,
                                   local_dir=MODELS_DIR / "text_encoders")
except Exception:
    TEXT_ENCODER_REPO = "unsloth/Qwen3-VL-8B-Instruct-GGUF"
    text_encoder = hf_hub_download(repo_id=TEXT_ENCODER_REPO,
                                   filename=TEXT_ENCODER_FILE,
                                   local_dir=MODELS_DIR / "text_encoders")
vision_projector = hf_hub_download(repo_id=TEXT_ENCODER_REPO,
                                   filename=VISION_FILE,
                                   local_dir=MODELS_DIR / "text_encoders")
print("Text Encoder + Vision Projector ready")

from PIL import Image

def prepare_reference(input_path: Path, out_dir: Path) -> Path:
    img = Image.open(input_path).convert("RGB")
    orig_size = img.size
    if max(img.size) > REF_MAX_DIM:
        ratio = REF_MAX_DIM / max(img.size)
        new_w = max(16, int(img.size[0] * ratio) // 16 * 16)
        new_h = max(16, int(img.size[1] * ratio) // 16 * 16)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        ref_path = out_dir / "resized_ref.png"
        img.save(ref_path)
        print(f"Resized reference: {orig_size} -> {(new_w, new_h)}")
        return ref_path
    print(f"Using original: {orig_size}")
    return input_path

def run_edit(input_image: Path, output_image: Path) -> bool:
    ref = prepare_reference(input_image, WORK_DIR)

    cmd = [
        SD_BIN,
        "--diffusion-model", diffusion,
        "--vae", vae,
        "--llm", text_encoder,
        "--llm_vision", vision_projector,
        "-r", str(ref),
        "-p", PROMPT,
        "--steps", str(STEPS),
        "--cfg-scale", str(CFG_SCALE),
        "--sampling-method", "euler",
        "-W", str(WIDTH),
        "-H", str(HEIGHT),
        "--diffusion-fa",
        "--backend", "vulkan0",
        "--params-backend", "vulkan0",
        "-o", str(output_image),
        "-v",
    ]

    print("Running command:")
    print(" ".join(cmd))
    print()

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env=env
    )
    for line in iter(proc.stdout.readline, ''):
        print(line, end="")
    proc.wait()

    return proc.returncode == 0 and output_image.exists()

print("\n[4/7] Starting Telegram bot...")
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

HELP_TEXT = (
    "Qwen-Image-2.1 Editor Bot\n\n"
    "Send me a photo and I'll edit it using the uncensored Qwen-Image-2.1 model.\n\n"
    f"Current prompt: {PROMPT}\n"
    f"Output size: {WIDTH}x{HEIGHT} | Steps: {STEPS}\n\n"
    "Just send an image to begin. Send /start to see this again."
)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text("Received image. Downloading...")

    try:
        photo = update.message.photo[-1]
        tg_file = await context.bot.get_file(photo.file_id)

        user_dir = WORK_DIR / f"user_{chat_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        ts = int(time.time())
        input_path = user_dir / f"input_{ts}.jpg"
        output_path = user_dir / f"output_{ts}.png"

        await tg_file.download_to_drive(custom_path=str(input_path))

        await msg.edit_text("Generating edited image... (this takes ~1-2 min on T4)")

        ok = run_edit(input_path, output_path)

        if not ok or not output_path.exists():
            await msg.edit_text("Generation failed. Please try another image.")
            return

        await msg.edit_text("Uploading result...")
        with open(output_path, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption="Done! Send another image to edit again."
            )

        await msg.delete()

        try:
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            (user_dir / "resized_ref.png").unlink(missing_ok=True)
        except Exception:
            pass

    except Exception as e:
        print(f"[ERROR] {e}")
        try:
            await update.message.reply_text(f"Error: {e}")
        except Exception:
            pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please send a photo to edit (not text). Send /start for info."
    )

def main():
    print("\n[5/7] Bot is running - waiting for images...")
    print("=" * 60)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("[6/7] Polling started. Press Ctrl+C to stop.\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
