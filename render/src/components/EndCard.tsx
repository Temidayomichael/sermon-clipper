import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand } from "../types";

const serif = loadSerif("italic", { weights: ["400"], subsets: ["latin"] }).fontFamily;

/** Closing card after the clip: points viewers to the full message. Shown over the frozen last frame. */
export const EndCard: React.FC<{
  start: number;
  title: string;
  subtitle: string;
  handle: string;
  logo: string | null;
  brand: Brand;
}> = ({ start, title, subtitle, handle, logo, brand }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(start * fps);
  if (frame < f0) return null;
  const local = (frame - f0) / fps;
  const dim = interpolate(local, [0, 0.35], [0, 0.86], { extrapolateRight: "clamp" });
  const pop = spring({ frame: frame - f0 - 4, fps, config: { damping: 13, stiffness: 170 } });
  const line = interpolate(local, [0.25, 0.7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: `rgba(8,10,20,${dim})` }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", gap: 26, transform: `scale(${0.85 + 0.15 * pop})`, opacity: pop }}>
        {logo ? <Img src={staticFile(logo)} style={{ width: 220, height: 220, objectFit: "contain", marginBottom: 10 }} /> : null}
        <div style={{ fontFamily: fonts.display, fontSize: 96, color: "#fff", textTransform: "uppercase", textAlign: "center", lineHeight: 1, padding: "0 60px" }}>{title}</div>
        <div style={{ fontFamily: serif, fontStyle: "italic", fontSize: 84, color: brand.accent, lineHeight: 1 }}>{subtitle}</div>
        <div style={{ width: 360 * line, height: 8, borderRadius: 4, background: brand.accent }} />
        {handle ? <div style={{ fontFamily: fonts.body, fontWeight: 800, fontSize: 46, color: "#fff", opacity: line }}>{handle}</div> : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
