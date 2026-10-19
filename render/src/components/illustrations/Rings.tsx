import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// Two wedding rings slide together and interlock, with a warm glow and sparkles.
// Metaphor: marriage, covenant, relationships, choosing a spouse, commitment.

const Ring: React.FC<{ x: number; y: number; tilt: number; front: boolean }> = ({ x, y, tilt, front }) => (
  <g transform={`translate(${x} ${y}) rotate(${tilt})`}>
    {/* Back half (darker) or front half (bright) of a ring seen at an angle */}
    <path
      d={front ? "M-200 0 A200 70 0 0 0 200 0" : "M-200 0 A200 70 0 0 1 200 0"}
      fill="none"
      stroke={front ? P.gold : P.goldDeep}
      strokeWidth="46"
      strokeLinecap="round"
    />
    {front ? <path d="M-170 22 A180 58 0 0 0 120 52" fill="none" stroke={P.cream} strokeWidth="10" strokeLinecap="round" opacity="0.8" /> : null}
  </g>
);

export const Rings: React.FC<IllustrationProps> = ({ t, duration }) => {
  const join = ramp(t, 0.1, 1.2);
  const spin = Math.sin(t * 1.2) * 4;
  const lx = W / 2 - 120 - 260 * (1 - join);
  const rx = W / 2 + 120 + 260 * (1 - join);
  const y = 1080;
  return (
    <Scene t={t} duration={duration} origin="50% 56%">
      <Backdrop glowY={0.56} />
      <circle cx={W / 2} cy={y} r={360} fill={P.gold} opacity={0.35 * join} filter="url(#softer)" />
      {/* Draw order makes the rings look interlocked: back halves first, then fronts */}
      <Ring x={lx} y={y} tilt={-24 + spin} front={false} />
      <Ring x={rx} y={y} tilt={24 - spin} front={false} />
      <Ring x={lx} y={y} tilt={-24 + spin} front />
      <Ring x={rx} y={y} tilt={24 - spin} front />
      {[0, 1, 2, 3].map((i) => {
        const s = ramp(t, 1.0 + i * 0.25, 1.3 + i * 0.25) * (1 - ramp(t, 1.6 + i * 0.25, 2.0 + i * 0.25));
        const [x, yy] = [[340, 860], [780, 900], [600, 1280], [430, 1250]][i];
        return <path key={i} d={`M${x} ${yy - 46 * s} L${x + 12 * s} ${yy} L${x} ${yy + 46 * s} L${x - 12 * s} ${yy} Z`} fill={P.cream} />;
      })}
      <Grain />
    </Scene>
  );
};
