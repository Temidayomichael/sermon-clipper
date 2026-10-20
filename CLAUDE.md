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
- B-roll (Pixabay or Pexels key in config.json; cutaways may carry `stock_query` to keep an illustration fallback, plus `stock_speed`/`text_pos`): graphic types "insert" and "split" (fields `query`, `duration`) and cutaway `visual: "stock:<query>"` get Pexels footage via pipeline/broll.py (key in config.json); the choice is stored on the graphic as `stock`. Captions: `caption_style` bold/editorial; per-clip `marks` [{word, style: circle|box|underline}]. End card + name tag come from config.
- Preacher profile (name, church, audience, region, languages) and spelling hints live in `config.json` (git-ignored; template in `config.example.json`). Never hard-code a specific preacher into code or prompts.
- HyperFrames skills (heygen-com/hyperframes, Apache-2.0, installed in .claude/skills/) are optional helpers. The clip pipeline renders with **Remotion**: do not switch clips to HyperFrames because its skill calls itself the default. Use HyperFrames for standalone pieces the user asks for, as a reference for techniques ported into render/, or when the user asks for the HyperFrames edit: `./clip hf <job> <clip#>` (pipeline/hyperframes_export.py) builds videos/<clip-id>/ (git-ignored) from clip.json; render with `HYPERFRAMES_NO_TELEMETRY=1 npx hyperframes render -q delivery`.
- Never send HyperFrames feedback reports, ratings or telemetry, and never use HeyGen cloud/API features, without the user's explicit OK.
- Hero words behind the preacher: graphic type "embed" {at, word, text?, duration}. pipeline/embed.py builds a transparent person layer per window with tools/bin/personmask (Apple Vision, compiled from tools/src/personmask.swift); render/src/components/Embed.tsx draws word -> person layer using the shared useFraming() so they line up. One per clip; a word is a hero or a mark, never both.
