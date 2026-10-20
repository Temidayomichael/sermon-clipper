"""Sermon clipper: turn a full sermon into captioned, graded vertical shorts.

  ./clip start <youtube-url | file>    ingest -> transcribe -> plan -> open review page
  ./clip make <job>                     cut + render every approved clip

Individual steps:
  ./clip ingest <url | file> [--name NAME]
  ./clip transcribe <job>
  ./clip plan <job> [--print-prompt | --import]
  ./clip review <job>
  ./clip cut <job> [clip-id-prefix]
  ./clip retime <job> [clip-id-prefix]   refresh captions/graphics after edits, without re-cutting
  ./clip render <job> [clip-id-prefix ...]
  ./clip broll <job> [--refresh]         find stock B-roll (Pexels) for inserts, splits and stock cutaways
  ./clip jobs
  ./clip resolve-install                 install the DaVinci Resolve bridge (optional)
"""
from __future__ import annotations

import argparse
import os
import sys

from .common import JOBS


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="clip", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for cmd in ("start", "ingest"):
        s = sub.add_parser(cmd); s.add_argument("src"); s.add_argument("--name")
        s.add_argument("--cookies-from", metavar="BROWSER", help="use your browser's YouTube login (chrome, safari, firefox, edge)")
    s = sub.add_parser("transcribe"); s.add_argument("job")
    s = sub.add_parser("plan"); s.add_argument("job")
    s.add_argument("--print-prompt", action="store_true", help="write the prompt to a file instead of calling claude")
    s.add_argument("--import", dest="do_import", action="store_true", help="import plan_raw.json you saved by hand")
    s = sub.add_parser("review"); s.add_argument("job"); s.add_argument("--port", type=int, default=8765)
    s = sub.add_parser("cut"); s.add_argument("job"); s.add_argument("only", nargs="?")
    s = sub.add_parser("retime"); s.add_argument("job"); s.add_argument("only", nargs="?")
    s = sub.add_parser("render"); s.add_argument("job"); s.add_argument("ids", nargs="*")
    s.add_argument("--4k", dest="k4", action="store_true", help="render at 2160x3840")
    s.add_argument("--range", help="preview only part of each clip, in seconds, e.g. 20-28 (writes <clip>.preview.mp4)")
    s = sub.add_parser("broll", help="find and download stock B-roll for every clip that needs it")
    s.add_argument("job"); s.add_argument("--refresh", action="store_true", help="search again even if footage is chosen")
    s = sub.add_parser("make"); s.add_argument("job"); s.add_argument("only", nargs="?")
    s.add_argument("--4k", dest="k4", action="store_true", help="cut and render at 4K (2160x3840)")
    s.add_argument("--ai-upscale", dest="ai_up", action="store_true", help="AI-upscale low-res footage (slow, ~30 min per clip)")
    s = sub.add_parser("hf", help="export a cut clip as a HyperFrames project (videos/<name>)")
    s.add_argument("job"); s.add_argument("clip", help="clip id prefix, e.g. 01"); s.add_argument("--project")
    sub.add_parser("jobs")
    sub.add_parser("resolve-install", help="install the DaVinci Resolve bridge scripts")

    a = ap.parse_args(argv)
    if getattr(a, "k4", False):
        os.environ["SERMON_CLIPPER_4K"] = "1"
    if getattr(a, "range", None):
        os.environ["SERMON_CLIPPER_RANGE"] = a.range
    if getattr(a, "ai_up", False):
        os.environ["SERMON_CLIPPER_AI_UPSCALE"] = "1"

    if a.cmd in ("start", "ingest"):
        from .ingest import ingest
        job = ingest(a.src, a.name, a.cookies_from)
        if a.cmd == "start":
            from .plan import plan
            from .review import review
            from .transcribe import transcribe
            transcribe(job)
            plan(job)
            review(job)
    elif a.cmd == "transcribe":
        from .transcribe import transcribe
        transcribe(a.job)
    elif a.cmd == "plan":
        from .plan import import_plan, plan
        import_plan(a.job) if a.do_import else plan(a.job, a.print_prompt)
    elif a.cmd == "review":
        from .review import review
        review(a.job, a.port)
    elif a.cmd == "cut":
        from .cut import cut
        cut(a.job, a.only)
    elif a.cmd == "retime":
        from .cut import cut
        cut(a.job, a.only, retime=True)
    elif a.cmd == "render":
        from .render import render
        render(a.job, a.ids or None)
    elif a.cmd == "make":
        from .broll import api_key, resolve_job
        from .cut import cut
        from .render import render
        if api_key():
            resolve_job(a.job)
        ids = cut(a.job, a.only)
        if ids:
            render(a.job, ids)
    elif a.cmd == "broll":
        from .broll import resolve_job
        print(f"Fetched footage for {resolve_job(a.job, only_missing=not a.refresh)} graphic(s).")
    elif a.cmd == "hf":
        from .hyperframes_export import export
        export(a.job, a.clip, a.project)
    elif a.cmd == "resolve-install":
        from .resolve_install import resolve_install
        resolve_install()
    elif a.cmd == "jobs":
        for d in sorted(p for p in JOBS.glob("*") if p.is_dir()) if JOBS.exists() else []:
            n = len(list((d / "out").glob("*.mp4"))) if (d / "out").exists() else 0
            print(f"{d.name}  ({n} rendered)")


if __name__ == "__main__":
    main(sys.argv[1:])
