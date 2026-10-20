import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { P } from "./illustrations/palette";

/**
 * A stock B-roll clip filling its box. `look`:
 *  - "duotone": smooth navy-to-gold gradient map, matching the illustrations (like the reference chess shot)
 *  - "natural": real colour, lightly graded to sit with the sermon footage
 * A slow push-in keeps it alive. Muted: the sermon audio carries on underneath.
 */
export const StockClip: React.FC<{ src: string; look?: string; t: number; duration: number }> = ({ src, look = "natural", t, duration }) => {
  const push = 1.05 + 0.08 * Math.min(1, t / Math.max(duration, 0.1));
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: P.navyDeep }}>
      <AbsoluteFill style={{ transform: `scale(${push})` }}>
        <OffthreadVideo
          src={staticFile(src)}
          muted
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: look === "duotone" ? "grayscale(1) contrast(1.25) brightness(1.05)" : "contrast(1.08) saturate(1.1) brightness(0.95)",
          }}
        />
      </AbsoluteFill>
      {look === "duotone" ? (
        <>
          <AbsoluteFill style={{ background: P.gold, mixBlendMode: "multiply" }} />
          <AbsoluteFill style={{ background: P.navy, mixBlendMode: "lighten" }} />
        </>
      ) : (
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)" }} />
      )}
    </AbsoluteFill>
  );
};
