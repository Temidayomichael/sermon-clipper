import { useMemo } from "react";
import { Audio, interpolate, staticFile, useVideoConfig } from "remotion";
import { Word } from "../types";

/** Music bed that ducks under speech, swells a little in pauses, and fades in/out. */
export const Music: React.FC<{ src: string; words: Word[]; volume: number }> = ({ src, words, volume }) => {
  const { fps, durationInFrames } = useVideoConfig();

  // Per-frame "speaking" flag, softened so the music glides rather than pumps.
  const levels = useMemo(() => {
    const speaking = new Array(durationInFrames).fill(0);
    for (const w of words) {
      for (let f = Math.floor((w.start - 0.15) * fps); f <= Math.ceil((w.end + 0.25) * fps); f++) {
        if (f >= 0 && f < durationInFrames) speaking[f] = 1;
      }
    }
    const win = Math.round(fps * 0.25);
    return speaking.map((_, i) => {
      let s = 0;
      let n = 0;
      for (let k = Math.max(0, i - win); k <= Math.min(durationInFrames - 1, i + win); k++) {
        s += speaking[k];
        n++;
      }
      return s / n;
    });
  }, [words, fps, durationInFrames]);

  return (
    <Audio
      src={staticFile(src)}
      loop
      volume={(f) => {
        const duck = 1 - 0.45 * (levels[f] ?? 1); // full in pauses, 55% under speech
        const fade = interpolate(f, [0, fps * 1.2, durationInFrames - fps * 1.5, durationInFrames], [0, 1, 1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return volume * 1.8 * duck * fade;
      }}
    />
  );
};
