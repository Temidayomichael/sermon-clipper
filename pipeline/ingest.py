"""Step 1: bring a sermon into jobs/<job>/source.mp4 from a YouTube link or a local file."""
from __future__ import annotations

import shutil
from pathlib import Path

from .common import JOBS, run, slugify, write_json


def ingest(src: str, name: str | None = None, cookies_from: str | None = None) -> str:
    is_url = src.startswith("http://") or src.startswith("https://")

    if is_url:
        auth = ["--cookies-from-browser", cookies_from] if cookies_from else []
        yt_title, date = _yt_info(src, auth)
        title = name or yt_title
        job = slugify(title) + (f"-{date}" if date and not name else "")
        d = JOBS / job
        d.mkdir(parents=True, exist_ok=True)
        out = d / "source.mp4"
        if not out.exists():
            print(f"Downloading {src} ...")
            try:
                run([
                    "yt-dlp", "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]",
                    "--merge-output-format", "mp4", "-o", str(out), *auth, src,
                ])
            except Exception:
                if not any(d.iterdir()):
                    d.rmdir()
                raise SystemExit(
                    "\nDownload failed. If yt-dlp said 'Sign in to confirm you're not a bot', YouTube wants a login:\n"
                    f"  ./clip start \"{src}\" --cookies-from chrome    (or safari / firefox / edge)\n"
                    "Or use the church's original recording: ./clip start /path/to/file.mp4"
                )
    else:
        p = Path(src).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f"File not found: {p}")
        title = name or p.stem
        job = slugify(title)
        d = JOBS / job
        d.mkdir(parents=True, exist_ok=True)
        out = d / "source.mp4"
        if not out.exists():
            if p.suffix.lower() == ".mp4":
                shutil.copy2(p, out)
            else:
                run(["ffmpeg", "-y", "-i", str(p), "-c:v", "libx264", "-crf", "18",
                     "-c:a", "aac", "-b:a", "192k", str(out)])

    write_json(d / "job.json", {"job": job, "title": title, "source": src})
    print(f"\nJob ready: {job}\n  {out}")
    return job


def _yt_info(url: str, auth: list[str]) -> tuple[str, str]:
    import subprocess
    r = subprocess.run(["yt-dlp", "--skip-download", "--print", "%(title)s\t%(upload_date)s", *auth, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        if "not a bot" in r.stderr or "429" in r.stderr:
            raise SystemExit(
                "YouTube is asking this Mac to sign in before downloading.\n"
                "  Option A: re-run with your browser's YouTube login, e.g.\n"
                f"      ./clip start \"{url}\" --cookies-from chrome    (or safari / firefox / edge)\n"
                "  Option B: get the original recording file from the church and run ./clip start /path/to/file.mp4"
            )
        raise SystemExit(f"yt-dlp failed:\n{r.stderr}")
    title, _, date = r.stdout.strip().partition("\t")
    return title.split("||")[0].strip() or "sermon", date if date != "NA" else ""
