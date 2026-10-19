import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A lion's head emerges with its mane flaring and eyes catching the light.
// Metaphor: boldness, courage, authority, the Lion of Judah, "the righteous are bold as a lion".

export const Lion: React.FC<IllustrationProps> = ({ t, duration }) => {
  const show = ramp(t, 0.05, 0.9);
  const flare = ramp(t, 0.4, 1.3);
  const cx = W / 2;
  const cy = 1080;
  const spikes = 28;
  const mane = Array.from({ length: spikes * 2 }, (_, i) => {
    const a = (i / (spikes * 2)) * Math.PI * 2;
    const r = i % 2 === 0 ? 330 + 70 * flare + Math.sin(t * 3 + i) * 8 : 250;
    return `${cx + Math.cos(a) * r},${cy + Math.sin(a) * r * 1.05}`;
  }).join(" ");
  const blink = t > 1.9 && t < 2.0 ? 0.15 : 1;

  return (
    <Scene t={t} duration={duration} origin="50% 56%">
      <Backdrop glowY={0.56} />
      <g opacity={show} transform={`translate(0 ${80 * (1 - show)})`}>
        <circle cx={cx} cy={cy} r={420} fill={P.gold} opacity="0.3" filter="url(#softer)" />
        <polygon points={mane} fill={P.goldDeep} />
        <circle cx={cx} cy={cy} r={265} fill={P.gold} opacity="0.55" />
        {/* Face */}
        <path d={`M${cx - 170} ${cy - 90} Q${cx} ${cy - 230} ${cx + 170} ${cy - 90} Q${cx + 200} ${cy + 80} ${cx + 90} ${cy + 210} Q${cx} ${cy + 260} ${cx - 90} ${cy + 210} Q${cx - 200} ${cy + 80} ${cx - 170} ${cy - 90} Z`} fill={P.cream} />
        {/* Ears */}
        <circle cx={cx - 150} cy={cy - 150} r={48} fill={P.cream} />
        <circle cx={cx + 150} cy={cy - 150} r={48} fill={P.cream} />
        <circle cx={cx - 150} cy={cy - 150} r={24} fill={P.goldDeep} />
        <circle cx={cx + 150} cy={cy - 150} r={24} fill={P.goldDeep} />
        {/* Eyes */}
        <ellipse cx={cx - 72} cy={cy - 30} rx={30} ry={22 * blink} fill={P.navyDeep} />
        <ellipse cx={cx + 72} cy={cy - 30} rx={30} ry={22 * blink} fill={P.navyDeep} />
        <circle cx={cx - 64} cy={cy - 36} r={7 * blink} fill={P.gold} />
        <circle cx={cx + 80} cy={cy - 36} r={7 * blink} fill={P.gold} />
        {/* Muzzle and nose */}
        <path d={`M${cx - 40} ${cy + 50} L${cx + 40} ${cy + 50} L${cx} ${cy + 95} Z`} fill={P.navyDeep} />
        <path d={`M${cx} ${cy + 95} L${cx} ${cy + 140} M${cx} ${cy + 140} Q${cx - 50} ${cy + 170} ${cx - 80} ${cy + 140} M${cx} ${cy + 140} Q${cx + 50} ${cy + 170} ${cx + 80} ${cy + 140}`} stroke={P.navyDeep} strokeWidth="10" fill="none" strokeLinecap="round" />
      </g>
      <Grain />
    </Scene>
  );
};
