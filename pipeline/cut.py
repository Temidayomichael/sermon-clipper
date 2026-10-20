"""Step 5: cut, clean, grade and face-track each approved clip.

Produces jobs/<job>/clips/<id>/cut.mp4 (16:9, filler removed, graded, loudness-normalised)
and clip.json with captions, graphics, zooms and crop keyframes re-timed to the cut.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .common import ASSETS, config, job_dir, read_json, run, write_json

PUNCT = re.compile(r"[^\w']+")


def norm(w: str) -> str:
    return PUNCT.sub("", w.lower())


# ---------------------------------------------------------------- segments

def keep_segments(words: list[dict], start: float, end: float, cfg: dict,
                  trims: list[list[float]] | None = None) -> list[tuple[float, float]]:
    """Source (start, end) ranges to keep.

    Drops filler phrases, single-word stammers ("the the"), any `trims` ranges from the plan
    (tangents, repeats), and shortens pauses. Every boundary is snapped to the video frame grid so
    audio and video are cut at exactly the same instant (otherwise lip-sync drifts a little per cut).
    """
    fps = cfg["fps"]
    ws = [w for w in words if w["start"] >= start - 0.05 and w["end"] <= end + 0.05]
    if not ws:
        return [(start, end)]

    removed = set()
    tokens = [norm(w["w"]) for w in ws]
    for phrase in cfg["filler_phrases"]:
        p = phrase.split()
        for i in range(len(tokens) - len(p) + 1):
            if tokens[i:i + len(p)] == p:
                removed.update(range(i, i + len(p)))
    for i in range(len(ws) - 1):  # stammer: same word twice in a row, no punctuation, no real pause
        if tokens[i] and tokens[i] == tokens[i + 1] and ws[i]["w"][-1:].isalnum() \
                and ws[i + 1]["start"] - ws[i]["end"] < 0.4:
            removed.add(i)
    for a, b in trims or []:
        removed.update(i for i, w in enumerate(ws) if w["start"] >= a - 0.05 and w["end"] <= b + 0.05)

    half = cfg["pause_keep"] / 2
    segs: list[list[float]] = []
    prev = None
    for i, w in enumerate(ws):
        if i in removed:
            if prev is not None:
                segs[-1][1] = prev["end"] + 0.04
            prev = None  # force a split after removed words
            continue
        if prev is None:
            segs.append([max(start - 0.05, w["start"] - 0.06), w["end"]])
        elif w["start"] - prev["end"] > cfg["max_pause"]:
            segs[-1][1] = prev["end"] + half
            segs.append([w["start"] - half, w["end"]])
        else:
            segs[-1][1] = w["end"]
        prev = w
    if segs:
        segs[-1][1] = min(end, segs[-1][1] + 0.35)

    snapped = []
    for a, b in segs:
        a, b = round(a * fps) / fps, round(b * fps) / fps
        if snapped and a <= snapped[-1][1] + 1 / fps:  # touching pieces: merge
            snapped[-1] = (snapped[-1][0], b)
        elif b - a >= 0.2:
            snapped.append((a, b))
    return snapped


class Timeline:
    """Maps source times to times in the cut clip."""

    def __init__(self, segs: list[tuple[float, float]]):
        self.map = []
        t = 0.0
        for a, b in segs:
            self.map.append((a, b, t))
            t += b - a
        self.duration = t

    def __call__(self, src: float) -> float:
        for a, b, o in self.map:
            if src < a:
                return o  # inside a removed gap: jump to next kept part
            if src < b:
                return o + (src - a)
        return self.duration


# ---------------------------------------------------------------- grade

def measure_luma(src: Path, start: float, dur: float) -> float:
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-ss", str(start), "-t", str(dur), "-i", str(src),
         "-vf", "fps=1,scale=320:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
         "-f", "null", "-"],
        capture_output=True, text=True,
    )
    vals = [float(v) for v in re.findall(r"YAVG=([\d.]+)", r.stdout + r.stderr)]
    return sum(vals) / len(vals) if vals else 110.0


def grade_filter(luma: float, cfg: dict) -> str:
    g = cfg["grade"]
    # Lift dark footage with gamma (gentle), pull down hot footage slightly.
    gamma = max(0.85, min(1.45, (g["target_luma"] / max(luma, 30)) ** 0.6))
    parts = [f"eq=contrast={g['contrast']}:saturation={g['saturation']}:gamma={gamma:.3f}"]
    lut = ASSETS / "luts" / "look.cube"
    if lut.exists():
        parts.append(f"lut3d='{lut}'")
    parts.append("cas=0.55")  # contrast-adaptive sharpening: crisper than unsharp on upscaled footage
    return ",".join(parts)


AUDIO_CHAIN = (
    "highpass=f=80,lowpass=f=14000,afftdn=nf=-25,"
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,"
    "loudnorm=I=-14:TP=-1.5:LRA=11"
)


def source_height(src: Path) -> int:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height",
                        "-of", "csv=p=0", str(src)], capture_output=True, text=True)
    try:
        return int(r.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        return 1080


def clean_filters(height: int, mode: str) -> tuple[str, str]:
    """Clean-up chain: (before upscaling, after upscaling).

    Before: remove compression blocks and noise at the source's own resolution (cheaper and cleaner).
    After: remove colour banding the upscale reveals. Sharpening happens later in the grade.
    """
    if mode == "off":
        return "", ""
    strength = mode if mode in ("light", "strong") else ("strong" if height < 720 else "light")
    if strength == "strong":
        return "deblock=filter=strong:block=8,nlmeans=s=2.2:p=7:r=9", "deband=1thr=0.015:2thr=0.015:3thr=0.015:blur=1"
    return "hqdn3d=1.5:1.5:3:3", "deband=1thr=0.01:2thr=0.01:3thr=0.01:blur=1"


def render_cut(src: Path, segs: list[tuple[float, float]], out: Path, vgrade: str, fps: int,
               clean: tuple[str, str] = ("", ""), size: tuple[int, int] = (1920, 1080),
               ai: dict | None = None) -> None:
    """Cut by exact frame and sample counts so picture and sound can never drift apart.

    1. Extract the clip's region to an intermediate at constant fps with uncompressed audio.
    2. Cut each piece as frames [f0, f1) and samples [f0*spf, f1*spf): identical lengths, every time.
    """
    sr = 48000
    spf = sr // fps  # audio samples per video frame (1600 at 30 fps)
    s0 = max(0.0, round((segs[0][0] - 1.0) * fps) / fps)
    s1 = segs[-1][1] + 1.0
    out.parent.mkdir(parents=True, exist_ok=True)
    region = out.parent / "region.mkv"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{s0:.4f}", "-i", str(src),
         "-t", f"{s1 - s0:.4f}", "-vf", f"fps={fps}", "-af", f"aresample={sr}", "-ac", "2",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "10", "-c:a", "pcm_s16le", str(region)])

    fc = []
    for i, (a, b) in enumerate(segs):
        f0, f1 = round((a - s0) * fps), round((b - s0) * fps)
        fade = 0.012
        d = (f1 - f0) / fps
        fc.append(f"[0:v]trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim=start_sample={f0 * spf}:end_sample={f1 * spf},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d={fade},afade=t=out:st={max(0, d - fade):.4f}:d={fade}[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[vc][ac]")
    pre = f"{clean[0]}," if clean[0] else ""
    post = f"{clean[1]}," if clean[1] else ""
    w, h = size
    if ai:
        # AI path: concat at source resolution (cleaned), track the face there, AI-upscale the visible strip.
        from .upscale import ai_upscale
        lowres = out.parent / "lowres.mkv"
        fc.append(f"[vc]{pre}format=yuv420p[vout]" if pre else "[vc]format=yuv420p[vout]")
        fc.append(f"[ac]{AUDIO_CHAIN},aresample={sr}[aout]")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(region),
             "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "8", "-c:a", "pcm_s16le", str(lowres)])
        region.unlink(missing_ok=True)
        keys = face_track(lowres)
        ai_upscale(lowres, keys, out, f"{post}{vgrade}".rstrip(","), fps, size, ai.get("mix", 0.75))
        lowres.unlink(missing_ok=True)
        return
    fc.append(f"[vc]{pre}scale={w}:{h}:flags=lanczos:force_original_aspect_ratio=decrease,"
              f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,{post}{vgrade},format=yuv420p[vout]")
    fc.append(f"[ac]{AUDIO_CHAIN},aresample={sr}[aout]")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(region),
         "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(out)])
    region.unlink(missing_ok=True)


# ---------------------------------------------------------------- reframe

FACE_MODEL = ASSETS / "models" / "face_detection_yunet_2023mar.onnx"


def face_track(video: Path, sample_fps: float = 5.0) -> list[dict]:
    """Horizontal face position (0-1) over time for the 9:16 crop.

    Each key also carries `fit` (split-screen/slide moment: show the whole frame) and `cut`
    (the picture changed sharply - camera cut, fast pan or one of our edits: re-frame instantly
    instead of gliding across).
    """
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, round(fps / sample_fps))
    det = None

    raw, prev = [], None
    i = 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if i % step == 0:
            _, frame = cap.retrieve()
            h, w = frame.shape[:2]
            small = cv2.resize(frame, (640, round(640 * h / w)))
            if det is None:
                det = cv2.FaceDetectorYN.create(str(FACE_MODEL), "", (small.shape[1], small.shape[0]), 0.6)
            g0 = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            band = max(1, g0.shape[0] // 9)
            # Black bars top and bottom = picture-in-picture / slide layout: show the whole frame.
            boxed = bool(g0[:band].mean() < 22 and g0[-band:].mean() < 22)

            thumb = cv2.GaussianBlur(cv2.resize(g0, (64, 36)), (3, 3), 0).astype(float)
            cut = prev is not None and float(np.abs(thumb - prev).mean()) > 18
            prev = thumb

            x = None
            if not boxed:
                _, faces = det.detect(small)
                if faces is not None and len(faces):
                    # Biggest confident face = the preacher (ignores small faces in the audience/backdrop).
                    f = max(faces, key=lambda r: r[2] * r[3] * r[14])
                    if f[2] >= small.shape[1] * 0.03:
                        x = float((f[0] + f[2] / 2) / small.shape[1])
            raw.append((i / fps, x, boxed, bool(cut)))
        i += 1
    cap.release()

    # Split into shots at sharp picture changes; frame each shot on its own.
    shots, cur_shot = [], []
    for r in raw:
        if r[3] and cur_shot:
            shots.append(cur_shot)
            cur_shot = []
        cur_shot.append(r)
    if cur_shot:
        shots.append(cur_shot)

    keys, fit_state, flat, idx = [], False, [r for shot in shots for r in shot], 0
    prev_x = 0.5
    win = max(1, int(sample_fps * 0.6))
    for shot in shots:
        known = sorted(x for _, x, _, _ in shot if x is not None)
        if not known:
            xs = [prev_x] * len(shot)
        elif known[int(0.9 * (len(known) - 1))] - known[int(0.1 * (len(known) - 1))] < 0.1:
            xs = [known[len(known) // 2]] * len(shot)  # he holds still: lock the frame, like a tripod
        else:
            # He (or the church camera) moves: rolling median + dead-zone, so we only re-frame for real moves.
            filled, cur = [], known[len(known) // 2]
            for _, x, _, _ in shot:
                cur = x if x is not None else cur
                filled.append(cur)
            xs, held = [], None
            for k in range(len(filled)):
                window = sorted(filled[max(0, k - win):k + win + 1])
                v = window[len(window) // 2]
                if held is None or abs(v - held) > 0.07:
                    held = v
                xs.append(held)
        prev_x = xs[-1]
        for k, (t, _, b, _) in enumerate(shot):
            # Debounce the layout flag: switch only when 2 samples agree, so one dark frame doesn't flip it.
            if b != fit_state and idx + 1 < len(flat) and flat[idx + 1][2] == b:
                fit_state = b
            keys.append({"t": round(t, 2), "x": round(xs[k], 4), "fit": fit_state, "cut": k == 0 and bool(keys)})
            idx += 1
    return keys or [{"t": 0, "x": 0.5, "fit": False, "cut": False}]


# ---------------------------------------------------------------- main

def apply_fixes(word: str, fixes: dict) -> str:
    key = norm(word)
    for wrong, right in fixes.items():
        if key == norm(wrong):
            m = re.match(r"^(\W*)(.*?)(\W*)$", word)
            return f"{m.group(1)}{right}{m.group(3)}"
    return word


def cut(job: str, only: str | None = None, retime: bool = False) -> list[str]:
    """Cut every approved clip. With retime=True, keep the existing cut video and face track and only
    refresh captions, graphics and zooms (fast: use after editing text or graphics in the review page)."""
    cfg = config()
    d = job_dir(job)
    plan = read_json(d / "plan.json")
    words = read_json(d / "transcript.json")["words"]
    src = d / "source.mp4"
    done = []

    for c in plan["clips"]:
        if not c.get("approved") or (only and not c["id"].startswith(only)):
            continue
        out_dir = d / "clips" / c["id"]
        print(f"\n✂  {c['id']}")
        segs = keep_segments(words, c["start"], c["end"], cfg, c.get("trims"))
        tl = Timeline(segs)
        print(f"   {len(segs)} pieces, {c['end'] - c['start']:.0f}s -> {tl.duration:.0f}s after removing pauses/filler")

        old = out_dir / "clip.json"
        if retime and (out_dir / "cut.mp4").exists() and old.exists():
            crop = read_json(old)["crop"]
            print("   retime only: reusing cut video and face track")
        else:
            luma = measure_luma(src, c["start"], c["end"] - c["start"])
            print(f"   brightness {luma:.0f}/255 -> grading")
            sh = source_height(src)
            clean = clean_filters(sh, cfg.get("clean", "auto"))
            size = (3840, 2160) if cfg.get("output_4k") else (1920, 1080)
            print(f"   source {sh}p -> clean-up: {'off' if not clean[0] else ('strong' if 'nlmeans' in clean[0] else 'light')}"
                  f"{', 4K intermediate' if size[0] == 3840 else ''}")
            from .upscale import available
            mode = cfg.get("upscale", "off")
            ai = {"mix": cfg.get("upscale_mix", 0.75)} if (mode == "ai" or (mode == "auto" and sh < 720)) and available() else None
            if mode in ("ai", "auto") and not available() and (mode == "ai" or sh < 720):
                print("   AI upscaling requested but Real-ESRGAN isn't installed (see pipeline/upscale.py); using regular upscaling")
            render_cut(src, segs, out_dir / "cut.mp4", grade_filter(luma, cfg), cfg["fps"], clean, size, ai)

            print("   tracking face for vertical crop")
            crop = face_track(out_dir / "cut.mp4")

        hl = {norm(w) for w in c.get("highlight_words", [])}
        fixes = c.get("caption_fixes", {})
        cap_words = []
        for w in words:
            if w["start"] < c["start"] - 0.05 or w["end"] > c["end"] + 0.05:
                continue
            if not any(a - 0.01 <= w["start"] < b for a, b in segs):
                continue
            text = apply_fixes(w["w"], fixes)
            if not norm(text):
                continue  # a caption fix mapped this word to "" (e.g. merging a mis-split name)
            cap_words.append({"w": text, "start": round(tl(w["start"]), 3),
                              "end": round(tl(w["end"]), 3), "hl": norm(text) in hl})

        # Animated highlights: first occurrence of each marked word gets a circle / box / underline.
        for m in c.get("marks", []):
            key = norm(m.get("word", ""))
            for cw in cap_words:
                if norm(cw["w"]) == key and "mark" not in cw:
                    cw["mark"] = m.get("style", "box")
                    break

        graphics = []
        for g in c.get("graphics", []):
            g2 = dict(g)
            g2["start"] = round(tl(g["at"]), 3)
            # Duration measured on the cut timeline, so trims inside a graphic shorten it to match.
            g2["duration"] = round(max(1.0, tl(g["at"] + float(g.get("duration", 4))) - g2["start"]), 3)
            if g.get("item_times"):
                g2["itemOffsets"] = [round(max(0.0, tl(x) - g2["start"]), 3) for x in g["item_times"]]
            g2.pop("at", None)
            g2.pop("item_times", None)
            graphics.append(g2)

        write_json(out_dir / "clip.json", {
            "id": c["id"],
            "hook": c["hook"],
            "duration": round(tl.duration, 3),
            "fps": cfg["fps"],
            "words": cap_words,
            "graphics": sorted(graphics, key=lambda g: g["start"]),
            "zooms": sorted(round(tl(z), 3) for z in c.get("zooms", [])),
            # Output times of internal edit points, for alternating jump-cut framing.
            "edits": [round(o, 3) for _, _, o in tl.map[1:]],
            "crop": crop,
            "brand": cfg["brand"],
            "sfxVolume": cfg["sfx_volume"],
            "musicVolume": cfg["music_volume"],
        })
        done.append(c["id"])
    if not done:
        print("No approved clips. Run ./clip review <job> and tick some first.")
    return done
