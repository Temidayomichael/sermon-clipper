import { AbsoluteFill, interpolate } from "remotion";
import { Brand, H, StockGraphic, W } from "../types";
import { StockClip } from "./StockClip";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** A short white "whip" at the cut in and out of B-roll, like a fast camera move. */
const Whip: React.FC<{ local: number; duration: number }> = ({ local, duration }) => {
  const a = interpolate(local, [0, 0.1], [0.55, 0], clamp) + interpolate(local, [duration - 0.08, duration], [0, 0.35], clamp);
  return a > 0 ? <AbsoluteFill style={{ background: "#fff", opacity: a }} /> : null;
};

/** Quick full-screen B-roll insert on a concrete word; captions stay on top, his voice continues. */
export const Insert: React.FC<{ g: StockGraphic; t: number }> = ({ g, t }) => {
  const local = t - g.start;
  if (!g.src) return null;
  const blur = interpolate(local, [0, 0.12], [14, 0], clamp);
  return (
    <AbsoluteFill style={{ filter: blur > 0.2 ? `blur(${blur}px)` : undefined }}>
      <StockClip src={g.src} look={g.look} t={local} duration={g.duration} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.55) 100%)" }} />
      <Whip local={local} duration={g.duration} />
    </AbsoluteFill>
  );
};

/** Split screen: the pastor stays on top, B-roll slides up into the lower half. */
export const Split: React.FC<{ g: StockGraphic; t: number; brand: Brand }> = ({ g, t, brand }) => {
  const local = t - g.start;
  if (!g.src) return null;
  const top = 1000;
  const slide = interpolate(local, [0, 0.35], [1, 0], { ...clamp, easing: (x) => 1 - Math.pow(1 - x, 3) });
  const out = interpolate(local, [g.duration - 0.3, g.duration], [0, 1], clamp);
  const y = top + (H - top) * Math.max(slide, out);
  return (
    <div style={{ position: "absolute", left: 0, top: y, width: W, height: H - top, overflow: "hidden" }}>
      <StockClip src={g.src} look={g.look} t={local} duration={g.duration} />
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 10, background: brand.accent }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 30%)" }} />
    </div>
  );
};
