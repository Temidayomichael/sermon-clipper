"""Export a cut clip as a HyperFrames project (vertical short), following the HyperFrames contract.

  ./clip hf <job> <clip-id-prefix> [--project videos/<name>]

Inputs come from the pipeline (clips/<id>/clip.json + cut.mp4): word timings, face track, edits,
zooms and graphics. The generated videos/<name>/index.html is one paused, seek-safe GSAP timeline:

  a-roll (face-tracked 9:16 reframe, jump zooms, whip blur) -> hero word -> person cut-out
  -> vignette -> cutaway (illustration + kinetic words + light leak) -> cards -> hook bar
  -> name tag (registry: lt-kicker-name) -> captions (editorial, marker strokes from the registry's
  marker-highlight) -> end card -> grain (registry: grain-overlay) -> progress bar; music + SFX.

Registry items are installed with `npx hyperframes add` (telemetry disabled).
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from .common import RENDER, ROOT, config, job_dir, read_json, run

W, H = 1080, 1920
VIDEO_TOP = 330
BOX_H = H - VIDEO_TOP
VW0 = BOX_H * 16 / 9
END = 2.2
ACCENT = "#FFD43B"
NAVY, GOLD, CREAM, RED = "#14204A", "#E9B824", "#F7E9BC", "#D8262F"
ENV = {**os.environ, "HYPERFRAMES_NO_TELEMETRY": "1"}

# Hand-drawn strokes from the registry's marker-highlight component (same paths, same dash-draw method).
STROKES = {
    "circle": ("0 0 100 40", "M 22 7 C 58 1, 95 8, 97 20 C 99 31, 74 38, 44 37 C 16 36, 2 29, 3 19 C 4 10, 22 4, 52 4.5", 2.8),
    "underline": ("0 0 100 12", "M 2 7 C 20 4.5, 46 8.5, 66 6 C 80 4.5, 92 7.5, 98 5.5", 4.5),
    "box": ("0 0 100 40", "M 3 24 C 22 20.5, 47 25.5, 68 22.5 C 79 21, 90 23, 97 21.5", 26),
}


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def norm(w: str) -> str:
    return re.sub(r"[^\w']", "", w.lower())


def f3(x: float) -> str:
    return f"{x:.3f}"


# ---------------------------------------------------------------- assets

def _ffmpeg(*args: str) -> None:
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def prepare_assets(proj: Path, cd: Path, clip: dict) -> dict:
    a = proj / "assets"
    a.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cd / "cut.mp4", a / "sermon-clip.mp4")
    dur = clip["duration"]
    _ffmpeg("-sseof", "-0.6", "-i", str(cd / "cut.mp4"), "-update", "1", "-q:v", "2", str(a / "last-frame.jpg"))
    out = {"fg": {}, "cutaway": {}}

    # Person cut-out per hero word: transparent VP9 WebM (from the pipeline's Apple Vision person layer).
    from .embed import ensure_tool, build_layer
    for g in clip["graphics"]:
        if g["type"] == "embed" and ensure_tool():
            mov = cd / "fg" / f"embed_{g['start']:.2f}.mov"
            mov.parent.mkdir(exist_ok=True)
            info = build_layer(cd / "cut.mp4", g["start"], g["duration"], mov, clip["fps"])
            webm = a / f"person-{g['start']:.2f}.webm"
            _ffmpeg("-i", str(mov), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M", "-auto-alt-ref", "0", "-an", str(webm))
            out["fg"][g["start"]] = {**info, "file": f"assets/{webm.name}"}

    # Cutaways with real stock footage (Pexels, chosen by pipeline/broll.py): 9:16 cover crop, trimmed,
    # lightly graded so it sits with the sermon footage. Otherwise our Remotion illustration library.
    from .broll import CACHE
    out["stock"] = set()
    for g in clip["graphics"]:
        st = g.get("stock") or {}
        vis = str(g.get("visual", ""))
        src = CACHE / st["file"] if st.get("file") else ROOT / "assets" / "broll" / vis[6:] if vis.startswith("broll:") else None
        if g["type"] == "cutaway" and src and src.exists():
            mp4 = a / f"broll-{g['start']:.2f}.mp4"
            _ffmpeg("-i", str(src), "-t", f3(g["duration"] + 0.4), "-an",
                    "-vf", f"setpts=PTS/{float(g.get('stock_speed', 1))},"  # stock_speed: e.g. play a time-lapse whole
                           f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={clip['fps']},"
                           "eq=contrast=1.07:saturation=0.9:brightness=-0.02,tpad=stop_mode=clone:stop_duration=3,format=yuv420p",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(mp4))
            out["cutaway"][g["start"]] = f"assets/{mp4.name}"
            out["stock"].add(g["start"])
    for g in clip["graphics"]:
        if g["type"] == "cutaway" and g["start"] not in out["cutaway"] and not str(g.get("visual", "")).startswith(("stock:", "broll:", "new:")):
            name = g["visual"]
            mp4 = a / f"cutaway-{name}.mp4"
            run(["npx", "remotion", "render", "src/index.ts", "Illustration", str(mp4),
                 f"--props={json.dumps({'name': name, 'seconds': round(g['duration'] + 0.2, 2)})}", "--log=error"], cwd=RENDER)
            out["cutaway"][g["start"]] = f"assets/{mp4.name}"

    # Music bed looped to the full length; SFX.
    from .sfx import ensure_default_music, ensure_sfx
    ensure_sfx()
    pad = RENDER / "public" / ensure_default_music()
    _ffmpeg("-stream_loop", "-1", "-i", str(pad), "-t", f3(dur + END), "-af", f"afade=t=out:st={dur + END - 1.5:.2f}:d=1.5", str(a / "music.wav"))
    for n in ("whoosh", "pop", "hit", "tick"):
        shutil.copy2(RENDER / "public" / "sfx" / f"{n}.wav", a / f"sfx-{n}.wav")
    # Instrument Serif (OFL) is not in the renderer's bundled font list: ship the woff2 files with the project.
    fonts = a / "fonts"
    fonts.mkdir(exist_ok=True)
    for name, url in FONTS.items():
        cache = ROOT / "assets" / "fonts" / name
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            run(["curl", "-sfL", "-o", str(cache), url])
        shutil.copy2(cache, fonts / name)
    return out


FONTS = {
    "InstrumentSerif-Italic.woff2": "https://fonts.gstatic.com/s/instrumentserif/v5/jizHRFtNs2ka5fXjeivQ4LroWlx-6zAjjH7Motmp5g.woff2",
    "InstrumentSerif-Regular.woff2": "https://fonts.gstatic.com/s/instrumentserif/v5/jizBRFtNs2ka5fXjeivQ4LroWlx-6zUTjnTLgNs.woff2",
}


def ensure_registry(proj: Path) -> None:
    for name in ("lt-kicker-name", "organic-light-leak-overlay", "grain-overlay"):
        target = proj / ("compositions/components" if name == "grain-overlay" else "compositions") / f"{name}.html"
        if not target.exists():
            run(["npx", "--yes", "hyperframes", "add", name, "--dir", str(proj), "--no-clipboard", "--json"],
                stdout=subprocess.DEVNULL, env=ENV)


def adapt_lower_third(proj: Path, kicker: str, name: str, dur: float) -> str:
    """Copy the registry lt-kicker-name block to compositions/nametag.html: vertical canvas, our accent,
    real text, exit retimed to the window. The installed registry file stays pristine."""
    s = (proj / "compositions" / "lt-kicker-name.html").read_text()
    s = (s.replace("#46e5b7", ACCENT).replace("left: 130px;", "left: 60px;").replace("bottom: 122px;", "bottom: 250px;")
          .replace("font-size: 70px;", "font-size: 60px;")
          .replace("width: 1920px;\n        height: 1080px;", f"width: {W}px;\n        height: {H}px;")
          .replace('data-width="1920"', f'data-width="{W}"').replace('data-height="1080"', f'data-height="{H}"')
          .replace('data-duration="4.8"', f'data-duration="{dur:.2f}"')
          .replace("Episode 47", esc(kicker)).replace("Maya Chen", esc(name)))
    for old, off in (("4.25", 0.55), ("4.3", 0.5), ("4.32", 0.48), ("4.75", 0.05)):
        s = s.replace(f"}}, {old});", f"}}, {dur - off:.2f});")
    (proj / "compositions" / "nametag.html").write_text(s)
    return "compositions/nametag.html"


# ---------------------------------------------------------------- timing helpers

def paginate(words: list[dict], max_words: int = 4, max_chars: int = 22) -> list[dict]:
    pages, cur = [], []

    def flush():
        if cur:
            pages.append({"start": cur[0]["start"], "end": cur[-1]["end"], "words": list(cur)})
            cur.clear()

    for i, w in enumerate(words):
        chars = sum(len(x["w"]) + 1 for x in cur) + len(w["w"])
        if cur and (len(cur) >= max_words or chars > max_chars or w["start"] - words[i - 1]["end"] > 0.35):
            flush()
        cur.append(w)
        if w["w"][-1:] in ".!?" and len(cur) > 1:
            flush()
    flush()
    for i in range(len(pages) - 1):
        if pages[i + 1]["start"] - pages[i]["end"] < 0.6:
            pages[i]["end"] = pages[i + 1]["start"]
    return pages


def pan_x(fx: float) -> float:
    return min(0.0, max(W - VW0, W / 2 - fx * VW0))


# ---------------------------------------------------------------- composition

def build_html(clip: dict, assets: dict, hook: str, cfg: dict) -> str:
    dur = clip["duration"]
    total = dur + END
    words = clip["words"]
    graphics = clip["graphics"]
    cutaways = [g for g in graphics if g["type"] == "cutaway"]
    embeds = [g for g in graphics if g["type"] == "embed" and g["start"] in assets["fg"]]
    panels = [g for g in graphics if g["type"] in ("keyword", "list", "quote", "scripture")]
    pre = []   # GSAP setup lines (gsap.set)
    tl = []    # timeline lines
    body = []  # HTML

    def live_cutaway(t):
        return any(g["start"] <= t < g["start"] + g["duration"] for g in cutaways)

    # --- A-roll: band (blurred copy) + face-tracked frame. #zoom = jump level, #punch = punch-ins + intro.
    def frame_markup(prefix: str, video: str) -> str:
        return (f'<div class="frame" id="{prefix}frame"><div class="zoom" id="{prefix}zoom"><div class="punch" id="{prefix}punch">'
                f'<div class="pan" id="{prefix}pan">{video}</div></div></div></div>')

    body.append(f'<video id="band-video" class="clip band" src="assets/sermon-clip.mp4" muted playsinline data-start="0" data-duration="{f3(dur)}" data-track-index="1"></video>')
    aroll = (f'<video id="aroll" class="clip fill" src="assets/sermon-clip.mp4" playsinline data-has-audio="true" data-volume="1" '
             f'data-start="0" data-duration="{f3(dur)}" data-track-index="0"></video>'
             f'<img id="freeze" class="clip fill" src="assets/last-frame.jpg" alt="" data-start="{f3(dur)}" data-duration="{f3(END)}" data-track-index="0" />')
    body.append(frame_markup("a-", aroll))

    # Face track -> pan keyframes (instant at camera cuts, 0.5 s glide otherwise), mirrored on the person layer.
    targets = '["#a-pan"' + ''.join(f', "#p{i}-pan"' for i in range(len(embeds))) + "]"
    ztargets = '["#a-zoom"' + ''.join(f', "#p{i}-zoom"' for i in range(len(embeds))) + "]"
    ptargets = '["#a-punch"' + ''.join(f', "#p{i}-punch"' for i in range(len(embeds))) + "]"
    keys = clip["crop"]
    last = None
    for k in keys:
        x = round(pan_x(k["x"]), 1)
        if last is None:
            pre.append(f"gsap.set({targets}, {{ x: {x} }});")
        elif abs(x - last) > 0.5:
            if k.get("cut"):
                tl.append(f"tl.set({targets}, {{ x: {x} }}, {f3(k['t'])});")
            else:
                tl.append(f"tl.to({targets}, {{ x: {x}, duration: 0.5, ease: 'sine.inOut' }}, {f3(k['t'])});")
        last = x

    # Jump-cut framing: toggle 1.0 / 1.09 at edits at least 1.2 s apart, with a 0.1 s whip blur.
    level, last_toggle = 0, -10.0
    for e in clip.get("edits", []):
        if e - last_toggle >= 1.2 and e < dur:
            level ^= 1
            last_toggle = e
            tl.append(f"tl.set({ztargets}, {{ scale: {1.09 if level else 1} }}, {f3(e)});")
            tl.append(f"tl.fromTo('#a-frame', {{ filter: 'blur(7px)' }}, {{ filter: 'blur(0px)', duration: 0.1, ease: 'none', immediateRender: false }}, {f3(e)});")
    # Opening punch + emphasis punch-ins.
    pre.append(f"gsap.set({ptargets}, {{ scale: 1.16 }});")
    pre.append("gsap.set('#a-frame', { filter: 'blur(0px)' }); gsap.set('#flash', { opacity: 0 });")
    tl.append(f"tl.to({ptargets}, {{ scale: 1, duration: 0.45, ease: 'power3.out' }}, 0);")
    for z in clip["zooms"]:
        if z > 0.6 and not live_cutaway(z):
            tl.append(f"tl.to({ptargets}, {{ scale: 1.12, duration: 0.22, ease: 'power3.out' }}, {f3(z)});")
            tl.append(f"tl.to({ptargets}, {{ scale: 1, duration: 0.4, ease: 'power2.inOut' }}, {f3(z + 2.2)});")
    tl.append("tl.fromTo('#flash', { opacity: 0.55 }, { opacity: 0, duration: 0.12, ease: 'none', immediateRender: false }, 0);")

    # --- Hero word behind the preacher + person cut-out (HyperFrames embedded-captions craft rules).
    for i, g in enumerate(embeds):
        fg = assets["fg"][g["start"]]
        word = (g.get("text") or g["word"]).upper()
        size = int(min(H * 0.19, 1900 / max(3, len(word))))
        head_y = VIDEO_TOP + fg["headTop"] * BOX_H
        cy = head_y + BOX_H * 0.1
        letters = "".join(f'<span class="hl-ch">{esc(c) if c != " " else "&nbsp;"}</span>' for c in word)
        body.append(f'<div id="hero{i}" class="clip hero" data-start="{f3(g["start"])}" data-duration="{f3(g["duration"])}" data-track-index="5" '
                    f'style="top:{cy - size * 0.55:.0f}px;font-size:{size}px"><div class="hero-in" id="hero{i}-in">{letters}</div></div>')
        tl.append(f"tl.fromTo('#hero{i}-in .hl-ch', {{ yPercent: 45, scale: 0.7, opacity: 0 }}, {{ yPercent: 0, scale: 1, opacity: 1, duration: 0.32, ease: 'back.out(1.6)', stagger: 0.045 }}, {f3(g['start'])});")
        tl.append(f"tl.to('#hero{i}-in', {{ scale: 1.03, duration: {f3(max(0.3, g['duration'] - 0.6))}, ease: 'sine.inOut' }}, {f3(g['start'] + 0.3)});")
        tl.append(f"tl.to('#hero{i}-in', {{ opacity: 0, scale: 1.08, duration: 0.3, ease: 'power2.in' }}, {f3(g['start'] + g['duration'] - 0.3)});")
        person = (f'<video id="person{i}" class="clip fill" src="{fg["file"]}" muted playsinline '
                  f'data-start="{f3(fg["fgFrom"])}" data-duration="{f3(fg["fgDuration"])}" data-track-index="6"></video>')
        body.append(frame_markup(f"p{i}-", person).replace('class="frame"', 'class="frame person-frame"'))

    body.append('<div id="vignette"></div>')

    # --- Cutaways: illustration video + kinetic words + light leak (registry block) at the entry.
    for ci, g in enumerate(cutaways):
        src = assets["cutaway"].get(g["start"])
        if not src:
            continue
        s, d = g["start"], g["duration"]
        nxt = cutaways[ci + 1]["start"] if ci + 1 < len(cutaways) else None
        if nxt is not None and nxt < s + d:
            d = nxt - s
        # Back-to-back cutaways (a montage) hard-cut into each other instead of fading through the preacher.
        joined_prev = ci > 0 and s - (cutaways[ci - 1]["start"] + cutaways[ci - 1]["duration"]) < 0.12
        joined_next = nxt is not None and nxt - (s + d) < 0.12
        stock = s in assets["stock"]
        video = (f'<video id="cut{ci}-video" class="clip fill-canvas" src="{src}" muted playsinline '
                 f'data-start="{f3(s)}" data-duration="{f3(d)}" data-track-index="7"></video>')
        if stock:  # real footage: slow push-in on a wrapper + a grade gradient so the words read
            body.append(f'<div class="cutaway stock" id="cut{ci}"><div class="push" id="cut{ci}-push">{video}</div><div class="stock-shade"></div>')
            pre.append(f"gsap.set('#cut{ci}-push', {{ scale: 1.0 }});")
            tl.append(f"tl.to('#cut{ci}-push', {{ scale: 1.1, duration: {f3(d)}, ease: 'none' }}, {f3(s)});")
        else:
            body.append(f'<div class="cutaway" id="cut{ci}">{video}')
        inside = [w for w in words if s - 0.05 <= w["start"] < s + d]
        em = {norm(x) for x in g.get("emphasis", [])}
        key = norm(g.get("keyword", ""))
        lines, cur = [], []
        for w in inside:
            style = "key" if norm(w["w"]) == key else "serif" if norm(w["w"]) in em else "sans"
            if style == "key" and cur:
                lines.append(cur); cur = []
            cur.append((w, style))
            if style == "key" or len(cur) >= 3:
                lines.append(cur); cur = []
        if cur:
            lines.append(cur)
        for li, line in enumerate(lines):
            start = line[0][0]["start"]
            nxt_pair = (li // 2 + 1) * 2  # lines show in pairs (top, bottom) and flip together, so order reads top-down
            end = lines[nxt_pair][0][0]["start"] if nxt_pair < len(lines) else s + d
            spans = "".join(f'<span class="k-{st}" id="cut{ci}-l{li}-w{wi}">{esc(w["w"].rstrip(",;:."))}</span>' for wi, (w, st) in enumerate(line))
            base = 470 if not stock or g.get("text_pos") == "top" else 1180  # text_pos "top" keeps a low subject clear
            top = base + (li % 2) * (170 if stock else 230)
            body.append(f'<div class="kline clip" id="cut{ci}-l{li}" style="top:{top}px" data-start="{f3(start)}" data-duration="{f3(max(0.4, end - start))}" data-track-index="8">{spans}</div>')
            for wi, (w, st) in enumerate(line):
                tl.append(f"tl.fromTo('#cut{ci}-l{li}-w{wi}', {{ opacity: 0, y: 18, scale: {0.6 if st == 'key' else 1} }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.14, ease: 'power2.out' }}, {f3(w['start'] - 0.02)});")
        body.append("</div>")
        pre.append(f"gsap.set('#cut{ci}', {{ opacity: 0 }});")
        if joined_prev:
            tl.append(f"tl.set('#cut{ci}', {{ opacity: 1 }}, {f3(s)});")
        else:
            tl.append(f"tl.to('#cut{ci}', {{ opacity: 1, duration: 0.12, ease: 'none' }}, {f3(s)});")
            tl.append(f"tl.fromTo('#flash', {{ opacity: 0.8 }}, {{ opacity: 0, duration: 0.2, ease: 'none', immediateRender: false }}, {f3(s)});")
        if joined_next:
            tl.append(f"tl.set('#cut{ci}', {{ opacity: 0 }}, {f3(s + d)});")
        else:
            tl.append(f"tl.to('#cut{ci}', {{ opacity: 0, duration: 0.18, ease: 'none' }}, {f3(s + d - 0.18)});")
        if joined_prev:
            continue
        body.append(f'<div id="leak{ci}" data-composition-id="organic-light-leak-overlay" data-composition-src="compositions/organic-light-leak-overlay.html" '
                    f'data-start="{f3(max(0, s - 0.3))}" data-duration="1.2" data-track-index="9" data-width="{W}" data-height="{H}" class="overlay"></div>')

    # --- Panels: keyword slam, numbered list, quote, scripture.
    for pi, g in enumerate(panels):
        s, d = g["start"], g["duration"]
        if pi + 1 < len(panels):
            d = max(0.8, min(d, panels[pi + 1]["start"] - s - 0.05))
        pid = f"panel{pi}"
        if g["type"] == "keyword":
            body.append(f'<div id="{pid}" class="clip slam" data-start="{f3(s)}" data-duration="{f3(d)}" data-track-index="10"><div class="slam-in" id="{pid}-in">{esc(g["text"])}</div></div>')
            tl.append(f"tl.fromTo('#{pid}-in', {{ scale: 1.6, rotation: -6, opacity: 0 }}, {{ scale: 1, rotation: 0, opacity: 1, duration: 0.3, ease: 'back.out(1.8)' }}, {f3(s)});")
        else:
            if g["type"] == "list":
                inner = f'<div class="p-title">{esc(g["title"])}</div>' + "".join(
                    f'<div class="p-item" id="{pid}-i{ii}"><span class="p-num">{ii + 1}</span>{esc(item)}</div>' for ii, item in enumerate(g["items"]))
            elif g["type"] == "quote":
                inner = f'<div class="p-quote"><span class="p-qmark">“</span>{esc(g["text"])}</div>'
            else:
                inner = f'<div class="p-tag">SCRIPTURE</div><div class="p-title">{esc(g["ref"])}</div>' + (f'<div class="p-verse">“{esc(g["text"])}”</div>' if g.get("text") else "")
            body.append(f'<div id="{pid}" class="clip panel" data-start="{f3(s)}" data-duration="{f3(d)}" data-track-index="10"><div class="panel-in" id="{pid}-in">{inner}</div></div>')
            tl.append(f"tl.fromTo('#{pid}-in', {{ y: 80, scale: 0.92, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(1.4)' }}, {f3(s)});")
            if g["type"] == "list":
                offs = g.get("itemOffsets") or [0.25 + ii * (d * 0.6 / max(1, len(g["items"]))) for ii in range(len(g["items"]))]
                for ii, o in enumerate(offs):
                    tl.append(f"tl.fromTo('#{pid}-i{ii}', {{ x: -40, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.2, ease: 'power2.out' }}, {f3(s + o)});")
        tl.append(f"tl.to('#{pid}-in', {{ opacity: 0, duration: 0.3, ease: 'power2.in' }}, {f3(s + d - 0.3)});")

    # --- Hook bar (whole clip).
    hsize = 82 if len(hook) < 22 else 70 if len(hook) < 34 else 60
    body.append(f'<div id="hook" class="clip" data-start="0" data-duration="{f3(dur)}" data-track-index="11"><div id="hook-card" style="font-size:{hsize}px">'
                f'{esc(hook)}<div id="hook-line"></div></div></div>')
    tl.append("tl.fromTo('#hook-card', { scale: 0.85, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(1.6)' }, 0);")
    tl.append("tl.fromTo('#hook-line', { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: 'power4.out' }, 0.25);")

    # --- Name tag (registry lt-kicker-name), only while nothing else is on screen.
    p = cfg["preacher"]
    if cfg.get("lower_third", True) and p.get("name"):
        first = min([g["start"] for g in graphics if g["type"] != "embed"] + [dur])
        lt_end = min(4.6, first - 0.15)
        if lt_end - 0.9 >= 1.6:
            src = adapt_lower_third(PROJ, p.get("church", ""), p["name"], lt_end - 0.9)
            body.append(f'<div id="nametag" data-composition-id="lt-kicker-name" data-composition-src="{src}" '
                        f'data-start="0.9" data-duration="{f3(lt_end - 0.9)}" data-track-index="12" data-width="{W}" data-height="{H}" class="overlay"></div>')

    # --- Captions: editorial rail; hero words omitted (a word lives in one place); hidden in cutaways.
    omit = [(norm(g["word"]), g["start"], g["start"] + g["duration"]) for g in embeds]
    shown = [w for w in words if not any(norm(w["w"]) == ow and s0 - 0.4 <= w["start"] <= e0 for ow, s0, e0 in omit)]
    pages = [pg for pg in paginate(shown) if not live_cutaway((pg["start"] + pg["end"]) / 2)]
    cap = ['<div id="captions">']
    for pi_, pg in enumerate(pages):
        spans = []
        for wi, w in enumerate(pg["words"]):
            wid = f"c{pi_}w{wi}"
            text = esc(w["w"].rstrip(",;:"))
            cls = "c-serif" if w.get("hl") else "c-sans"
            mark = ""
            if w.get("mark") in STROKES:
                vb, d, sw = STROKES[w["mark"]]
                mark = (f'<svg class="mark mark-{w["mark"]}" viewBox="{vb}" preserveAspectRatio="none"><path id="{wid}-mark" d="{d}" '
                        f'fill="none" stroke="{ACCENT}" stroke-width="{sw}" stroke-linecap="round" /></svg>')
                tl.append(f"drawMark('#{wid}-mark', {f3(w['start'])});")
            spans.append(f'<span class="{cls}" id="{wid}">{mark}<span class="c-txt">{text}</span></span>')
            tl.append(f"tl.fromTo('#{wid}', {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.1, ease: 'power2.out' }}, {f3(w['start'] - 0.03)});")
        nxt = pages[pi_ + 1]["start"] - 0.03 if pi_ + 1 < len(pages) else dur
        end = min(pg["end"] + 0.05, nxt, dur)
        cap.append(f'<div class="cpage clip" id="cp{pi_}" data-start="{f3(pg["start"] - 0.03)}" data-duration="{f3(max(0.05, end - pg["start"] + 0.03))}" data-track-index="13">{"".join(spans)}</div>')
    cap.append("</div>")
    body.append("".join(cap))
    for g in embeds:  # captions step back while a hero word plays
        tl.append(f"tl.to('#captions', {{ opacity: 0.3, duration: 0.2 }}, {f3(g['start'])});")
        tl.append(f"tl.to('#captions', {{ opacity: 1, duration: 0.25 }}, {f3(g['start'] + g['duration'] - 0.25)});")

    # --- End card.
    ec = cfg.get("end_card", {})
    handle = ec.get("handle", "")
    body.append(f'<div id="endcard" class="clip" data-start="{f3(dur)}" data-duration="{f3(END)}" data-track-index="14"><div id="ec-dim"></div><div id="ec-in">'
                f'<div id="ec-title">{esc(ec.get("title", "Watch the full message"))}</div><div id="ec-sub">{esc(ec.get("subtitle", "on YouTube"))}</div>'
                f'<div id="ec-line"></div>' + (f'<div id="ec-handle">{esc(handle)}</div>' if handle else "") + "</div></div>")
    tl.append(f"tl.fromTo('#ec-dim', {{ opacity: 0 }}, {{ opacity: 0.86, duration: 0.35 }}, {f3(dur)});")
    tl.append(f"tl.fromTo('#ec-in', {{ scale: 0.85, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: 'back.out(1.5)' }}, {f3(dur + 0.12)});")
    tl.append(f"tl.fromTo('#ec-line', {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: 'power3.out' }}, {f3(dur + 0.3)});")
    tl.append(f"tl.to('#hook-card', {{ opacity: 0, duration: 0.25 }}, {f3(dur - 0.25)});")

    # --- Flash, grain (registry grain-overlay), progress.
    body.append('<div id="flash"></div>')
    grain = (ROOT_GRAIN_HTML or "")
    body.append(grain)
    body.append('<div id="progress"><div id="progress-bar"></div></div>')
    pre.append("gsap.set('#progress-bar', { scaleX: 0 });")
    tl.append(f"tl.to('#progress-bar', {{ scaleX: 1, duration: {f3(total)}, ease: 'none' }}, 0);")

    # --- Sound: music bed + SFX (the sermon audio stays on the a-roll video).
    sfx = [("hit", 0.0, 0.9)]
    for g in graphics:
        if g["type"] == "embed":
            sfx.append(("hit", max(0, g["start"] - 0.05), 1.0))
        elif g["type"] == "cutaway":
            ends = [x["start"] + x["duration"] for x in cutaways]
            starts = [x["start"] for x in cutaways]
            if any(abs(g["start"] - e) < 0.12 for e in ends):
                sfx.append(("tick", g["start"], 0.8))  # montage cut
            else:
                sfx.append(("whoosh", max(0, g["start"] - 0.2), 1.0))
            if not any(abs(g["start"] + g["duration"] - st) < 0.12 for st in starts):
                sfx.append(("whoosh", g["start"] + g["duration"] - 0.25, 0.6))
        elif g["type"] == "keyword":
            sfx.append(("hit", max(0, g["start"] - 0.12), 0.8))
        elif g["type"] in ("list", "quote", "scripture"):
            sfx.append(("whoosh", max(0, g["start"] - 0.12), 0.8))
            if g["type"] == "list":
                for o in g.get("itemOffsets") or []:
                    sfx.append(("tick", g["start"] + o, 0.7))
    for z in clip["zooms"]:
        sfx.append(("whoosh", max(0, z - 0.15), 0.45))
    last_pop = -10
    for w in words:
        if w.get("hl") and w["start"] - last_pop > 0.8:
            sfx.append(("pop", w["start"], 0.6)); last_pop = w["start"]
    sfx.append(("hit", dur, 0.7))
    vol = cfg.get("sfx_volume", 0.5)
    audio = [f'<audio id="music" src="assets/music.wav" data-start="0" data-duration="{f3(total)}" data-track-index="20" data-volume="{cfg.get("music_volume", 0.3) * 0.5:.2f}"></audio>']
    for i, (n, t, v) in enumerate(sorted(sfx, key=lambda x: x[1])):
        if t < total - 0.2:
            audio.append(f'<audio id="sfx{i}" src="assets/sfx-{n}.wav" data-start="{f3(t)}" data-duration="1.2" data-track-index="{21 + i % 4}" data-volume="{v * vol:.2f}"></audio>')

    return TEMPLATE.format(
        W=W, H=H, VT=VIDEO_TOP, BH=BOX_H, VW0=f"{VW0:.1f}", TOTAL=f3(total), ACCENT=ACCENT, NAVY=NAVY, GOLD=GOLD, CREAM=CREAM, RED=RED,
        BODY="\n      ".join(body), AUDIO="\n      ".join(audio), PRE="\n      ".join(pre), TL="\n      ".join(tl),
        GRAIN_CSS=GRAIN_CSS,
    )


ROOT_GRAIN_HTML = ""
GRAIN_CSS = ""
PROJ = ROOT


def load_grain(proj: Path) -> None:
    """Paste the registry grain-overlay component (HTML + CSS), softened for footage."""
    global ROOT_GRAIN_HTML, GRAIN_CSS
    s = (proj / "compositions" / "components" / "grain-overlay.html").read_text()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    css = re.search(r"<style>(.*?)</style>", s, re.S).group(1).replace("opacity: 0.15;", "opacity: 0.07;")
    ROOT_GRAIN_HTML = re.sub(r"<style>.*?</style>", "", s, flags=re.S).strip().replace("z-index: 100;", "z-index: 40;")
    GRAIN_CSS = css


TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Instrument Serif"; font-style: italic; font-weight: 400; src: url("assets/fonts/InstrumentSerif-Italic.woff2") format("woff2"); }}
      @font-face {{ font-family: "Instrument Serif"; font-style: normal; font-weight: 400; src: url("assets/fonts/InstrumentSerif-Regular.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #08090d; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #08090d; font-family: "Montserrat", sans-serif; }}
      .band {{ position: absolute; left: 50%; top: -200px; width: 1597px; height: 898px; margin-left: -798px; object-fit: cover; filter: blur(30px) brightness(0.35) saturate(1.3); }}
      .frame {{ position: absolute; left: 0; top: {VT}px; width: {W}px; height: {BH}px; overflow: hidden; }}
      .zoom, .punch {{ position: absolute; inset: 0; transform-origin: 50% 30%; }}
      .pan {{ position: absolute; left: 0; top: 0; width: {VW0}px; height: {BH}px; }}
      .fill {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .fill-canvas {{ position: absolute; inset: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #vignette {{ position: absolute; inset: 0; z-index: 8; background: linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.6) 100%); }}
      .person-frame {{ z-index: 6; }}
      .hero {{ position: absolute; left: 0; width: {W}px; z-index: 5; display: flex; justify-content: center; font-family: "League Gothic", sans-serif; color: {ACCENT}; line-height: 1; white-space: nowrap; }}
      .hero-in {{ display: flex; text-shadow: 0 8px 30px rgba(0,0,0,0.45); }}
      .hl-ch {{ display: inline-block; }}
      .cutaway {{ position: absolute; inset: 0; z-index: 9; }}
      .kline {{ position: absolute; left: 60px; right: 60px; display: flex; justify-content: center; align-items: baseline; gap: 26px; flex-wrap: wrap; top: 470px; }}
      .push {{ position: absolute; inset: 0; transform-origin: 50% 45%; }}
      .stock-shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.05) 50%, rgba(0,0,0,0.78) 100%); }}
      .stock .k-key {{ color: {ACCENT}; text-shadow: 0 10px 40px rgba(0,0,0,0.6); text-transform: uppercase; font-size: 170px; }}
      .k-sans {{ display: inline-block; font-family: "Montserrat", sans-serif; font-weight: 700; font-size: 84px; color: #fff; -webkit-text-stroke: 10px rgba(10,14,30,0.9); paint-order: stroke fill; text-shadow: 0 4px 18px rgba(0,0,0,0.55); }}
      .k-serif {{ display: inline-block; font-family: "Instrument Serif", serif; font-style: italic; font-size: 150px; color: {CREAM}; -webkit-text-stroke: 12px {NAVY}; paint-order: stroke fill; text-shadow: 0 6px 24px rgba(0,0,0,0.45); }}
      .k-key {{ display: inline-block; font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 190px; color: {RED}; text-shadow: 6px 8px 0 {NAVY}, 0 18px 40px rgba(0,0,0,0.5); text-transform: lowercase; }}
      .overlay {{ position: absolute; inset: 0; z-index: 10; pointer-events: none; }}
      .slam {{ position: absolute; left: 0; width: {W}px; top: 990px; z-index: 11; display: flex; justify-content: center; }}
      .slam-in {{ font-family: "League Gothic", sans-serif; font-size: 170px; line-height: 1; color: {ACCENT}; text-transform: uppercase; text-shadow: 0 0 2px #000, 0 10px 34px rgba(0,0,0,0.7); }}
      .panel {{ position: absolute; left: 70px; right: 70px; top: 960px; z-index: 11; }}
      .panel-in {{ background: rgba(10,10,14,0.85); border: 3px solid rgba(255,255,255,0.12); border-radius: 28px; padding: 30px 40px; color: #fff; box-shadow: 0 24px 60px rgba(0,0,0,0.5); }}
      .p-title {{ font-family: "League Gothic", sans-serif; font-size: 64px; color: {ACCENT}; text-transform: uppercase; margin-bottom: 12px; }}
      .p-item {{ display: flex; align-items: center; gap: 20px; font-weight: 700; font-size: 50px; margin: 10px 0; }}
      .p-num {{ width: 58px; height: 58px; border-radius: 14px; background: {ACCENT}; color: #111; display: flex; align-items: center; justify-content: center; font-family: "League Gothic", sans-serif; font-size: 40px; flex-shrink: 0; }}
      .p-quote {{ font-weight: 700; font-size: 50px; line-height: 1.22; }}
      .p-qmark {{ display: block; font-family: "Instrument Serif", serif; font-size: 110px; line-height: 0.6; height: 50px; color: {ACCENT}; }}
      .p-tag {{ display: inline-block; font-size: 24px; font-weight: 700; letter-spacing: 3px; background: rgba(255,255,255,0.12); padding: 6px 14px; border-radius: 8px; margin-bottom: 12px; }}
      .p-verse {{ font-family: "Instrument Serif", serif; font-style: italic; font-size: 46px; line-height: 1.3; margin-top: 10px; }}
      #hook {{ position: absolute; top: 150px; left: 60px; right: 60px; z-index: 12; display: flex; justify-content: center; }}
      #hook-card {{ position: relative; background: #fbfaf5; color: #0b0b0d; font-family: "League Gothic", sans-serif; line-height: 1.08; text-transform: uppercase; text-align: center; padding: 20px 34px 26px; border-radius: 22px; box-shadow: 0 18px 50px rgba(0,0,0,0.45); letter-spacing: 1px; }}
      #hook-line {{ position: absolute; left: 34px; right: 34px; bottom: 12px; height: 8px; border-radius: 4px; background: {ACCENT}; transform-origin: 0% 50%; }}
      #captions {{ position: absolute; inset: 0; z-index: 13; pointer-events: none; }}
      .cpage {{ position: absolute; top: 1370px; left: 60px; right: 60px; display: flex; flex-wrap: wrap; justify-content: center; align-items: baseline; gap: 0 20px; }}
      .c-sans, .c-serif {{ position: relative; display: inline-block; }}
      .c-sans .c-txt {{ position: relative; font-family: "Montserrat", sans-serif; font-weight: 700; font-size: 78px; line-height: 1.2; color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.9); }}
      .c-serif .c-txt {{ position: relative; font-family: "Instrument Serif", serif; font-style: italic; font-size: 118px; line-height: 1.05; color: {ACCENT}; text-shadow: 0 6px 22px rgba(0,0,0,0.6); }}
      .mark {{ position: absolute; overflow: visible; pointer-events: none; }}
      .mark-circle {{ left: -14%; top: -22%; width: 128%; height: 144%; }}
      .mark-underline {{ left: -4%; bottom: -16%; width: 108%; height: 30%; }}
      .mark-box {{ left: -8%; top: 6%; width: 116%; height: 92%; opacity: 0.85; }}
      #endcard {{ position: absolute; inset: 0; z-index: 30; }}
      #ec-dim {{ position: absolute; inset: 0; background: rgb(8,10,20); }}
      #ec-in {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 26px; }}
      #ec-title {{ font-family: "League Gothic", sans-serif; font-size: 110px; color: #fff; text-transform: uppercase; text-align: center; line-height: 1; padding: 0 60px; }}
      #ec-sub {{ font-family: "Instrument Serif", serif; font-style: italic; font-size: 88px; color: {ACCENT}; line-height: 1; }}
      #ec-line {{ width: 360px; height: 8px; border-radius: 4px; background: {ACCENT}; }}
      #ec-handle {{ font-weight: 700; font-size: 46px; color: #fff; }}
      #flash {{ position: absolute; inset: 0; z-index: 35; background: #fff; opacity: 0; pointer-events: none; }}
      #progress {{ position: absolute; left: 0; right: 0; top: 0; height: 10px; z-index: 45; background: rgba(255,255,255,0.18); }}
      #progress-bar {{ height: 100%; background: {ACCENT}; transform-origin: 0% 50%; }}
      {GRAIN_CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      {BODY}
      {AUDIO}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // Marker strokes (registry marker-highlight technique): dash-draw by getTotalLength.
      function drawMark(sel, at) {{
        const p = document.querySelector(sel);
        if (!p) return;
        const len = p.getTotalLength();
        gsap.set(p, {{ strokeDasharray: len, strokeDashoffset: len }});
        tl.to(p, {{ strokeDashoffset: 0, duration: 0.45, ease: "power2.inOut" }}, at);
      }}
      {PRE}
      {TL}
      tl.to({{}}, {{ duration: {TOTAL} }}, 0);
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def export(job: str, prefix: str, project: str | None = None) -> Path:
    cfg = config()
    d = job_dir(job)
    plan = {c["id"]: c for c in read_json(d / "plan.json")["clips"]}
    cd = next(p.parent for p in sorted((d / "clips").glob("*/clip.json")) if p.parent.name.startswith(prefix))
    clip = read_json(cd / "clip.json")
    meta = plan.get(clip["id"], {})
    proj = ROOT / (project or f"videos/{clip['id']}")
    if not (proj / "hyperframes.json").exists():
        proj.parent.mkdir(parents=True, exist_ok=True)
        run(["npx", "--yes", "hyperframes", "init", str(proj), "--non-interactive", "--example=blank", "--skill=general-video"],
            stdout=subprocess.DEVNULL, env=ENV)
    print(f"HyperFrames project: {proj}")
    global PROJ
    PROJ = proj
    ensure_registry(proj)
    load_grain(proj)
    print("   preparing assets (person cut-outs, illustration videos, music, SFX)...")
    assets = prepare_assets(proj, cd, clip)
    (proj / "index.html").write_text(build_html(clip, assets, meta.get("hook") or clip["hook"], cfg))
    print("   wrote index.html")
    return proj
