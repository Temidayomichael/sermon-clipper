"""Shared paths and helpers for the sermon clipper pipeline."""
from __future__ import annotations

import json
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
