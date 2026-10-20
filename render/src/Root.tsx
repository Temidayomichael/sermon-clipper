import { Composition } from "remotion";
import { IllustrationPreview } from "./IllustrationPreview";
import { Short } from "./Short";
import { ClipProps, H, W } from "./types";

const sample: ClipProps = {
  id: "sample",
  hook: "Nobody will reward you for serving them",
  duration: 8,
  fps: 30,
  video: "",
  music: null,
  words: "People don't reward service. People reward excellence and relationships."
    .split(" ")
    .map((w, i) => ({ w, start: 0.4 + i * 0.45, end: 0.8 + i * 0.45, hl: /excellence|relationships/i.test(w) })),
  graphics: [
    { type: "list", start: 3, duration: 4, title: "People reward", items: ["Excellence", "Relationships"] },
  ],
  zooms: [2.5],
  crop: [{ t: 0, x: 0.5 }],
  brand: { accent: "#FFD43B", panel: "rgba(10,10,14,0.82)", text: "#FFFFFF" },
  sfxVolume: 0.5,
  musicVolume: 0.07,
};

export const Root: React.FC = () => (
  <>
  <Composition
    id="Illustration"
    component={IllustrationPreview}
    width={W}
    height={H}
    fps={30}
    durationInFrames={120}
    defaultProps={{ name: "chess", seconds: 4 }}
    calculateMetadata={({ props }) => ({ durationInFrames: Math.round((props.seconds ?? 4) * 30) })}
  />
  <Composition
    id="Short"
    component={Short}
    width={W}
    height={H}
    fps={30}
    durationInFrames={240}
    defaultProps={sample}
    calculateMetadata={({ props }) => ({
      fps: props.fps,
      durationInFrames: Math.ceil((props.duration + (props.endCard ? props.endCard.seconds : 0.4)) * props.fps),
    })}
  />
  </>
);
