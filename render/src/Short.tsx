import { AbsoluteFill, Freeze, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Background, useFraming } from "./components/Background";
import { Insert, Split } from "./components/BRoll";
import { Captions } from "./components/Captions";
import { Cutaway } from "./components/Cutaway";
import { EmbedWord, PersonLayer } from "./components/Embed";
import { EndCard } from "./components/EndCard";
import { Graphics } from "./components/Graphics";
import { HookBar } from "./components/HookBar";
import { LowerThird } from "./components/LowerThird";
import { Music } from "./components/Music";
import { Progress } from "./components/Progress";
import { Sfx } from "./components/Sfx";
import { fonts } from "./fonts";
import { ClipProps, CutawayGraphic, EmbedGraphic, StockGraphic } from "./types";

export const Short: React.FC<ClipProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const live = (g: { start: number; duration: number }) => t >= g.start && t < g.start + g.duration;
  const cutaway = p.graphics.find((g): g is CutawayGraphic => g.type === "cutaway" && live(g));
  const insert = p.graphics.find((g): g is StockGraphic => g.type === "insert" && live(g));
  const split = p.graphics.find((g): g is StockGraphic => g.type === "split" && live(g));
  const panel = p.graphics.some((g) => !["cutaway", "insert", "split", "embed"].includes(g.type) && live(g));
  const embeds = p.graphics.filter((g): g is EmbedGraphic => g.type === "embed");
  const embed = embeds.find(live);
  const framing = useFraming(p.crop, p.zooms, p.edits ?? []);
  // While a hero word plays, the other captions step back (setup -> impact -> afterglow).
  const captionDim = embed ? interpolate(t - embed.start, [0, 0.2, embed.duration - 0.25, embed.duration], [1, 0.3, 0.3, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
  const ended = p.endCard ? t >= p.duration : false;
  const lastFrame = Math.max(0, Math.round(p.duration * fps) - 1);
  const flash = interpolate(t, [0, 0.12], [0.55, 0], { extrapolateRight: "clamp" });

  const background = <Background video={p.video} crop={p.crop} zooms={p.zooms} edits={p.edits ?? []} />;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", fontFamily: fonts.body }}>
      {/* After the clip, the last frame holds still behind the end card. */}
      {ended ? <Freeze frame={lastFrame}>{background}</Freeze> : background}
      {split && !ended ? <Split g={split} t={t} brand={p.brand} /> : null}
      {/* Words behind the preacher: video -> hero word -> the preacher cut out on top. */}
      {embed && !ended && !cutaway && !insert ? <EmbedWord g={embed} t={t} framing={framing} brand={p.brand} /> : null}
      {!ended && !cutaway && !insert ? embeds.map((g, i) => <PersonLayer key={i} g={g} framing={framing} />) : null}
      {/* Soft top and bottom vignettes so text always reads (after the person layer, so it blends seamlessly). */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.6) 100%)",
        }}
      />
      {insert && !ended ? <Insert g={insert} t={t} /> : null}
      {cutaway && !ended ? <Cutaway g={cutaway} words={p.words} t={t} /> : null}
      {!ended ? <HookBar text={p.hook} brand={p.brand} /> : null}
      {!ended ? <Graphics graphics={p.graphics} brand={p.brand} t={t} /> : null}
      {p.lowerThird ? (
        <LowerThird name={p.lowerThird.name} church={p.lowerThird.church} brand={p.brand} hidden={!!cutaway || !!insert || !!split || panel} />
      ) : null}
      <AbsoluteFill style={{ opacity: captionDim }}>
        <Captions
          words={p.words}
          brand={p.brand}
          t={t}
          hidden={!!cutaway || ended}
          style={p.captionStyle}
          omit={embeds.map((g) => ({ word: g.word, start: g.start, end: g.start + g.duration }))}
        />
      </AbsoluteFill>
      {p.endCard ? (
        <EndCard start={p.duration} title={p.endCard.title} subtitle={p.endCard.subtitle} handle={p.endCard.handle} logo={p.endCard.logo} brand={p.brand} />
      ) : null}
      {flash > 0 ? <AbsoluteFill style={{ background: "#fff", opacity: flash }} /> : null}
      <Progress brand={p.brand} />
      <Sfx {...p} />
      {p.music ? <Music src={p.music} words={p.words} volume={p.musicVolume} /> : null}
    </AbsoluteFill>
  );
};
