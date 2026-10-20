# Sermon Clipper

**Turn a full sermon into ready-to-post vertical shorts:** captioned, colour-graded, face-tracked, with motion graphics, illustrated cutaways, sound effects and music, after a storyboard step where you approve every clip before anything is built.

Built for church media teams who don't have a full-time editor. Free and open source (MIT).

![Illustrated cutaway library](assets/illustration-library-new.png)

## What it does

1. **Ingest** a sermon from a video file (or a YouTube link you have the right to download).
2. **Transcribe** it on your own computer, with word-level timing.
3. **Pick the clips.** Claude reads the transcript and proposes 8-12 moments most likely to travel: contrarian claims, personal stories, humour, practical rules. Each gets a hook, title, caption, an A/B hook and a virality score.
4. **Storyboard.** A local web page shows each clip as phone-shaped frames (one per beat), the edited transcript with removed parts struck through, and the estimated length. Edit hooks and graphics, cut parts with ✂ Trim, leave notes, then approve or drop each clip.
5. **Build** the approved clips:

| Layer | What happens |
|---|---|
| Cuts | Starts on the hook; fillers ("are you following me?"), stammers and long pauses removed; jump-cut punch-ins for rhythm |
| Sync | Picture and sound cut at exact frame/sample counts, so lip-sync never drifts |
| Framing | Face-tracked 9:16 crop that holds steady per camera shot; switches to full frame for split-screen scripture slides |
| Lighting | Per-clip brightness balancing, contrast, saturation, sharpening (or your own LUT) |
| Audio | Rumble cut, noise reduction, compression, loudness at -14 LUFS |
| Captions | Word-by-word, 3-4 words per page. Two styles: **bold** (heavy uppercase) or **editorial** (clean words with gold italic key words). Hand-drawn **circles, marker boxes and underlines** draw onto key words |
| Words behind the preacher | Each clip's peak word appears huge **behind** the preacher, his head passing in front of it. The cut-out uses Apple's built-in person segmentation (macOS, on-device, no download); the craft rules are adapted from HyperFrames' embedded-captions |
| Stock B-roll | Real footage from [Pixabay](https://pixabay.com) or [Pexels](https://www.pexels.com) (free for commercial use), found automatically from search words Claude writes: quick full-screen **inserts** on concrete words, **split-screen** (preacher top, footage bottom), or stock footage inside a cutaway. Swap any clip from the storyboard |
| Motion graphics | Hook title bar, keyword slams, numbered lists, scripture cards, quote cards, progress bar |
| Illustrated cutaways | A full-screen animated illustration on the clip's core metaphor (18 so far: chess, seed, coins, scale, house, crown, prayer, rings, storm, lion, door, mountain, road, lamp, clock, cross, family, harvest) with the preacher's words as kinetic type and light-leak transitions. Or your own stock clip in the same duotone look |
| Transitions | A punchy opening (snap zoom + flash), whip blur on jump cuts, light leaks around cutaways |
| Name tag & end card | The preacher's name and church slide in a moment after the hook; a closing "Watch the full message on YouTube" card with your handle and logo |
| Sound | Whooshes, pops and impacts placed automatically; a soft music bed that ducks under speech |

Output per clip: a 1080×1920 MP4, an `.srt` caption file, and a `.txt` with the title, caption and A/B hook to paste when posting.

## Requirements

- **macOS on Apple Silicon** (M1 or later). Transcription uses [mlx-whisper](https://github.com/ml-explore/mlx-examples). Other platforms would need a different Whisper backend; contributions welcome.
- [Homebrew](https://brew.sh), Node.js 18+, and about 5 GB free disk space (models + renders).
- **Claude** for the clip-picking step, via [Claude Code](https://claude.com/claude-code) (desktop app or CLI). Without it you can still paste the generated prompt into any Claude chat (`./clip plan <job> --print-prompt`).

## Install

```bash
git clone https://github.com/Temidayomichael/sermon-clipper.git
cd sermon-clipper
brew install ffmpeg yt-dlp uv
uv sync                                # Python environment
(cd render && npm install)             # video renderer
cp config.example.json config.json     # then edit: your preacher, church, audience, local words
```

Optional:

```bash
./render/node_modules/.bin/remotion skills add   # official Remotion skills, for editing the graphics with Claude
./clip resolve-install                           # DaVinci Resolve bridge (see below)
```

The first transcription downloads the Whisper model (~1.5 GB); the first render downloads a headless Chrome for Remotion.

## Use it

```bash
./clip start sermon.mp4          # ingest -> transcribe -> plan -> opens the storyboard
```

On the storyboard, approve the clips you want (and leave notes on the ones you want changed). In Claude Code, opened in this folder:

- `/plan-clips <job>` picks clips (if `./clip start` couldn't call Claude itself)
- `/revise-clips <job>` applies your storyboard notes, and draws new illustrations when a clip needs one

Then build:

```bash
./clip make <job>                # cut, grade and render every approved clip -> jobs/<job>/out/
```

Preview part of a clip quickly with `./clip render <job> 05 --range 20-28` (writes `<clip>.preview.mp4`). All commands: `./clip --help` (`ingest`, `transcribe`, `plan`, `review`, `cut`, `retime`, `render`, `make`, `jobs`, `resolve-install`). After editing text or graphics on the storyboard, `./clip retime <job>` refreshes them in seconds without re-cutting.

## Customise

- **`config.json`**: preacher profile (name, church, audience, region, languages), spelling hints for transcription, brand colour, filler phrases, music/SFX volume. See `config.example.json` and `DEFAULT_CONFIG` in `pipeline/common.py`.
- **Music**: drop tracks into `assets/music/` (rotated across clips). Default: a generated soft pad.
- **HyperFrames edit (optional)**: `./clip hf <job> <clip#>` turns a cut clip into a [HyperFrames](https://github.com/heygen-com/hyperframes) project in `videos/<clip-id>/` (same look: face-tracked reframe, editorial captions, footage cutaways with kinetic words, words behind the preacher, name tag, end card, music and SFX). Preview with `npx hyperframes preview`, render with `npx hyperframes render -q delivery`. Set `HYPERFRAMES_NO_TELEMETRY=1` to keep telemetry off.
- **Stock B-roll**: create a free API key at [pixabay.com/api/docs](https://pixabay.com/api/docs/) and paste it into `config.json` as `"pixabay_api_key"` (a Pexels key in `"pexels_api_key"` also works). Footage is fetched for the storyboard and before building (`./clip broll <job>` to fetch on its own); post text includes the photographer credits. Your own clips in `assets/broll/` work too.
- **Picture quality**: `"clean": "auto"` (default) removes compression blocks, noise and banding before upscaling (strong for sources under 720p); set `"light"`, `"strong"` or `"off"`. Add `--4k` to `./clip make` / `./clip render` (or `"output_4k": true`) to export 2160×3840, which gives YouTube a higher-quality encode. Best results always come from the original camera files rather than a downloaded copy.
- **AI upscaling (optional, for low-resolution sources)**: download `realesrgan-ncnn-vulkan-*-macos.zip` from [Real-ESRGAN releases](https://github.com/xinntao/Real-ESRGAN/releases) (v0.2.5.0), unzip it into `tools/realesrgan/`, then add `--ai-upscale` to `./clip make` (or set `"upscale": "auto"`). Only the strip the vertical crop shows is AI-upscaled, blended with regular upscaling (`"upscale_mix"`, default 0.75) so faces stay natural. It is slow: roughly 30-35 minutes per minute of finished clip on an M3 Pro.
- **Captions and branding**: `"caption_style": "bold" | "editorial"`, the `"end_card"` title/subtitle/handle, `"lower_third": false` to hide the name tag. Put a logo at `assets/brand/logo.png` for the end card.
- **Sound effects**: replace `assets/sfx/whoosh.wav`, `pop.wav`, `hit.wav`, `tick.wav`.
- **Look**: add `assets/luts/look.cube`; graphics live in `render/src/components/`. Preview with `cd render && npm run studio`.
- **Illustrations**: `render/src/components/illustrations/`. Preview one with
  `cd render && npx remotion still src/index.ts Illustration out.png --props='{"name":"chess"}'`.
- **Clip-picking rules**: `prompts/pick_clips.md` and the `viral-clips` skill in `.claude/skills/`.

## Making clips trend

The project's `viral-clips` skill scores every clip out of 20 (hook, tension, life topic, specifics, emotion, payoff, shareability…), runs each hook through a five-point test, and writes an A/B hook for testing. Log results in `assets/learnings.md` after posting; future plans favour what worked for your audience. No tool can guarantee virality; this stacks the odds.

## DaVinci Resolve (optional)

`./clip resolve-install` adds bridge scripts to Resolve's **Workspace → Scripts → Utility** menu so Claude can build and adjust timelines inside Resolve (including the free version, which blocks outside control). Experimental.

## Use responsibly

- Clip only sermons you have permission to use, ideally with the preacher's and church's sign-off. Respect platform terms when downloading.
- The editing rules forbid taking a preacher out of context or inventing stories in titles. Please keep it that way.

## Licences and credits

- **This project:** MIT (see `LICENSE`).
- **[Remotion](https://www.remotion.dev)** renders the videos and has its own licence: free for individuals, for-profit companies with up to 3 employees, and **non-profit organisations (most churches)**. Larger for-profit companies need a [Remotion Company License](https://www.remotion.pro/license).
- Stock footage: [Pixabay](https://pixabay.com) (Pixabay Content License) or [Pexels](https://www.pexels.com) (Pexels License); the post text credits the videographers.
- Face detection: [YuNet](https://github.com/opencv/opencv_zoo) (Apache 2.0). Transcription: [mlx-whisper](https://github.com/ml-explore/mlx-examples) (MIT) with OpenAI Whisper models. Video: [FFmpeg](https://ffmpeg.org).
- The `viral-clips` skill summarises frameworks from the MIT-licensed open-source skills [vyralcontent/content-skills](https://github.com/vyralcontent/content-skills) and [arhamhi/hooksmith](https://github.com/arhamhi/hooksmith).

## Contributing

Issues and pull requests welcome, especially new illustrations, other transcription backends (Windows/Linux), and export to CapCut/Premiere/DaVinci timelines.
