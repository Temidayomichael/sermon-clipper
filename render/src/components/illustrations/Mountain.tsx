import { Backdrop, Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// The sun rises behind a mountain while a path climbs to the peak and a flag is planted.
// Metaphor: obstacles, climbing, vision, goals, the high place, perseverance, "speak to the mountain".

export const Mountain: React.FC<IllustrationProps> = ({ t, duration }) => {
  const sun = ramp(t, 0, 1.6);
  const path = ramp(t, 0.3, Math.max(1.2, duration - 0.8));
  const flag = ramp(t, duration - 0.8, duration - 0.3);
  const len = 1500;
  const peak = { x: 540, y: 820 };
  return (
    <Scene t={t} duration={duration} origin="50% 60%">
      <Backdrop glowY={0.5} />
      <circle cx={peak.x + 40} cy={peak.y + 220 - 280 * sun} r={150} fill={P.gold} />
      <circle cx={peak.x + 40} cy={peak.y + 220 - 280 * sun} r={260} fill={P.gold} opacity="0.4" filter="url(#softer)" />
      {/* Far range */}
      <path d={`M0 1260 L220 980 L380 1120 L${peak.x} ${peak.y} L760 1060 L900 960 L${W} 1180 L${W} ${H} L0 ${H} Z`} fill={P.navySoft} />
      {/* Snow cap */}
      <path d={`M${peak.x - 70} ${peak.y + 90} L${peak.x} ${peak.y} L${peak.x + 80} ${peak.y + 100} L${peak.x + 30} ${peak.y + 80} L${peak.x} ${peak.y + 110} Z`} fill={P.cream} />
      {/* Near range */}
      <path d={`M0 1420 L300 1200 L520 1380 L740 1240 L${W} 1440 L${W} ${H} L0 ${H} Z`} fill={P.navyDeep} />
      {/* Switchback path up to the peak */}
      <path
        d={`M380 1600 L640 1440 L420 1300 L650 1150 L470 1020 L${peak.x} ${peak.y + 30}`}
        stroke={P.gold}
        strokeWidth="12"
        strokeDasharray={`${len}`}
        strokeDashoffset={len * (1 - path)}
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Flag */}
      <g transform={`translate(${peak.x} ${peak.y + 10})`} opacity={flag}>
        <rect x="-4" y={-150 * flag} width="8" height={150 * flag} fill={P.cream} />
        <path d={`M4 ${-150 * flag} L${90 + Math.sin(t * 8) * 8} ${-125 * flag} L4 ${-100 * flag} Z`} fill={P.red} />
      </g>
      <Grain />
    </Scene>
  );
};
