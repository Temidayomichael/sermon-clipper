import { Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { ClipProps } from "../types";

type Hit = { at: number; name: "whoosh" | "pop" | "hit" | "tick"; vol: number };

/** Places sound effects on the timeline: impact on the hook, whooshes on graphics and zooms, pops on key words. */
export const Sfx: React.FC<ClipProps> = ({ graphics, zooms, words, sfxVolume }) => {
  const { fps } = useVideoConfig();
  const hits: Hit[] = [{ at: 0, name: "hit", vol: 0.9 }];

  for (const g of graphics) {
    if (g.type === "cutaway") {
      hits.push({ at: Math.max(0, g.start - 0.2), name: "whoosh", vol: 1 });
      hits.push({ at: g.start + g.duration - 0.25, name: "whoosh", vol: 0.6 });
      const key = (g.keyword ?? "").toLowerCase();
      const kw = words.find((w) => w.start >= g.start && w.start < g.start + g.duration && w.w.toLowerCase().replace(/[^\w']/g, "") === key);
      if (kw) hits.push({ at: kw.start, name: "hit", vol: 0.9 });
      continue;
    }
    hits.push({ at: Math.max(0, g.start - 0.12), name: g.type === "keyword" ? "hit" : "whoosh", vol: 0.8 });
    if (g.type === "list") {
      const step = (g.duration * 0.6) / Math.max(1, g.items.length);
      g.items.forEach((_, i) => hits.push({ at: g.start + (g.itemOffsets?.[i] ?? 0.25 + i * step), name: "tick", vol: 0.7 }));
    }
  }
  for (const z of zooms) hits.push({ at: Math.max(0, z - 0.15), name: "whoosh", vol: 0.45 });

  let lastPop = -10;
  for (const w of words) {
    if (w.hl && w.start - lastPop > 0.8) {
      hits.push({ at: w.start, name: "pop", vol: 0.6 });
      lastPop = w.start;
    }
  }

  return (
    <>
      {hits.map((h, i) => (
        <Sequence key={i} from={Math.round(h.at * fps)} durationInFrames={Math.round(fps * 1.2)} layout="none">
          <Audio src={staticFile(`sfx/${h.name}.wav`)} volume={h.vol * sfxVolume} />
        </Sequence>
      ))}
    </>
  );
};
