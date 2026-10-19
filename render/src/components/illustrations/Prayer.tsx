import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A figure kneeling in prayer inside a beam of light, with sparks rising.
// Metaphor: prayer, intercession, waiting on God, fasting, devotion.

export const Prayer: React.FC<IllustrationProps> = ({ t, duration }) => {
  const beam = ramp(t, 0, 0.9);
  const hands = ramp(t, 0.2, 1.0);
  const cx = W / 2;
  const sparks = Array.from({ length: 16 }, (_, i) => {
    const life = ((t * 0.6 + i * 0.137) % 1);
    const x = cx + Math.sin(i * 2.3) * 180 * (0.4 + life);
    const y = 1180 - life * 520;
    return <circle key={i} cx={x} cy={y} r={6 + (i % 3) * 3} fill={P.cream} opacity={(1 - life) * 0.8 * beam} />;
  });
  return (
    <Scene t={t} duration={duration} origin="50% 60%">
      <Backdrop glowY={0.55} />
      {/* Beam from above */}
      <polygon points={`${cx - 60},0 ${cx + 60},0 ${cx + 340},1500 ${cx - 340},1500`} fill={P.gold} opacity={0.22 * beam} filter="url(#soft)" />
      <circle cx={cx} cy={1000} r={300} fill={P.gold} opacity={0.4 * beam} filter="url(#softer)" />
      {sparks}
      {/* Ground glow */}
      <ellipse cx={cx} cy={1450} rx={380} ry={50} fill={P.gold} opacity={0.35 * beam} />
      {/* Kneeling figure, facing right, head bowed, hands raised together */}
      <g transform={`translate(${cx - 590} ${40 * (1 - hands)})`} opacity={hands} fill={P.navyDeep} stroke={P.navyDeep} strokeLinejoin="round" strokeLinecap="round">
        <path d="M380 1448 L610 1448 L606 1396 L400 1404 Z" />
        <path d="M545 1448 L648 1448 L640 1200 L536 1196 Z" />
        <path d="M536 1210 L644 1210 C660 1110 664 1020 650 945 C620 925 585 922 556 932 C540 1020 530 1120 536 1210 Z" />
        <circle cx="648" cy="868" r="56" />
        <path d="M630 960 L730 1080 L728 905" fill="none" strokeWidth="44" />
        <path d="M612 975 L700 1070 L712 915" fill="none" strokeWidth="40" opacity="0.9" />
      </g>
      <Grain />
    </Scene>
  );
};
