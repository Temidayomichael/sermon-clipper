import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ILLUSTRATIONS } from "./components/illustrations";

/** Studio/still preview of one illustration: npx remotion still src/index.ts Illustration out.png --props='{"name":"chess"}' */
export const IllustrationPreview: React.FC<{ name: string; seconds?: number }> = ({ name }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const Comp = ILLUSTRATIONS[name];
  return <AbsoluteFill>{Comp ? <Comp t={frame / fps} duration={durationInFrames / fps} /> : null}</AbsoluteFill>;
};
