"""Optional AI upscaling with Real-ESRGAN (realesrgan-x4plus), for low-resolution sources.

AI upscaling is slow (~3.4 s per 640x360 frame on an M3 Pro GPU), so only the strip of each frame that
the vertical crop actually shows (around the tracked face) is AI-upscaled. The rest of the frame - only
seen blurred or in full-frame slide moments - is upscaled with Lanczos. The AI strip is blended with the
Lanczos result (`upscale_mix`) and feathered at its edges, which keeps faces natural rather than waxy.

Install once: download realesrgan-ncnn-vulkan (macOS build) from
https://github.com/xinntao/Real-ESRGAN/releases into tools/realesrgan/.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

from .common import ROOT

BIN = ROOT / "tools" / "realesrgan" / "realesrgan-ncnn-vulkan"
MODEL = "realesrgan-x4plus"
SECONDS_PER_FRAME_FULL = 3.4  # measured on an M3 Pro for a 640x360 frame


def available() -> bool:
    return BIN.exists()


def _keys_at(keys: list[dict], t: float) -> dict:
    k = keys[0]
    for c in keys:
        if c["t"] <= t:
            k = c
        else:
            break
    return k


def ai_upscale(lowres: Path, keys: list[dict], out: Path, vfilters: str, fps: int,
               size: tuple[int, int] = (1920, 1080), mix: float = 0.75, strip: float = 0.44) -> None:
    """lowres: concatenated clip at source resolution (with final audio). keys: face track on lowres.
    Writes `out` at `size`, with `vfilters` (post-clean + grade) applied, audio copied from lowres."""
    import cv2

    work = out.parent / "upscale_work"
    shutil.rmtree(work, ignore_errors=True)
    src_dir, strip_dir, up_dir = work / "frames", work / "strips", work / "up"
    for p in (src_dir, strip_dir, up_dir):
        p.mkdir(parents=True)

    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(lowres), "-fps_mode", "passthrough",
                    str(src_dir / "%06d.png")], check=True)
    frames = sorted(src_dir.glob("*.png"))
    h, w = cv2.imread(str(frames[0])).shape[:2]
    sw = int(w * strip) // 2 * 2

    # 1. Cut the strip each frame will actually show (skip full-frame slide moments).
    x0s = {}
    for i, f in enumerate(frames):
        k = _keys_at(keys, i / fps)
        if k.get("fit"):
            continue
        x0 = int(min(max(0, k["x"] * w - sw / 2), w - sw))
        cv2.imwrite(str(strip_dir / f.name), cv2.imread(str(f))[:, x0:x0 + sw])
        x0s[f.name] = x0
    n = len(x0s)
    est = n * SECONDS_PER_FRAME_FULL * strip
    print(f"   AI upscaling {n} frames (strip {sw}px of {w}px), roughly {est / 60:.0f} min...")

    # 2. Real-ESRGAN on the strips, with a simple progress readout.
    t0 = time.time()
    proc = subprocess.Popen([str(BIN), "-i", str(strip_dir), "-o", str(up_dir), "-n", MODEL, "-s", "4", "-f", "png"],
                            cwd=BIN.parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while proc.poll() is None:
        time.sleep(15)
        done = len(list(up_dir.glob("*.png")))
        if done:
            left = (time.time() - t0) / done * (n - done)
            print(f"   ... {done}/{n} frames, ~{left / 60:.0f} min left", flush=True)
    if proc.returncode != 0:
        raise SystemExit("Real-ESRGAN failed. Check tools/realesrgan/ is installed (see pipeline/upscale.py).")

    # 3. Compose: Lanczos full frame + blended, feathered AI strip; pipe to ffmpeg with grade + audio.
    W, H = size
    scale = H / h
    pw = int(round(sw * scale))
    feather = max(8, pw // 14)
    ramp = np.ones(pw, np.float32)
    ramp[:feather] = np.linspace(0, 1, feather)
    ramp[-feather:] = np.linspace(1, 0, feather)
    alpha = (ramp * mix)[None, :, None]

    enc = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
         "-i", str(lowres), "-map", "0:v", "-map", "1:a",
         "-vf", f"{vfilters},format=yuv420p" if vfilters else "format=yuv420p",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    ox = (W - int(round(w * scale))) // 2
    for f in frames:
        base_small = cv2.imread(str(f))
        base = np.zeros((H, W, 3), np.uint8)
        bw = int(round(w * scale))
        base[:, ox:ox + bw] = cv2.resize(base_small, (bw, H), interpolation=cv2.INTER_LANCZOS4)
        if f.name in x0s and (up_dir / f.name).exists():
            up = cv2.resize(cv2.imread(str(up_dir / f.name)), (pw, H), interpolation=cv2.INTER_AREA).astype(np.float32)
            px = ox + int(round(x0s[f.name] * scale))
            region = base[:, px:px + pw].astype(np.float32)
            base[:, px:px + pw] = (region * (1 - alpha) + up * alpha).clip(0, 255).astype(np.uint8)
        enc.stdin.write(base.tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise SystemExit("Encoding the upscaled clip failed.")
    shutil.rmtree(work, ignore_errors=True)
