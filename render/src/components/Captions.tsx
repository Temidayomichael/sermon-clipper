import { useMemo } from "react";
import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand, CAPTION_TOP, Word } from "../types";

type Page = { start: number; end: number; words: Word[] };

const serif = loadSerif("italic", { weights: ["400"], subsets: ["latin"] }).fontFamily;

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

/** Hand-drawn style mark that draws onto a word: circle, marker box or underline swoosh. */
const Mark: React.FC<{ kind: "circle" | "box" | "underline"; p: number; color: string }> = ({ kind, p, color }) => {
  if (p <= 0) return null;
  if (kind === "box") {
    return (
      <span
        style={{
          position: "absolute",
          left: -14,
          right: -14,
          top: "8%",
          bottom: "4%",
          background: color,
          borderRadius: 10,
          transform: `rotate(-2deg) scaleX(${p})`,
          transformOrigin: "left center",
          zIndex: -1,
        }}
      />
    );
  }
  const stroke = { fill: "none", stroke: color, strokeWidth: 9, strokeLinecap: "round" as const, pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - p };
  if (kind === "circle") {
    return (
      <svg viewBox="0 0 100 50" preserveAspectRatio="none" style={{ position: "absolute", left: "-14%", top: "-22%", width: "128%", height: "144%", overflow: "visible", pointerEvents: "none" }}>
        <path d="M58 4 C88 3 99 16 97 27 C95 41 72 48 46 47 C18 46 2 38 3 25 C4 11 26 4 52 5 C70 6 84 9 92 14" vectorEffect="non-scaling-stroke" {...stroke} />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 100 20" preserveAspectRatio="none" style={{ position: "absolute", left: "-4%", bottom: "-18%", width: "108%", height: "32%", overflow: "visible", pointerEvents: "none" }}>
      <path d="M2 14 C30 4 62 4 98 10" vectorEffect="non-scaling-stroke" {...stroke} />
    </svg>
  );
};

/** Clean "editorial" captions (like the reference): sans words build up, key words in gold italic serif. */
const Editorial: React.FC<{ page: Page; brand: Brand; t: number; enter: number }> = ({ page, brand, t, enter }) => (
  <div
    style={{
      position: "absolute",
      top: CAPTION_TOP - 10,
      left: 60,
      right: 60,
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      alignItems: "baseline",
      gap: "0 20px",
      opacity: enter,
    }}
  >
    {page.words.map((w, i) => {
      const on = interpolate(t, [w.start - 0.03, w.start + 0.1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      const mp = w.mark ? interpolate(t, [w.start, w.start + 0.35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
      const text = w.w.replace(/[,;:]$/, "");
      const base = { position: "relative" as const, display: "inline-block", opacity: on, transform: `translateY(${(1 - on) * 10}px)` };
      return w.hl ? (
        <span key={i} style={{ ...base, fontFamily: serif, fontStyle: "italic", fontSize: 118, lineHeight: 1.05, color: w.mark === "box" && mp > 0.5 ? "#0B1433" : brand.accent, textShadow: "0 6px 22px rgba(0,0,0,0.5)" }}>
          {w.mark ? <Mark kind={w.mark} p={mp} color={brand.accent} /> : null}
          {text}
        </span>
      ) : (
        <span key={i} style={{ ...base, fontFamily: fonts.body, fontWeight: 700, fontSize: 78, lineHeight: 1.2, color: w.mark === "box" && mp > 0.5 ? "#0B1433" : "#fff", textShadow: "0 4px 18px rgba(0,0,0,0.65)" }}>
          {w.mark ? <Mark kind={w.mark} p={mp} color={brand.accent} /> : null}
          {text}
        </span>
      );
    })}
  </div>
);

export const Captions: React.FC<{
  words: Word[];
  brand: Brand;
  t: number;
  hidden?: boolean;
  style?: "bold" | "editorial";
  /** Words shown as a hero elsewhere (behind the preacher) are left out of the captions: one place per word. */
  omit?: { word: string; start: number; end: number }[];
}> = ({ words, brand, t, hidden, style = "bold", omit = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shown = useMemo(() => {
    const n = (x: string) => x.toLowerCase().replace(/[^\w']/g, "");
    return words.filter((w) => !omit.some((o) => n(o.word) === n(w.w) && w.start >= o.start - 0.4 && w.start <= o.end));
  }, [words, omit]);
  const pages = useMemo(() => paginate(shown), [shown]);
  const page = pages.find((p) => t >= p.start && t < p.end + 0.05);
  if (!page || hidden) return null;

  const enter = spring({ frame: frame - Math.round(page.start * fps), fps, config: { damping: 14, stiffness: 260 } });
  if (style === "editorial") return <Editorial page={page} brand={brand} t={t} enter={enter} />;

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
        const mp = w.mark ? interpolate(t, [w.start, w.start + 0.35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
        const boxed = w.mark === "box" && mp > 0.5;
        const color = boxed ? "#fff" : w.hl ? brand.accent : active ? brand.accent : brand.text;
        const wpop = w.hl
          ? spring({ frame: frame - Math.round(w.start * fps), fps, config: { damping: 9, stiffness: 300 } })
          : 1;
        return (
          <span
            key={i}
            style={{
              position: "relative",
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
            {w.mark ? <Mark kind={w.mark} p={mp} color={w.mark === "box" ? "#D8262F" : brand.accent} /> : null}
            {w.w.replace(/[,;:]$/, "")}
          </span>
        );
      })}
    </div>
  );
};
