import { useMemo } from "react";
import { AbsoluteFill, Easing, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { H, W } from "../types";

const SRC_ASPECT = 16 / 9;
const FIT_TOP = 380; // where the full frame sits in "fit" mode (below the hook bar)
const VIDEO_TOP = 330; // the cropped video starts below the hook bar so it never covers his face

/** Jump-cut framing: alternate between wide and tight at each edit (skipping edits under 1.2 s apart). */
function jumpLevel(t: number, edits: number[]): number {
  let level = 0;
  let lastToggle = -10;
  for (const e of edits) {
    if (e > t) break;
    if (e - lastToggle >= 1.2) {
      level ^= 1;
      lastToggle = e;
    }
  }
  return level ? 1.09 : 1;
}

/** Punch-in zoom: quick ease in, hold, gentle ease out. */
function zoomAt(t: number, zooms: number[]): number {
  let z = 1;
  for (const s of zooms) {
    const v = interpolate(t, [s - 0.05, s + 0.22, s + 2.2, s + 2.6], [1, 1.12, 1.12, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
    z = Math.max(z, v);
  }
  return z;
}

/** Box-blur a per-frame series so values glide, without blurring across camera cuts (shot ids differ). */
function smooth(raw: number[], win: number, shot?: number[]): number[] {
  return raw.map((_, i) => {
    let sum = 0;
    let n = 0;
    for (let k = Math.max(0, i - win); k <= Math.min(raw.length - 1, i + win); k++) {
      if (shot && shot[k] !== shot[i]) continue;
      sum += raw[k];
      n++;
    }
    return sum / n;
  });
}

export const Background: React.FC<{
  video: string;
  crop: { t: number; x: number; fit?: boolean; cut?: boolean }[];
  zooms: number[];
  edits: number[];
}> = ({ video, crop, zooms, edits }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  // Per-frame face x and layout mode, smoothed so the virtual camera pans like an operator
  // and cross-fades between the vertical crop and the full-frame layout.
  const { xs, fits } = useMemo(() => {
    const rawX: number[] = [];
    const rawFit: number[] = [];
    const shot: number[] = [];
    let k = 0;
    let s = 0;
    for (let f = 0; f < durationInFrames; f++) {
      const tt = f / fps;
      while (k + 1 < crop.length && crop[k + 1].t <= tt) {
        k++;
        if (crop[k].cut) s++;
      }
      rawX.push(crop[k]?.x ?? 0.5);
      rawFit.push(crop[k]?.fit ? 1 : 0);
      shot.push(s);
    }
    return { xs: smooth(rawX, Math.round(fps * 0.5), shot), fits: smooth(rawFit, Math.round(fps * 0.12)) };
  }, [crop, fps, durationInFrames]);

  if (!video) {
    return <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 35%, #3a3f4b, #0d0e12 70%)" }} />;
  }

  const i = Math.min(frame, xs.length - 1);
  const fit = fits[i] ?? 0;
  const src = staticFile(video);

  // Vertical crop that follows the face.
  const zoom = jumpLevel(t, edits) * zoomAt(t, zooms) * interpolate(frame, [0, durationInFrames], [1, 1.03]);
  const boxH = H - VIDEO_TOP;
  const vh = boxH * zoom;
  const vw = vh * SRC_ASPECT;
  const left = Math.min(0, Math.max(W - vw, W / 2 - (xs[i] ?? 0.5) * vw));
  const top = -(vh - boxH) * 0.3; // zoom toward the upper third, where faces sit

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* Always mounted: this layer carries the sermon audio, even while the full-frame layout shows. */}
      <AbsoluteFill style={{ opacity: 1 - fit }}>
        {/* Top band behind the hook bar: a dark, blurred copy of the shot. */}
        <OffthreadVideo
          src={src}
          muted
          style={{
            position: "absolute",
            height: VIDEO_TOP * 2.2,
            width: VIDEO_TOP * 2.2 * SRC_ASPECT,
            left: (W - VIDEO_TOP * 2.2 * SRC_ASPECT) / 2,
            top: -VIDEO_TOP * 0.6,
            maxWidth: "none",
            filter: "blur(30px) brightness(0.35) saturate(1.3)",
          }}
        />
        <div style={{ position: "absolute", top: VIDEO_TOP, left: 0, width: W, height: boxH, overflow: "hidden" }}>
          <OffthreadVideo src={src} style={{ position: "absolute", width: vw, height: vh, left, top, maxWidth: "none" }} />
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: 90,
              background: "linear-gradient(180deg, rgba(0,0,0,0.55), rgba(0,0,0,0))",
            }}
          />
        </div>
      </AbsoluteFill>
      {fit > 0 ? (
        <AbsoluteFill style={{ opacity: fit }}>
          {/* Blurred, zoomed copy fills the canvas behind the full frame. */}
          <OffthreadVideo
            src={src}
            muted
            style={{
              position: "absolute",
              height: H,
              width: H * SRC_ASPECT,
              left: (W - H * SRC_ASPECT) / 2,
              top: 0,
              maxWidth: "none",
              filter: "blur(40px) brightness(0.45) saturate(1.2)",
            }}
          />
          <OffthreadVideo
            src={src}
            muted
            style={{
              position: "absolute",
              width: W,
              height: W / SRC_ASPECT,
              left: 0,
              top: FIT_TOP,
              boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
            }}
          />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
