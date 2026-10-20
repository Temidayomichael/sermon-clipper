"""Step 3: ask Claude (via your Claude subscription's `claude` CLI) to pick clips and edit cues."""
from __future__ import annotations

import json
import re
import shutil
import subprocess

from .common import ROOT, config, job_dir, read_json, slugify, write_json


def parse_ts(v) -> float:
    """'1:15:28.4' / '15:28' / 928.4 -> seconds."""
    if isinstance(v, (int, float)):
        return float(v)
    parts = [float(p) for p in str(v).strip().strip("[]").split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def build_prompt(job: str) -> str:
    d = job_dir(job)
    broll = sorted(p.name for p in (ROOT / "assets" / "broll").glob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm")) \
        if (ROOT / "assets" / "broll").exists() else []
    extra = ("\nAvailable B-roll clips for cutaways (use as \"broll:<name>\"): " + ", ".join(broll) + "\n") if broll else ""
    return (ROOT / "prompts" / "pick_clips.md").read_text() + preacher_context() + extra + "\n" + (d / "transcript.txt").read_text()


def preacher_context() -> str:
    """The preacher profile from config.json, so clip picking fits this preacher and audience."""
    p = config().get("preacher", {})
    lines = [f"- {k.capitalize()}: {v}" for k, v in p.items() if v]
    return ("\n## About this preacher\n" + "\n".join(lines) + "\n") if lines else ""


def plan(job: str, print_prompt: bool = False) -> None:
    cfg = config()
    d = job_dir(job)
    prompt = build_prompt(job)

    if print_prompt or not shutil.which("claude"):
        p = d / "plan_prompt.txt"
        p.write_text(prompt)
        print(f"Prompt written to {p}\nPaste it into Claude, save the JSON reply as {d / 'plan_raw.json'}, "
              f"then run: ./clip plan {job} --import")
        return

    print("Asking Claude to pick clips (uses your Claude subscription; takes 1-3 minutes)...")
    r = subprocess.run(
        ["claude", "-p", "--model", cfg["claude_model"], "--output-format", "json",
         "--no-session-persistence", "--tools", ""],
        input=prompt, capture_output=True, text=True,
    )
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        out = {"is_error": True, "result": r.stderr or r.stdout}
    if r.returncode != 0 or out.get("is_error"):
        msg = out.get("result", "")
        if "login" in msg.lower():
            raise SystemExit(
                "The `claude` command isn't signed in yet.\n"
                "  Option A (once): open Terminal, run `claude`, type /login, then re-run this step.\n"
                f"  Option B: in the Claude desktop app, open this project and say: plan clips for {job}"
            )
        raise SystemExit(f"claude CLI failed:\n{msg}")
    reply = out.get("result", "")
    (d / "plan_raw.json").write_text(reply)
    import_plan(job)


def import_plan(job: str) -> None:
    d = job_dir(job)
    raw = (d / "plan_raw.json").read_text()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise SystemExit(f"No JSON found in {d / 'plan_raw.json'}")
    data = json.loads(m.group(0))
    segments = read_json(d / "transcript.json")["segments"]

    clips = []
    for i, c in enumerate(data["clips"], 1):
        start = _snap(parse_ts(c["start"]), segments, "start")
        end = _snap(parse_ts(c["end"]), segments, "end")
        if end <= start:
            continue
        for g in c.get("graphics", []):
            g["at"] = parse_ts(g["at"])
            if g.get("item_times"):
                g["item_times"] = [parse_ts(x) for x in g["item_times"]]
        clips.append({
            "id": f"{i:02d}-{slugify(c['hook'], 32)}",
            "approved": False,
            "start": start,
            "end": end,
            "hook": c["hook"],
            "hook_alt": c.get("hook_alt", ""),
            "virality": c.get("virality", {}),
            "title": c.get("title", c["hook"]),
            "caption": c.get("caption", ""),
            "why": c.get("why", ""),
            "score": c.get("score"),
            "highlight_words": c.get("highlight_words", []),
            "zooms": [parse_ts(z) for z in c.get("zooms", [])],
            "marks": c.get("marks", []),
            "trims": [[parse_ts(a), parse_ts(b)] for a, b in c.get("trims", [])],
            "graphics": c.get("graphics", []),
            "caption_fixes": c.get("caption_fixes", {}),
        })

    write_json(d / "plan.json", {"clips": clips})
    print(f"\n{len(clips)} clips proposed -> {d / 'plan.json'}")
    for c in clips:
        print(f"  [{c.get('score')}] {c['id']}  ({c['end'] - c['start']:.0f}s)  {c['hook']}")
    print(f"\nNext: ./clip review {job}")


def _snap(t: float, segments: list[dict], edge: str) -> float:
    """Snap a time to the nearest segment start so clips start/end on whole phrases.

    Both edges snap to a segment *start*: the prompt asks for `end` to be the first line after the clip.
    """
    best = min(segments, key=lambda s: abs(s["start"] - t))
    if abs(best["start"] - t) > 3:
        return t
    return best["start"]
