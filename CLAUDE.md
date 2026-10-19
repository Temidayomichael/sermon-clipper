# Sermon clipper

Turns full sermon recordings into captioned, graded, vertical shorts with motion graphics and sound effects.

Pipeline (`./clip --help`): ingest → transcribe (mlx-whisper, local) → plan (Claude picks clips per `prompts/pick_clips.md`) → review (local page, user approves) → cut (ffmpeg: filler/pause removal, grade, audio clean, face-track) → render (Remotion in `render/`).

- Jobs live in `jobs/<job>/` (git-ignored): source.mp4, transcript.{json,txt}, plan.json, clips/<id>/, out/.
- Times in plan.json are source seconds; cut.py re-times everything to the cut clip.
- Tunables live in `config.json` (see DEFAULT_CONFIG in pipeline/common.py). Drop `assets/luts/look.cube`, `assets/sfx/<name>.wav` or `assets/music/*.mp3` to override the look, SFX or music.
- When asked to "plan clips" for a job, follow `.claude/commands/plan-clips.md`.
- Workflow: plan -> storyboard (`./clip review`, user edits/notes/status) -> "revise <job>" (follow `.claude/commands/revise-clips.md`) -> user approves -> `./clip make`. Never build clips the user hasn't approved.
- New illustrations: plans may request `visual: "new:<description>"` (renders as the "glow" placeholder); draw them during revise per `.claude/commands/revise-clips.md`.
- Cutaways: graphic type "cutaway" (render/src/components/Cutaway.tsx) with visuals from render/src/components/illustrations/ (registered in index.tsx; keep the list in prompts/pick_clips.md in sync) or "broll:<file>" from assets/broll/.
- Official Remotion agent skills are installed in .agents/skills (symlinked to .claude/skills). Load remotion-best-practices / remotion-markup before changing render/ code.
- `./clip retime <job>` refreshes clip.json (captions, graphics, zooms) without re-cutting video.
- Virality: the project skill `.claude/skills/viral-clips` (rubric, hook test, retention, posting, guardrails) is loaded by plan-clips and revise-clips. Plans carry `hook_alt` (A/B) and `virality` {score, weakest}. Results go in `assets/learnings.md`.
- Preacher profile (name, church, audience, region, languages) and spelling hints live in `config.json` (git-ignored; template in `config.example.json`). Never hard-code a specific preacher into code or prompts.
