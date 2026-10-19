import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "./components/Background";
import { Music } from "./components/Music";
import { Captions } from "./components/Captions";
import { Cutaway } from "./components/Cutaway";
import { Graphics } from "./components/Graphics";
import { HookBar } from "./components/HookBar";
import { Progress } from "./components/Progress";
import { Sfx } from "./components/Sfx";
import { ClipProps, CutawayGraphic } from "./types";
import { fonts } from "./fonts";

export const Short: React.FC<ClipProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const cutaway = p.graphics.find(
    (g): g is CutawayGraphic => g.type === "cutaway" && t >= g.start && t < g.start + g.duration,
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", fontFamily: fonts.body }}>
      <Background video={p.video} crop={p.crop} zooms={p.zooms} edits={p.edits ?? []} />
      {/* Soft top and bottom vignettes so text always reads. */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.6) 100%)",
        }}
      />
      {cutaway ? <Cutaway g={cutaway} words={p.words} t={t} /> : null}
      <HookBar text={p.hook} brand={p.brand} />
      <Graphics graphics={p.graphics} brand={p.brand} t={t} />
      <Captions words={p.words} brand={p.brand} t={t} hidden={!!cutaway} />
      <Progress brand={p.brand} />
      <Sfx {...p} />
      {p.music ? <Music src={p.music} words={p.words} volume={p.musicVolume} /> : null}
    </AbsoluteFill>
  );
};
