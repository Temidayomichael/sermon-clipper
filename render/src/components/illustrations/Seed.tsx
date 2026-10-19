import { Backdrop, Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// Rain falls, a seed drops into the soil, and a sprout grows and unfolds its leaves.
// Metaphor: sowing and reaping, work, growth, seasons, patience.

const GROUND = 1260;

export const Seed: React.FC<IllustrationProps> = ({ t, duration }) => {
  const drop = ramp(t, 0.1, 0.7); // seed falls into the soil
  const grow = ramp(t, 0.8, Math.max(1.6, duration - 0.6)); // stem grows
  const leaf1 = ramp(t, 1.2, 2.0);
  const leaf2 = ramp(t, 1.7, 2.6);
  const stemH = 520 * grow;
  const sway = Math.sin(t * 2.2) * 6 * grow;
  const tipX = W / 2 + sway;
  const tipY = GROUND - stemH;

  const rain = Array.from({ length: 46 }, (_, i) => {
    const x = (i * 197) % W;
    const speed = 900 + ((i * 53) % 400);
    const y = ((t * speed + i * 211) % (GROUND + 200)) - 150;
    return <line key={i} x1={x} y1={y} x2={x - 10} y2={y + 60} stroke={P.cream} strokeOpacity="0.35" strokeWidth="4" strokeLinecap="round" />;
  });

  return (
    <Scene t={t} duration={duration} origin="50% 65%">
      <Backdrop glowY={0.55} />
      {/* Sun behind clouds */}
      <circle cx={W / 2} cy={560} r={300} fill={P.gold} opacity="0.35" filter="url(#softer)" />
      {rain}
      {/* Soil with layers */}
      <path d={`M0 ${GROUND} Q${W / 2} ${GROUND - 40} ${W} ${GROUND} L${W} ${H} L0 ${H} Z`} fill={P.navyDeep} />
      <path d={`M0 ${GROUND + 120} Q${W / 2} ${GROUND + 80} ${W} ${GROUND + 120} L${W} ${H} L0 ${H} Z`} fill={P.navySoft} opacity="0.5" />
      {Array.from({ length: 14 }, (_, i) => (
        <ellipse key={i} cx={(i * 151) % W} cy={GROUND + 60 + ((i * 89) % 380)} rx={18} ry={9} fill={P.gold} opacity="0.18" />
      ))}
      {/* Seed */}
      <ellipse cx={W / 2} cy={600 + (GROUND + 30 - 600) * drop} rx={22} ry={32} fill={P.gold} transform={`rotate(${20 * drop} ${W / 2} ${600 + (GROUND + 30 - 600) * drop})`} />
      {/* Sprout */}
      {grow > 0 ? (
        <g>
          <path
            d={`M${W / 2} ${GROUND + 20} C${W / 2 - 30} ${GROUND - stemH * 0.4}, ${tipX + 30} ${GROUND - stemH * 0.7}, ${tipX} ${tipY}`}
            stroke={P.gold}
            strokeWidth="18"
            fill="none"
            strokeLinecap="round"
          />
          <g transform={`translate(${tipX - 6} ${tipY + stemH * 0.35}) rotate(${-40 - 20 * (1 - leaf1)}) scale(${leaf1})`}>
            <path d="M0 0 C-60 -80 -200 -60 -240 0 C-200 60 -60 70 0 0 Z" fill={P.gold} />
            <path d="M0 0 L-220 0" stroke={P.goldDeep} strokeWidth="5" />
          </g>
          <g transform={`translate(${tipX + 6} ${tipY + stemH * 0.15}) rotate(${30 + 20 * (1 - leaf2)}) scale(${leaf2})`}>
            <path d="M0 0 C60 -80 200 -60 240 0 C200 60 60 70 0 0 Z" fill={P.cream} />
            <path d="M0 0 L220 0" stroke={P.goldDeep} strokeWidth="5" />
          </g>
          <circle cx={tipX} cy={tipY} r={16} fill={P.cream} />
        </g>
      ) : null}
      <Grain />
    </Scene>
  );
};
