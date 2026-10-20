import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand } from "../types";

const IN = 1.3; // seconds after the start
const OUT = 4.6;

/** Name tag that slides in a moment after the hook, so new viewers know who is speaking. */
export const LowerThird: React.FC<{ name: string; church: string; brand: Brand; hidden: boolean }> = ({ name, church, brand, hidden }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < IN || t > OUT || hidden) return null;
  const enter = spring({ frame: frame - Math.round(IN * fps), fps, config: { damping: 16, stiffness: 160 } });
  const exit = interpolate(t, [OUT - 0.35, OUT], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const x = -620 * (1 - enter) - 620 * exit;
  return (
    <div style={{ position: "absolute", left: 50 + x, top: 1180, display: "flex", alignItems: "stretch", filter: "drop-shadow(0 12px 30px rgba(0,0,0,0.5))" }}>
      <div style={{ width: 14, background: brand.accent, borderRadius: "8px 0 0 8px" }} />
      <div style={{ background: "rgba(10,10,14,0.88)", padding: "14px 26px 16px", borderRadius: "0 10px 10px 0" }}>
        <div style={{ fontFamily: fonts.display, fontSize: 52, lineHeight: 1, color: "#fff", textTransform: "uppercase", letterSpacing: 1 }}>{name}</div>
        {church ? <div style={{ fontFamily: fonts.body, fontWeight: 600, fontSize: 28, color: brand.accent, marginTop: 6 }}>{church}</div> : null}
      </div>
    </div>
  );
};
