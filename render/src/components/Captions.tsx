import { useMemo } from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand, CAPTION_TOP, Word } from "../types";

type Page = { start: number; end: number; words: Word[] };

const MAX_WORDS = 4;
const MAX_CHARS = 22;

/** Group words into short punchy caption pages (TikTok style). */
function paginate(words: Word[]): Page[] {
  const pages: Page[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (cur.length) pages.push({ start: cur[0].start, end: cur[cur.length - 1].end, words: cur });
    cur = [];
  };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    const chars = cur.reduce((n, x) => n + x.w.length + 1, 0) + w.w.length;
    if (cur.length && (cur.length >= MAX_WORDS || chars > MAX_CHARS || (prev && w.start - prev.end > 0.35))) flush();
    cur.push(w);
    if (/[.!?]$/.test(w.w) && cur.length > 1) flush();
  });
  flush();
  // Hold each page until the next one starts (no flicker in short gaps).
  for (let i = 0; i < pages.length - 1; i++) {
    if (pages[i + 1].start - pages[i].end < 0.6) pages[i].end = pages[i + 1].start;
  }
  return pages;
}

export const Captions: React.FC<{ words: Word[]; brand: Brand; t: number; hidden?: boolean }> = ({ words, brand, t, hidden }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pages = useMemo(() => paginate(words), [words]);
  const page = pages.find((p) => t >= p.start && t < p.end + 0.05);
  if (!page || hidden) return null;

  const enter = spring({ frame: frame - Math.round(page.start * fps), fps, config: { damping: 14, stiffness: 260 } });

  return (
    <div
      style={{
        position: "absolute",
        top: CAPTION_TOP,
        left: 50,
        right: 50,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: "4px 40px",
        transform: `scale(${0.8 + 0.2 * enter}) translateY(${(1 - enter) * 20}px)`,
      }}
    >
      {page.words.map((w, i) => {
        const active = t >= w.start && t < w.end + 0.08;
        const color = w.hl ? brand.accent : active ? brand.accent : brand.text;
        const wpop = w.hl
          ? spring({ frame: frame - Math.round(w.start * fps), fps, config: { damping: 9, stiffness: 300 } })
          : 1;
        return (
          <span
            key={i}
            style={{
              fontFamily: fonts.body,
              fontWeight: 900,
              fontSize: w.hl ? 92 : 80,
              lineHeight: 1.15,
              textTransform: "uppercase",
              color,
              WebkitTextStroke: "10px #000",
              paintOrder: "stroke fill",
              textShadow: "0 8px 24px rgba(0,0,0,0.55)",
              transform: `scale(${(active ? 1.06 : 1) * (0.7 + 0.3 * wpop)})`,
              display: "inline-block",
            }}
          >
            {w.w.replace(/[,;:]$/, "")}
          </span>
        );
      })}
    </div>
  );
};
