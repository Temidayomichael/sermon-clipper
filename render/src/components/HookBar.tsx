import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand, HOOK_TOP } from "../types";

export const HookBar: React.FC<{ text: string; brand: Brand }> = ({ text, brand }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12, stiffness: 180 } });
  const underline = interpolate(frame, [8, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const size = text.length < 22 ? 82 : text.length < 34 ? 70 : 60;

  return (
    <div
      style={{
        position: "absolute",
        top: HOOK_TOP,
        left: 60,
        right: 60,
        display: "flex",
        justifyContent: "center",
        transform: `scale(${0.85 + 0.15 * pop})`,
        opacity: pop,
      }}
    >
      <div
        style={{
          background: "#fff",
          color: "#0b0b0d",
          fontFamily: fonts.display,
          fontSize: size,
          lineHeight: 1.08,
          textTransform: "uppercase",
          textAlign: "center",
          padding: "20px 34px 24px",
          borderRadius: 22,
          boxShadow: "0 18px 50px rgba(0,0,0,0.45)",
          position: "relative",
          letterSpacing: 0.5,
        }}
      >
        {text}
        <div
          style={{
            position: "absolute",
            left: 34,
            bottom: 12,
            height: 8,
            width: `calc((100% - 68px) * ${underline})`,
            background: brand.accent,
            borderRadius: 4,
          }}
        />
      </div>
    </div>
  );
};
