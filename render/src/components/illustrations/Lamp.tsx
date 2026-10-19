import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// An oil lamp is lit; its flame flickers and the circle of light grows.
// Metaphor: the Word of God ("a lamp unto my feet"), revelation, insight, being a light, wisdom.

export const Lamp: React.FC<IllustrationProps> = ({ t, duration }) => {
  const lit = ramp(t, 0.2, 0.7);
  const glow = ramp(t, 0.4, Math.max(1, duration - 0.5));
  const flick = 1 + Math.sin(t * 17) * 0.05 + Math.sin(t * 29) * 0.04;
  const cx = W / 2;
  const fy = 1060;
  return (
    <Scene t={t} duration={duration} origin="50% 58%">
      <Backdrop glowY={0.6} />
      <circle cx={cx + 150} cy={fy} r={250 + 450 * glow} fill={P.gold} opacity={0.35 * lit} filter="url(#softer)" />
      <circle cx={cx + 150} cy={fy} r={120 + 120 * glow} fill={P.gold} opacity={0.45 * lit} filter="url(#soft)" />
      {/* Flame */}
      <g transform={`translate(${cx + 150} ${fy}) scale(${lit * flick} ${lit * (2 - flick)})`}>
        <path d="M0 0 C-40 -40 -30 -110 0 -170 C30 -110 40 -40 0 0 Z" fill={P.gold} />
        <path d="M0 -10 C-18 -40 -12 -80 0 -110 C12 -80 18 -40 0 -10 Z" fill={P.cream} />
      </g>
      {/* Lamp body */}
      <path d={`M${cx - 260} ${fy + 60} Q${cx - 60} ${fy + 260} ${cx + 160} ${fy + 40} L${cx + 120} ${fy + 10} Q${cx - 20} ${fy + 90} ${cx - 200} ${fy + 40} Z`} fill={P.goldDeep} />
      <path d={`M${cx - 260} ${fy + 60} Q${cx - 60} ${fy + 260} ${cx + 160} ${fy + 40}`} fill="none" stroke={P.cream} strokeWidth="6" opacity="0.6" />
      <ellipse cx={cx - 60} cy={fy + 40} rx={80} ry={22} fill={P.navyDeep} />
      <path d={`M${cx - 280} ${fy + 30} Q${cx - 340} ${fy + 60} ${cx - 290} ${fy + 110}`} fill="none" stroke={P.goldDeep} strokeWidth="22" strokeLinecap="round" />
      <ellipse cx={cx - 50} cy={fy + 250} rx={170} ry={26} fill={P.goldDeep} />
      <rect x={cx - 80} y={fy + 160} width={60} height={90} fill={P.goldDeep} />
      <Grain />
    </Scene>
  );
};
