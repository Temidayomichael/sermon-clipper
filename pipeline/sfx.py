"""Default sound effects, synthesised with ffmpeg. Drop your own <name>.wav into assets/sfx to override."""
from __future__ import annotations

import shutil

from .common import ASSETS, RENDER, run

SOUNDS = {
    # Air whoosh for graphics and zoom entrances.
    "whoosh": ("anoisesrc=color=pink:d=0.55:a=0.9,bandpass=f=1400:width_type=h:w=2200,"
               "afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.23,volume=1.6"),
    # Soft pop for highlighted caption words / keyword slams.
    "pop": "aevalsrc='0.8*sin(2*PI*(500+1800*exp(-t*45))*t)*exp(-t*28)':d=0.16",
    # Low impact for the hook at the start.
    "hit": ("aevalsrc='0.9*sin(2*PI*(48+70*exp(-t*12))*t)*exp(-t*5)+0.25*(random(0)*2-1)*exp(-t*35)':d=0.9,"
            "lowpass=f=3000"),
    # Tick for list items appearing.
    "tick": "aevalsrc='0.7*sin(2*PI*2100*t)*exp(-t*80)':d=0.06",
}


def ensure_sfx() -> None:
    out_dir = RENDER / "public" / "sfx"
    out_dir.mkdir(parents=True, exist_ok=True)
    user_dir = ASSETS / "sfx"
    user_dir.mkdir(parents=True, exist_ok=True)
    for name, graph in SOUNDS.items():
        out = out_dir / f"{name}.wav"
        user = user_dir / f"{name}.wav"
        if user.exists():
            shutil.copy2(user, out)
        elif not out.exists():
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", graph,
                 "-ar", "48000", "-ac", "2", str(out)])


# Default music bed: a soft four-chord worship pad (C - G - Am - F), synthesised locally so it is
# royalty-free. Your own tracks in assets/music/ always take priority.
CHORDS = {
    "C": [130.81, 261.63, 329.63, 392.00, 523.25],
    "G": [98.00, 246.94, 293.66, 392.00, 493.88],
    "Am": [110.00, 261.63, 329.63, 440.00, 523.25],
    "F": [87.31, 261.63, 349.23, 440.00, 523.25],
}


def ensure_default_music() -> str:
    out = RENDER / "public" / "music" / "default-pad.wav"
    if out.exists():
        return "music/default-pad.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.parent / "_chords"
    tmp.mkdir(exist_ok=True)
    parts = []
    for name, freqs in CHORDS.items():
        # Each note: a sine plus a quiet detuned copy for warmth, with a slow swell.
        expr = "+".join(f"0.12*sin(2*PI*{f}*t)+0.05*sin(2*PI*{f * 1.003:.3f}*t)" for f in freqs)
        p = tmp / f"{name}.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
             "-i", f"aevalsrc='{expr}':s=48000:d=5", "-af",
             "afade=t=in:d=1.4,afade=t=out:st=3.4:d=1.6,lowpass=f=1800", "-ac", "2", str(p)])
        parts.append(p)
    inputs = sum((["-i", str(p)] for p in parts), [])
    chain = "[0][1]acrossfade=d=1:c1=tri:c2=tri[x1];[x1][2]acrossfade=d=1:c1=tri:c2=tri[x2];" \
            "[x2][3]acrossfade=d=1:c1=tri:c2=tri,aecho=0.8:0.6:90|180:0.35|0.2,volume=1.4[out]"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", chain,
         "-map", "[out]", "-ar", "48000", str(out)])
    shutil.rmtree(tmp)
    return "music/default-pad.wav"
