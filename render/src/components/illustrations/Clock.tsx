import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A clock's hands race then slow; sun and moon trade places around it.
// Metaphor: time, seasons, timing, deadlines, waiting, "to everything there is a season".

export const Clock: React.FC<IllustrationProps> = ({ t, duration }) => {
  const show = ramp(t, 0, 0.6);
  // Fast at first, easing to a stop.
  const p = 1 - Math.pow(1 - Math.min(1, t / Math.max(duration, 0.1)), 3);
  const minute = p * 360 * 6;
  const hour = p * 360 * 0.5;
  const cx = W / 2;
  const cy = 1100;
  const orbit = p * Math.PI;
  return (
    <Scene t={t} duration={duration} origin="50% 57%">
      <Backdrop glowY={0.57} />
      {/* Sun and moon orbiting */}
      <circle cx={cx + Math.cos(Math.PI + orbit) * 420} cy={cy + Math.sin(Math.PI + orbit) * 300} r={60} fill={P.gold} opacity={show} />
      <g opacity={show}>
        <circle cx={cx + Math.cos(orbit) * 420} cy={cy + Math.sin(orbit) * 300} r={50} fill={P.cream} />
        <circle cx={cx + Math.cos(orbit) * 420 + 22} cy={cy + Math.sin(orbit) * 300 - 12} r={44} fill={P.navy} />
      </g>
      <g opacity={show} transform={`translate(${cx} ${cy}) scale(${0.85 + 0.15 * show})`}>
        <circle r={300} fill={P.gold} opacity="0.25" filter="url(#softer)" />
        <circle r={250} fill={P.navyDeep} stroke={P.gold} strokeWidth="22" />
        {Array.from({ length: 12 }, (_, i) => {
          const a = (i / 12) * Math.PI * 2;
          const big = i % 3 === 0;
          return (
            <line key={i} x1={Math.cos(a) * (big ? 180 : 200)} y1={Math.sin(a) * (big ? 180 : 200)} x2={Math.cos(a) * 225} y2={Math.sin(a) * 225} stroke={P.cream} strokeWidth={big ? 14 : 7} strokeLinecap="round" />
          );
        })}
        <line x1="0" y1="0" x2="0" y2="-120" stroke={P.cream} strokeWidth="20" strokeLinecap="round" transform={`rotate(${hour})`} />
        <line x1="0" y1="0" x2="0" y2="-185" stroke={P.gold} strokeWidth="12" strokeLinecap="round" transform={`rotate(${minute})`} />
        <circle r={20} fill={P.red} />
      </g>
      <Grain />
    </Scene>
  );
};
