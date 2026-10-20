"""Words behind the preacher: build a transparent "person only" layer for each embed window.

For every graphic {"type": "embed"} in a clip, we cut the window out of cut.mp4, segment the person
with Apple's built-in Vision person segmentation (tools/bin/personmask, compiled from tools/src),
and write a ProRes 4444 clip with alpha. The renderer stacks: video -> hero word -> this person layer,
so the word passes behind him. We also measure where his head is, so the word crosses it.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np

from .common import ROOT, run

BIN = ROOT / "tools" / "bin" / "personmask"
SRC = ROOT / "tools" / "src" / "personmask.swift"
PAD = 0.3  # seconds of person layer before and after the word's window


def ensure_tool() -> bool:
    """Compile the mask tool on first use (macOS + Xcode command line tools)."""
    if BIN.exists() and BIN.stat().st_mtime >= SRC.stat().st_mtime:
        return True
    if not shutil.which("swiftc"):
        print("   words-behind-preacher needs macOS with Xcode command line tools (xcode-select --install); skipping")
        return False
    BIN.parent.mkdir(parents=True, exist_ok=True)
    run(["swiftc", "-O", str(SRC), "-o", str(BIN)], stderr=subprocess.DEVNULL)
    return True


def build_layer(cut: Path, start: float, duration: float, out: Path, fps: int) -> dict:
    """Person-only layer for [start, start+duration] of cut.mp4. Returns layer timing and head position."""
    import cv2

    s0 = max(0.0, round((start - PAD) * fps) / fps)
    dur = duration + 2 * PAD
    work = out.with_suffix("")
    shutil.rmtree(work, ignore_errors=True)
    run([str(BIN), str(cut), f"{s0:.4f}", f"{dur:.4f}", str(work), "accurate"], stdout=subprocess.DEVNULL)
    masks = sorted(work.glob("*.png"))
    if not masks:
        raise RuntimeError("no masks produced")

    # Head position: top of the person in each mask, as a fraction of frame height (median = steady).
    tops, centers = [], []
    for m in masks[:: max(1, len(masks) // 12)]:
        a = cv2.imread(str(m), cv2.IMREAD_GRAYSCALE)
        rows = np.where((a > 128).sum(axis=1) > a.shape[1] * 0.01)[0]
        if len(rows):
            tops.append(rows[0] / a.shape[0])
            cols = np.where(a[rows[0]: rows[0] + max(1, a.shape[0] // 10)] > 128)[1]
            centers.append(float(cols.mean()) / a.shape[1] if len(cols) else 0.5)

    # Firm up the soft Vision edges a little, then merge as alpha onto the video window.
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", f"{s0:.4f}", "-t", f"{len(masks) / fps:.4f}", "-i", str(cut),
         "-framerate", str(fps), "-i", str(work / "%06d.png"),
         "-filter_complex",
         "[1:v]format=gray,lut=y='clip((val-50)*1.35,0,255)',gblur=sigma=0.8[a];[0:v][a]alphamerge,format=yuva444p10le[v]",
         "-map", "[v]", "-frames:v", str(len(masks)),
         "-c:v", "prores_ks", "-profile:v", "4444", "-an", str(out)])
    shutil.rmtree(work, ignore_errors=True)
    return {
        "fgFrom": round(s0, 4),
        "fgDuration": round(len(masks) / fps, 4),
        "headTop": round(float(np.median(tops)) if tops else 0.25, 4),
        "headX": round(float(np.median(centers)) if centers else 0.5, 4),
    }


def prepare(clip_dir: Path, props: dict) -> None:
    """Build (or reuse) person layers for every embed graphic in a clip's render props."""
    embeds = [g for g in props["graphics"] if g["type"] == "embed"]
    if not embeds or not ensure_tool():
        return
    cut = clip_dir / "cut.mp4"
    (clip_dir / "fg").mkdir(exist_ok=True)
    for g in embeds:
        out = clip_dir / "fg" / f"embed_{g['start']:.2f}.mov"
        meta = out.with_suffix(".json")
        import json
        if out.exists() and meta.exists() and out.stat().st_mtime >= cut.stat().st_mtime:
            info = json.loads(meta.read_text())
        else:
            print(f"   cutting out the preacher for '{g.get('text') or g.get('word')}' ...")
            info = build_layer(cut, g["start"], g["duration"], out, props["fps"])
            meta.write_text(json.dumps(info))
        g.update(info)
        g["fgFile"] = out.name
