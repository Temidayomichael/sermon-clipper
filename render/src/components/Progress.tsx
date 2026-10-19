import { useCurrentFrame, useVideoConfig } from "remotion";
import { Brand } from "../types";

export const Progress: React.FC<{ brand: Brand }> = ({ brand }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 10, background: "rgba(255,255,255,0.18)" }}>
      <div style={{ height: "100%", width: `${(frame / durationInFrames) * 100}%`, background: brand.accent }} />
    </div>
  );
};
