import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";
import { lightLeak } from "@remotion/effects/light-leak";
import { useMemo } from "react";
import { AbsoluteFill, OffthreadVideo, Solid, interpolate, staticFile, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { CutawayGraphic, Word } from "../types";
import { ILLUSTRATIONS } from "./illustrations";
import { P } from "./illustrations/palette";

const serif = loadSerif("italic", { weights: ["400"], subsets: ["latin"] }).fontFamily;

const norm = (w: string) => w.toLowerCase().replace(/[^\w']/g, "");

/** Your own B-roll clip, given the same smooth navy-to-gold duotone as the illustrations. */
const DuotoneClip: React.FC<{ src: string; t: number; duration: number }> = ({ src, t, duration }) => (
  <AbsoluteFill style={{ transform: `scale(${1.05 + 0.07 * (t / duration)})` }}>
    <OffthreadVideo
      src={staticFile(src)}
      muted
      style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) contrast(1.25) brightness(1.05)" }}
    />
    {/* Gradient map: darks -> navy, lights -> gold */}
    <AbsoluteFill style={{ background: P.gold, mixBlendMode: "multiply" }} />
    <AbsoluteFill style={{ background: P.navy, mixBlendMode: "lighten" }} />
  </AbsoluteFill>
);

/** Light-leak sweep, canvas-rendered with @remotion/effects. */
const Leak: React.FC<{ progress: number; seed: number; strength?: number }> = ({ progress, seed, strength = 0.7 }) => {
  const { width, height } = useVideoConfig();
  if (progress <= 0 || progress >= 1) return null;
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", opacity: strength }}>
      <Solid width={width} height={height} effects={[lightLeak({ seed, hueShift: 0, progress })]} />
    </AbsoluteFill>
  );
};

type Line = { words: { w: string; start: number; style: "sans" | "serif" | "key" }[] };

/**
 * Full-screen illustrated cutaway (like the duotone chess cutaways in popular faith-podcast edits): his voice continues
 * while an illustration or duotone clip fills the frame, and his words build up as kinetic type.
 */
export const Cutaway: React.FC<{ g: CutawayGraphic; words: Word[]; t: number }> = ({ g, words, t }) => {
  const local = t - g.start;
  const emphasis = useMemo(() => new Set((g.emphasis ?? []).map(norm)), [g.emphasis]);
  const keyword = norm(g.keyword ?? "");

  // His words inside the cutaway, grouped into short lines (max 3 words; the keyword gets its own line).
  const lines = useMemo(() => {
    const inside = words.filter((w) => w.start >= g.start - 0.05 && w.start < g.start + g.duration);
    const out: Line[] = [];
    let cur: Line = { words: [] };
    for (const w of inside) {
      const style = norm(w.w) === keyword ? "key" : emphasis.has(norm(w.w)) ? "serif" : "sans";
      if (style === "key" && cur.words.length) {
        out.push(cur);
        cur = { words: [] };
      }
      cur.words.push({ w: w.w.replace(/[,;:.]$/, ""), start: w.start, style });
      if (style === "key" || cur.words.length >= 3) {
        out.push(cur);
        cur = { words: [] };
      }
    }
    if (cur.words.length) out.push(cur);
    return out;
  }, [words, g.start, g.duration, emphasis, keyword]);

  // Show the latest two lines that have started (the phrase builds like the reference).
  const started = lines.filter((l) => l.words[0].start <= t + 0.02);
  const visible = started.slice(-2);

  const fadeIn = interpolate(local, [0, 0.12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(local, [g.duration - 0.18, g.duration], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const flash = interpolate(local, [0, 0.05, 0.22], [0.9, 0.6, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const Ill = g.visual.startsWith("broll:") ? null : ILLUSTRATIONS[g.visual] ?? ILLUSTRATIONS.glow;

  return (
    <AbsoluteFill style={{ opacity: fadeIn * fadeOut }}>
      {Ill ? <Ill t={local} duration={g.duration} /> : <DuotoneClip src={g.visual.slice(6)} t={local} duration={g.duration} />}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,18,48,0.55) 0%, rgba(10,18,48,0) 45%)" }} />
      <div style={{ position: "absolute", top: 470, left: 60, right: 60, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
        {visible.map((line, li) => (
          <div key={line.words[0].start} style={{ display: "flex", gap: 26, alignItems: "baseline", justifyContent: "center", flexWrap: "wrap" }}>
            {line.words.map((w, wi) => {
              const on = interpolate(t, [w.start - 0.02, w.start + 0.12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const base = { display: "inline-block", opacity: on, transform: `translateY(${(1 - on) * 18}px)` } as const;
              if (w.style === "key") {
                return (
                  <span
                    key={wi}
                    style={{
                      ...base,
                      fontFamily: fonts.body,
                      fontWeight: 900,
                      fontSize: Math.min(210, Math.round(1500 / Math.max(4, w.w.length))),
                      lineHeight: 1,
                      color: P.red,
                      letterSpacing: -2,
                      textShadow: `6px 8px 0 ${P.navyDeep}, 0 18px 40px rgba(0,0,0,0.5)`,
                      transform: `scale(${0.6 + 0.4 * on})`,
                    }}
                  >
                    {w.w.toLowerCase()}
                  </span>
                );
              }
              if (w.style === "serif") {
                return (
                  <span key={wi} style={{ ...base, fontFamily: serif, fontStyle: "italic", fontSize: 150, lineHeight: 1, color: P.cream, textShadow: "0 6px 24px rgba(0,0,0,0.45)" }}>
                    {w.w}
                  </span>
                );
              }
              return (
                <span
                  key={wi}
                  style={{
                    ...base,
                    fontFamily: fonts.body,
                    fontWeight: 700,
                    fontSize: li === visible.length - 1 ? 86 : 76,
                    color: "#fff",
                    textShadow: "0 4px 18px rgba(0,0,0,0.55)",
                  }}
                >
                  {w.w}
                </span>
              );
            })}
          </div>
        ))}
      </div>
      <AbsoluteFill style={{ background: "#fff", opacity: flash }} />
      <Leak progress={interpolate(local, [0, 0.4], [0.3, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} seed={3} />
      <Leak progress={interpolate(local, [g.duration - 0.35, g.duration + 0.05], [0, 0.55], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} seed={8} strength={0.55} />
    </AbsoluteFill>
  );
};
