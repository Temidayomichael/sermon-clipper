"""Step 4: storyboard + review page.

Shows every proposed clip as a storyboard (one phone-shaped frame per beat), the edited transcript with
removed parts struck through, editable hooks/graphics, notes and a status per clip. Saves into plan.json.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .common import RENDER, ROOT, config, job_dir, read_json, write_json

def _illustration_names() -> list[str]:
    """Illustration names registered in render/src/components/illustrations/index.tsx (minus the placeholder)."""
    src = (RENDER / "src" / "components" / "illustrations" / "index.tsx").read_text()
    return [n for n in re.findall(r"^\s+(\w+): \w+,", src, re.M) if n != "glow"]


ILLUSTRATION_NAMES = _illustration_names()


def storyboard_data(job: str) -> dict:
    """Beats, edited transcript and estimated length for every clip in the plan."""
    from .cut import keep_segments, norm

    cfg = config()
    d = job_dir(job)
    plan = read_json(d / "plan.json")
    words = read_json(d / "transcript.json")["words"]
    out = []
    for c in plan["clips"]:
        segs = keep_segments(words, c["start"], c["end"], cfg, c.get("trims"))
        trims = c.get("trims") or []
        hl = {norm(w) for w in c.get("highlight_words", [])}
        fixes = {norm(k): v for k, v in c.get("caption_fixes", {}).items()}
        ws = []
        for w in words:
            if w["start"] < c["start"] - 0.05 or w["end"] > c["end"] + 0.05:
                continue
            kept = any(a - 0.01 <= w["start"] < b for a, b in segs)
            trimmed = any(a - 0.05 <= w["start"] and w["end"] <= b + 0.05 for a, b in trims)
            text = fixes.get(norm(w["w"]), w["w"])
            if not norm(text) and text != w["w"]:
                continue
            ws.append({"w": text, "t": w["start"], "kept": kept, "trimmed": trimmed, "hl": norm(text) in hl})

        beats = [{"t": c["start"], "kind": "hook"}]
        for i, g in enumerate(c.get("graphics", [])):
            beats.append({"t": max(g["at"], c["start"] + 0.1), "kind": g["type"], "g": i})
        beats.sort(key=lambda b: b["t"])
        for i, b in enumerate(beats):
            end = beats[i + 1]["t"] if i + 1 < len(beats) else c["end"]
            b["words"] = " ".join(x["w"] for x in ws if x["kept"] and b["t"] - 0.05 <= x["t"] < end)[:220]
        out.append({
            "id": c["id"],
            "est": round(sum(b - a for a, b in segs), 1),
            "raw": round(c["end"] - c["start"], 1),
            "words": ws,
            "beats": beats,
        })
    from .broll import api_key
    return {"clips": out, "illustrations": _illustration_names(), "pexels": bool(api_key())}


def thumb(job: str, t: float) -> Path:
    """A 9:16 frame of the source at time t, cropped around the biggest face (cached)."""
    import cv2

    d = job_dir(job) / "thumbs"
    d.mkdir(exist_ok=True)
    out = d / f"{t:.1f}.jpg"
    if out.exists():
        return out
    raw = d / f"{t:.1f}_raw.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(job_dir(job) / "source.mp4"),
                    "-frames:v", "1", str(raw)], check=True)
    img = cv2.imread(str(raw))
    raw.unlink(missing_ok=True)
    h, w = img.shape[:2]
    cx = w / 2
    model = ROOT / "assets" / "models" / "face_detection_yunet_2023mar.onnx"
    if model.exists():
        det = cv2.FaceDetectorYN.create(str(model), "", (w, h), 0.6)
        _, faces = det.detect(img)
        if faces is not None and len(faces):
            f = max(faces, key=lambda r: r[2] * r[3] * r[14])
            cx = f[0] + f[2] / 2
    cw = int(h * 9 / 16)
    x0 = int(min(max(0, cx - cw / 2), w - cw))
    crop = cv2.resize(img[:, x0:x0 + cw], (360, 640), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(str(out), crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return out


def illustration(name: str) -> Path:
    """A still of an illustration (rendered once with Remotion, then cached)."""
    out = RENDER / "out" / "illustrations" / f"{name}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npx", "remotion", "still", "src/index.ts", "Illustration", str(out), "--frame=75",
                        f"--props={json.dumps({'name': name})}", "--scale=0.34", "--log=error"], cwd=RENDER, check=True)
    return out


def review(job: str, port: int = 8765) -> None:
    d = job_dir(job)
    plan_file = d / "plan.json"
    if not plan_file.exists():
        raise SystemExit(f"No plan yet. Run: ./clip plan {job}")
    page = (ROOT / "pipeline" / "review.html").read_text()
    video = d / "source.mp4"

    from .broll import api_key, resolve_job
    if api_key():
        print("Finding stock B-roll for the storyboard...")
        try:
            resolve_job(job)
        except SystemExit as e:
            print(f"  B-roll skipped: {e}")
    print("Preparing illustration previews (first time only)...")
    for n in _illustration_names() + ["glow"]:
        illustration(n)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            try:
                if path in ("/", "/index.html"):
                    self._send(200, "text/html; charset=utf-8", page.replace("__JOB__", job).encode())
                elif path == "/plan.json":
                    self._send(200, "application/json", plan_file.read_bytes())
                elif path == "/storyboard.json":
                    self._send(200, "application/json", json.dumps(storyboard_data(job)).encode())
                elif path.startswith("/thumb/"):
                    t = float(path[len("/thumb/"):].removesuffix(".jpg"))
                    self._send(200, "image/jpeg", thumb(job, t).read_bytes(), cache=True)
                elif path.startswith("/illus/"):
                    name = path[len("/illus/"):].removesuffix(".png")
                    if name not in _illustration_names() + ["glow"]:
                        return self._send(404, "text/plain", b"not found")
                    self._send(200, "image/png", illustration(name).read_bytes(), cache=True)
                elif path.startswith("/source.mp4"):
                    self._video()
                else:
                    self._send(404, "text/plain", b"not found")
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_POST(self):
            if self.path in ("/broll/next", "/broll/find"):
                from .broll import next_clip, resolve_job
                n = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(n) or b"{}")
                try:
                    if self.path == "/broll/next":
                        next_clip(job, body["clip"], int(body["g"]))
                    else:
                        resolve_job(job)
                    res = {"ok": True}
                except SystemExit as e:
                    res = {"ok": False, "error": str(e)}
                except Exception as e:  # network trouble etc.
                    res = {"ok": False, "error": f"B-roll search failed: {e}"}
                return self._send(200, "application/json", json.dumps(res).encode())
            if self.path != "/save":
                return self._send(404, "text/plain", b"not found")
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n))
            write_json(plan_file, data)
            approved = sum(1 for c in data["clips"] if c.get("approved"))
            self._send(200, "application/json", json.dumps({"ok": True, "approved": approved}).encode())

        def _video(self):
            size = os.path.getsize(video)
            rng = self.headers.get("Range")
            start, end = 0, size - 1
            if rng:
                m = re.match(r"bytes=(\d*)-(\d*)", rng)
                if m:
                    if m.group(1):
                        start = int(m.group(1))
                    if m.group(2):
                        end = int(m.group(2))
            end = min(end, start + 8 * 1024 * 1024, size - 1)
            self.send_response(206 if rng else 200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            if rng:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            with open(video, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(end - start + 1))

        def _send(self, code, ctype, body, cache=False):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            if cache:
                self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            self.wfile.write(body)

    url = f"http://localhost:{port}/"
    print(f"Storyboard: {url}\nReview each clip, edit, leave notes, set a status, press Save. Ctrl+C here when done.")
    print(f"Then tell Claude \"revise {job}\" to apply your notes, or run: ./clip make {job}")
    webbrowser.open(url)
    try:
        ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    except KeyboardInterrupt:
        clips = read_json(plan_file)["clips"]
        print(f"\nSaved. {sum(1 for c in clips if c.get('approved'))} clip(s) approved.")
