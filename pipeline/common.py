"""Shared paths and helpers for the sermon clipper pipeline."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"
ASSETS = ROOT / "assets"
RENDER = ROOT / "render"
CONFIG_FILE = ROOT / "config.json"

DEFAULT_CONFIG = {
    # Who is preaching and who the clips are for. Fill this in config.json (kept out of git).
    "preacher": {
        "name": "",
        "church": "",
        "audience": "a general Christian audience",
        "region": "",
        "languages": "English",
    },
    # Extra spelling hints for transcription: names, places, local words the preacher uses.
    "vocab": "",
    "whisper_model": "mlx-community/whisper-large-v3-turbo",
    "language": "en",
    "claude_model": "opus",
    "fps": 30,
    # Gaps between words longer than this are shortened (seconds).
    "max_pause": 0.4,
    "pause_keep": 0.16,
    # Phrases cut out of clips wherever they appear.
    "filler_phrases": [
        "are you following me now",
        "are you following me",
        "are you still following me",
        "are you getting what i'm trying to say",
        "are you with me",
        "are you still with me",
        "are you listening to me",
        "do you understand what i'm saying",
        "is that clear",
        "is that okay",
    ],
    # Grade: target average brightness (0-255 luma) and base look.
    "grade": {"target_luma": 112, "contrast": 1.06, "saturation": 1.12},
    # Brand colours used by the motion graphics.
    "brand": {"accent": "#FFD43B", "panel": "rgba(10,10,14,0.82)", "text": "#FFFFFF"},
    "music_volume": 0.3,
    "sfx_volume": 0.5,
    # Caption look: "bold" (heavy uppercase, TikTok style) or "editorial" (clean words, gold italic key words).
    "caption_style": "bold",
    # Stock B-roll looks: "duotone" (navy/gold, like the illustrations) or "natural" (lightly graded).
    "broll_look": {"cutaway": "duotone", "insert": "natural", "split": "natural"},
    # Name tag a few seconds in (uses preacher name/church) and closing card. Logo: assets/brand/logo.png.
    "lower_third": True,
    "end_card": {"enabled": True, "title": "Watch the full message", "subtitle": "on YouTube", "handle": "", "seconds": 2.2},
    # Video clean-up before upscaling: "auto" (strong for sources under 720p, light otherwise), "light", "strong", "off".
    "clean": "auto",
    # AI upscaling (Real-ESRGAN) of the visible strip: "off", "ai" (always), "auto" (only for sources under 720p).
    # Slow: roughly 30-35 minutes per minute of finished clip on an M3 Pro. upscale_mix blends AI with regular
    # upscaling (1.0 = pure AI; lower keeps faces more natural).
    "upscale": "off",
    "upscale_mix": 0.75,
    # Render finished clips at 2160x3840 (4K) instead of 1080x1920. Helps YouTube quality; slower, bigger files.
    "output_4k": False,
    # Free key from https://www.pexels.com/api/ (or set PEXELS_API_KEY).
    "pexels_api_key": "",
    "pixabay_api_key": "",
}


def config() -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if CONFIG_FILE.exists():
        user = json.loads(CONFIG_FILE.read_text())
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    if os.environ.get("SERMON_CLIPPER_4K"):
        cfg["output_4k"] = True
    if os.environ.get("SERMON_CLIPPER_AI_UPSCALE"):
        cfg["upscale"] = "ai"
    return cfg


def job_dir(job: str) -> Path:
    d = JOBS / job
    if not d.exists():
        raise SystemExit(f"No job named '{job}'. Run: ./clip ingest <url-or-file> first.")
    return d


def slugify(text: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].strip("-") or "sermon"


def ts(sec: float) -> str:
    """Seconds -> H:MM:SS.s"""
    sec = max(0.0, sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}" if h else f"{int(m)}:{s:04.1f}"


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kw)


def read_json(p: Path):
    return json.loads(p.read_text())


def write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))
