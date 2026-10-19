"""Step 2: word-level transcript with mlx-whisper (runs locally on Apple Silicon)."""
from __future__ import annotations

from .common import config, job_dir, ts, write_json

# Generic church vocabulary; the preacher's own names and places come from config.json ("preacher", "vocab").
VOCAB = (
    "Hallelujah, praise God, amen. Thessalonians, Corinthians, Ephesians, Ecclesiastes, Lamentations, "
    "Deuteronomy, Isaiah, Jeremiah, Elijah, Elisha, Nehemiah. Tithe, offering, Holy Ghost, Holy Spirit."
)


def vocab_hint(cfg: dict) -> str:
    p = cfg.get("preacher", {})
    who = ", ".join(x for x in (p.get("name"), p.get("church")) if x)
    return " ".join(x for x in (who + "." if who else "", VOCAB, cfg.get("vocab", "")) if x)


def transcribe(job: str) -> None:
    import mlx_whisper

    cfg = config()
    d = job_dir(job)
    out = d / "transcript.json"
    if out.exists():
        print("Transcript already exists, skipping. Delete transcript.json to redo.")
        return

    print(f"Transcribing with {cfg['whisper_model']} (first run downloads the model, ~1.5 GB)...")
    result = mlx_whisper.transcribe(
        str(d / "source.mp4"),
        path_or_hf_repo=cfg["whisper_model"],
        language=cfg["language"],
        word_timestamps=True,
        condition_on_previous_text=False,
        hallucination_silence_threshold=2.0,
        initial_prompt=vocab_hint(cfg),
        verbose=False,
    )

    segments, words = [], []
    for seg in result["segments"]:
        text = seg["text"].strip()
        if not text:
            continue
        segments.append({"start": round(seg["start"], 2), "end": round(seg["end"], 2), "text": text})
        for w in seg.get("words", []):
            word = w["word"].strip()
            if word:
                words.append({"w": word, "start": round(w["start"], 3), "end": round(w["end"], 3)})

    lines = sentence_lines(words) or segments
    write_json(out, {"segments": lines, "whisper_segments": segments, "words": words})
    (d / "transcript.txt").write_text("\n".join(f"[{ts(s['start'])}] {s['text']}" for s in lines))
    print(f"Transcript: {len(lines)} lines, {len(words)} words -> {out}")


def sentence_lines(words: list[dict], max_words: int = 18, gap: float = 0.8) -> list[dict]:
    """Re-cut the transcript into short sentence-level lines so clip starts can be precise."""
    lines, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["start"] - cur[-1]["end"] > gap or len(cur) >= max_words):
            lines.append(cur)
            cur = []
        cur.append(w)
        if w["w"][-1:] in ".?!":
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    return [{"start": round(l[0]["start"], 2), "end": round(l[-1]["end"], 2),
             "text": " ".join(x["w"] for x in l)} for l in lines]
