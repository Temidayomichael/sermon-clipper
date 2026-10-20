"""Step 6: render the vertical shorts with Remotion (captions, hook bar, graphics, zooms, SFX)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from .common import ASSETS, RENDER, job_dir, read_json, run, write_json
from .broll import CACHE, credits
from .common import config
from .sfx import ensure_default_music, ensure_sfx


def _link(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _srt(words: list[dict], path: Path) -> None:
    def t(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    lines, n = [], 1
    for i in range(0, len(words), 7):
        chunk = words[i:i + 7]
        lines += [str(n), f"{t(chunk[0]['start'])} --> {t(chunk[-1]['end'])}",
                  " ".join(w["w"] for w in chunk), ""]
        n += 1
    path.write_text("\n".join(lines))


def render(job: str, ids: list[str] | None = None) -> None:
    from .cut import cut

    d = job_dir(job)
    # Refresh captions/graphics/B-roll choices from the latest plan (fast; no re-cut).
    for i in ids or [None]:
        cut(job, i, retime=True)
    ensure_sfx()
    plan = {c["id"]: c for c in read_json(d / "plan.json")["clips"]}

    # Music: your tracks in assets/music/ (rotated across clips), else the built-in worship pad.
    mdir = ASSETS / "music"
    tracks = sorted(p for p in mdir.glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a")) if mdir.exists() else []
    music_files = []
    for n, t in enumerate(tracks):
        rel = f"music/track{n}{t.suffix.lower()}"
        _link(t, RENDER / "public" / rel)
        music_files.append(rel)
    if not music_files:
        music_files = [ensure_default_music()]

    # Your own B-roll for cutaways: assets/broll/<file> is available as visual "broll:<file>".
    bdir = ASSETS / "broll"
    for b in (bdir.glob("*") if bdir.exists() else []):
        if b.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm"):
            _link(b, RENDER / "public" / "broll" / b.name)

    # Logo for the end card (optional): assets/brand/logo.png
    logo = ASSETS / "brand" / "logo.png"
    if logo.exists():
        _link(logo, RENDER / "public" / "brand" / "logo.png")
    cfg = config()

    clip_dirs = sorted(p.parent for p in (d / "clips").glob("*/clip.json"))
    if ids:
        clip_dirs = [p for p in clip_dirs if any(p.name.startswith(i) for i in ids)]
    out_dir = d / "out"
    out_dir.mkdir(exist_ok=True)

    for n, cd in enumerate(clip_dirs):
        props = read_json(cd / "clip.json")
        rel = f"jobs/{job}/{props['id']}/cut.mp4"
        _link(cd / "cut.mp4", RENDER / "public" / rel)
        props["video"] = rel
        props["music"] = music_files[n % len(music_files)]
        # Stock footage: stage the cached clip and point the graphic at it.
        for g in props["graphics"]:
            st = g.get("stock") or {}
            if st.get("file") and (CACHE / st["file"]).exists():
                _link(CACHE / st["file"], RENDER / "public" / "broll" / st["file"])
                g["src"] = f"broll/{st['file']}"
                if g["type"] == "cutaway":
                    g["visual"] = f"broll:{st['file']}"
            g["look"] = cfg["broll_look"].get(g["type"], "natural")
        # Words behind the preacher: build person-only layers and stage them.
        from .embed import prepare as prepare_embeds
        prepare_embeds(cd, props)
        for g in props["graphics"]:
            if g.get("fgFile"):
                rel_fg = f"jobs/{job}/{props['id']}/fg/{g['fgFile']}"
                _link(cd / "fg" / g["fgFile"], RENDER / "public" / rel_fg)
                g["fgSrc"] = rel_fg
        p = cfg["preacher"]
        props["captionStyle"] = cfg["caption_style"]
        props["lowerThird"] = {"name": p.get("name", ""), "church": p.get("church", "")} if cfg["lower_third"] and p.get("name") else None
        ec = cfg["end_card"]
        props["endCard"] = {**ec, "logo": "brand/logo.png" if logo.exists() else None} if ec.get("enabled") else None
        props_file = cd / "props.json"
        write_json(props_file, props)

        out = out_dir / f"{props['id']}.mp4"
        print(f"\n🎬 Rendering {props['id']} ({props['duration']:.0f}s)")
        cmd = ["npx", "remotion", "render", "src/index.ts", "Short", str(out), f"--props={props_file}",
               "--log=error", f"--concurrency={max(2, (os.cpu_count() or 8) // 2)}", "--timeout=120000"]
        if cfg.get("output_4k"):
            cmd.insert(-2, "--scale=2")  # 2160x3840
        rng = os.environ.get("SERMON_CLIPPER_RANGE")  # "a-b" seconds: quick preview of part of a clip
        if rng:
            a, b = (float(x) for x in rng.split("-"))
            cmd.insert(-2, f"--frames={int(a * props['fps'])}-{int(b * props['fps'])}")
            out = out_dir / f"{props['id']}.preview.mp4"
            cmd[cmd.index(next(c for c in cmd if c.endswith(".mp4")))] = str(out)
        try:
            run(cmd, cwd=RENDER)
        except Exception:
            print("   render hiccup, retrying once with fewer parallel workers...")
            run(cmd[:-2] + ["--concurrency=2", "--timeout=240000"], cwd=RENDER)

        _srt(props["words"], out_dir / f"{props['id']}.srt")
        meta = plan.get(props["id"], {})
        (out_dir / f"{props['id']}.txt").write_text(
            f"TITLE:\n{meta.get('title', '')}\n\nCAPTION:\n{meta.get('caption', '')}\n"
            + (f"\nA/B TEST HOOK (render with this hook for the second post):\n{meta['hook_alt']}\n" if meta.get("hook_alt") else "")
            + (("\nB-ROLL CREDITS (add to the caption or description):\nVideo by " + "; ".join(credits(meta)) + "\n") if credits(meta) else "")
        )
        print(f"   ✓ {out}")
    print(f"\nDone. Finished videos, captions and post text are in {out_dir}")
