import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A house draws itself line by line, its window lights up, and a key swings into view.
// Metaphor: home, rent, landlord, family, household, living with people.

export const House: React.FC<IllustrationProps> = ({ t, duration }) => {
  const draw = ramp(t, 0.1, 1.2);
  const light = ramp(t, 1.1, 1.5);
  const key = ramp(t, 1.0, 1.8);
  const outline = "M240 1400 L240 900 L540 640 L840 900 L840 1400 Z M180 950 L540 610 L900 950";
  const len = 3600;
  const swing = Math.sin(Math.max(0, t - 1.8) * 3) * 8 * Math.exp(-Math.max(0, t - 1.8));

  return (
    <Scene t={t} duration={duration} origin="50% 55%">
      <Backdrop glowY={0.6} />
      <g transform="translate(0 170)">
      <ellipse cx={W / 2} cy={1420} rx={460} ry={50} fill={P.navyDeep} opacity="0.8" />
      {/* Fill fades in once the outline is drawn */}
      <path d="M240 1400 L240 900 L540 640 L840 900 L840 1400 Z" fill={P.navySoft} opacity={0.8 * draw} />
      <path d={outline} stroke={P.gold} strokeWidth="20" fill="none" strokeLinejoin="round" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - draw)} />
      {/* Door and window */}
      <rect x={470} y={1150} width={140} height={250} rx={10} fill={P.navyDeep} opacity={draw} />
      <circle cx={585} cy={1280} r={9} fill={P.gold} opacity={draw} />
      <rect x={300} y={1000} width={130} height={110} rx={8} fill={P.gold} opacity={0.25 + 0.75 * light} />
      <rect x={650} y={1000} width={130} height={110} rx={8} fill={P.gold} opacity={0.25 + 0.75 * light} />
      <circle cx={365} cy={1055} r={120} fill={P.gold} opacity={0.3 * light} filter="url(#softer)" />
      <circle cx={715} cy={1055} r={120} fill={P.gold} opacity={0.3 * light} filter="url(#softer)" />
      {/* Key */}
      <g transform={`translate(${905} ${760 - 140 * (1 - key)}) rotate(${-25 + 25 * key + swing}) scale(0.8)`} opacity={key}>
        <circle cx="0" cy="0" r="62" fill="none" stroke={P.cream} strokeWidth="22" />
        <rect x="-11" y="56" width="22" height="210" rx="8" fill={P.cream} />
        <rect x="8" y="200" width="46" height="20" rx="6" fill={P.cream} />
        <rect x="8" y="240" width="34" height="20" rx="6" fill={P.cream} />
      </g>
      </g>
      <Grain />
    </Scene>
  );
};
