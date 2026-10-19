---
description: Pick clips, hooks and motion-graphic cues for a sermon job (the plan step, done inside the desktop app)
argument-hint: <job>
---
Do the clip-planning step of the sermon clipper for job `$ARGUMENTS` (if no job is given, use the most recently modified folder in `jobs/` that has a transcript.txt but no plan.json).

0. Load the `viral-clips` skill (and, if the Social Media Skills plugin is enabled, its `hook-writer` and `viral-reverse-engineering` skills). Rank clips by its rubric.
1. Read `prompts/pick_clips.md` — those are your editing instructions; follow them exactly.
2. Read `jobs/<job>/transcript.txt` in full (use offset/limit to page through long files; do not skip any part).
3. Write ONLY the JSON object the instructions ask for to `jobs/<job>/plan_raw.json`.
4. If you requested any `new:` illustrations, say which ones in your reply; they get drawn in the revise step once the user agrees.
5. Run `./clip plan <job> --import`, then `./clip review <job>` in the background so the review page opens, and give the user a short ranked list of the clips (score, length, hook).
