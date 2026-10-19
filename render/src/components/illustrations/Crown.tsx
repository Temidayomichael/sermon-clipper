import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// Rays of light open up and a crown descends into the glow.
// Metaphor: kingdom, God, glory, authority, calling, grace and mercy.

export const Crown: React.FC<IllustrationProps> = ({ t, duration }) => {
  const open = ramp(t, 0, 1.0);
  const descend = ramp(t, 0.3, 1.4);
  const rays = Array.from({ length: 18 }, (_, i) => {
    const a = (i / 18) * Math.PI * 2 + t * 0.15;
    const r1 = 120;
    const r2 = 1500 * open;
    const w = 0.07;
    const cx = W / 2;
    const cy = 1080;
    const p = (ang: number, r: number) => `${cx + Math.cos(ang) * r},${cy + Math.sin(ang) * r}`;
    return <polygon key={i} points={`${p(a - w, r1)} ${p(a - w * 1.8, r2)} ${p(a + w * 1.8, r2)} ${p(a + w, r1)}`} fill={P.gold} opacity={i % 2 ? 0.16 : 0.28} />;
  });
  const y = 1080 - 380 * (1 - descend);

  return (
    <Scene t={t} duration={duration} origin="50% 56%">
      <Backdrop glowY={0.56} />
      {rays}
      <circle cx={W / 2} cy={1080} r={260} fill={P.gold} opacity={0.55 * open} filter="url(#softer)" />
      <g transform={`translate(${W / 2} ${y})`} opacity={descend}>
        <path d="M-260 120 L-300 -150 L-150 -20 L0 -230 L150 -20 L300 -150 L260 120 Z" fill={P.cream} />
        <rect x="-270" y="110" width="540" height="70" rx="16" fill={P.gold} />
        {[-300, 0, 300].map((x, i) => (
          <circle key={i} cx={x} cy={i === 1 ? -240 : -160} r="26" fill={P.gold} />
        ))}
        {[-150, 0, 150].map((x, i) => (
          <circle key={i} cx={x} cy={145} r="16" fill={P.red} />
        ))}
      </g>
      <Grain />
    </Scene>
  );
};
