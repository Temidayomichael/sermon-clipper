import { AbsoluteFill, Easing, OffthreadVideo, Sequence, interpolate, staticFile, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand, EmbedGraphic, H, W } from "../types";
import { Framing } from "./Background";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Words behind the preacher (technique from HyperFrames' embedded-captions craft rules):
 * one huge peak word (~18% of frame height) sits BETWEEN the backdrop and the person, so his head
 * covers part of it. Per-letter entrance, a slow breathing hold, clean exit. Rendered under PersonLayer.
 */
export const EmbedWord: React.FC<{ g: EmbedGraphic; t: number; framing: Framing; brand: Brand }> = ({ g, t, framing, brand }) => {
  const local = t - g.start;
  // Only draw the word when the preacher cut-out exists; without it the word would sit in front of him.
  if (local < 0 || local > g.duration || !g.fgSrc) return null;
  const text = (g.text || g.word || "").toUpperCase();
  const size = Math.min(H * 0.19, Math.round(1900 / Math.max(3, text.length)));
  const { vw, vh, left, top, boxTop } = framing;
  // Head position in the vertical frame; the word's middle sits across the forehead/eyes.
  const headY = boxTop + top + (g.headTop ?? 0.25) * vh;
  const cx = Math.max(size * text.length * 0.27, Math.min(W - size * text.length * 0.27, left + (g.headX ?? 0.5) * vw));
  const cy = headY + vh * 0.1; // across the forehead: his head covers roughly a third to half of the word
  const exit = interpolate(local, [g.duration - 0.3, g.duration], [0, 1], clamp);
  const breathe = 1 + 0.025 * Math.sin(Math.min(local, g.duration) * 2.2);
  return (
    <div
      style={{
        position: "absolute",
        left: cx,
        top: cy,
        transform: `translate(-50%, -50%) scale(${breathe * (1 + 0.08 * exit)})`,
        opacity: (1 - exit) * (1 - framing.fit),
        display: "flex",
        whiteSpace: "nowrap",
        fontFamily: fonts.display,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: -1,
        color: brand.accent,
        textShadow: `0 ${size * 0.04}px ${size * 0.12}px rgba(0,0,0,0.45)`,
      }}
    >
      {text.split("").map((ch, i) => {
        const at = i * 0.045; // tight stagger: a punchy, urgent arrival
        const p = interpolate(local, [at, at + 0.32], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) });
        return (
          <span key={i} style={{ display: "inline-block", opacity: Math.min(1, p * 1.6), transform: `translateY(${(1 - p) * size * 0.45}px) scale(${0.7 + 0.3 * p})` }}>
            {ch === " " ? " " : ch}
          </span>
        );
      })}
    </div>
  );
};

/** The preacher cut out of the frame (transparent ProRes 4444), positioned exactly like the background video. */
export const PersonLayer: React.FC<{ g: EmbedGraphic; framing: Framing }> = ({ g, framing }) => {
  const { fps } = useVideoConfig();
  if (!g.fgSrc || g.fgFrom === undefined || !g.fgDuration) return null;
  const { vw, vh, left, top, blur, fit, boxTop, boxH } = framing;
  return (
    <Sequence from={Math.round(g.fgFrom * fps)} durationInFrames={Math.round(g.fgDuration * fps)} layout="none">
      <AbsoluteFill style={{ opacity: 1 - fit }}>
        <div style={{ position: "absolute", top: boxTop, left: 0, width: W, height: boxH, overflow: "hidden" }}>
          <OffthreadVideo
            src={staticFile(g.fgSrc)}
            transparent
            muted
            style={{ position: "absolute", width: vw, height: vh, left, top, maxWidth: "none", filter: blur ? `blur(${blur}px)` : undefined }}
          />
        </div>
      </AbsoluteFill>
    </Sequence>
  );
};
