import { Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A small boat rocks on a stormy sea; lightning flashes, then light breaks through the clouds.
// Metaphor: trials, storms of life, fear, faith in the storm, Jesus calming the sea.

const wave = (t: number, base: number, amp: number, len: number, speed: number) => {
  let d = `M0 ${H} L0 ${base}`;
  for (let x = 0; x <= W; x += 30) d += ` L${x} ${base + Math.sin(x / len + t * speed) * amp + Math.sin(x / (len * 0.43) - t * speed * 1.3) * amp * 0.4}`;
  return d + ` L${W} ${H} Z`;
};

export const Storm: React.FC<IllustrationProps> = ({ t, duration }) => {
  const bolt = t > 0.55 && t < 0.75 ? 1 : t > 0.85 && t < 0.92 ? 0.6 : 0;
  const breakthrough = ramp(t, duration * 0.55, duration * 0.95);
  const rock = Math.sin(t * 2.6) * 9;
  const bob = Math.sin(t * 2.6 + 1) * 18;
  return (
    <Scene t={t} duration={duration} origin="50% 60%">
      <defs>
        <linearGradient id="stormsky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#060B1E" />
          <stop offset="1" stopColor={P.navy} />
        </linearGradient>
        <filter id="softer"><feGaussianBlur stdDeviation="18" /></filter>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="11" />
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.09 0" />
        </filter>
      </defs>
      <rect width={W} height={H} fill="url(#stormsky)" />
      {/* Light breaking through */}
      <polygon points={`${W * 0.62},700 ${W * 0.72},700 ${W * 0.95},1500 ${W * 0.35},1500`} fill={P.gold} opacity={0.35 * breakthrough} filter="url(#softer)" />
      <circle cx={W * 0.67} cy={720} r={170} fill={P.gold} opacity={0.6 * breakthrough} filter="url(#softer)" />
      {/* Clouds */}
      {[0, 1, 2, 3, 4].map((i) => (
        <ellipse key={i} cx={(i * 260 + t * 30) % (W + 300) - 150} cy={780 + (i % 2) * 70} rx={260} ry={90} fill="#0B1433" opacity="0.95" />
      ))}
      {/* Lightning */}
      {bolt > 0 ? (
        <>
          <rect width={W} height={H} fill={P.cream} opacity={0.18 * bolt} />
          <path d="M300 800 L250 960 L320 960 L240 1160" stroke={P.cream} strokeWidth="12" fill="none" opacity={bolt} strokeLinejoin="round" />
        </>
      ) : null}
      {/* Rain */}
      {Array.from({ length: 40 }, (_, i) => {
        const x = (i * 211) % W;
        const y = ((t * 1400 + i * 157) % 900) + 760;
        return <line key={i} x1={x} y1={y} x2={x - 24} y2={y + 60} stroke={P.cream} strokeOpacity="0.3" strokeWidth="4" />;
      })}
      {/* Sea */}
      <path d={wave(t, 1330, 46, 90, 2.2)} fill={P.navySoft} />
      {/* Boat */}
      <g transform={`translate(${W / 2} ${1330 + bob}) rotate(${rock})`}>
        <path d="M-200 -10 L200 -10 L150 70 L-150 70 Z" fill={P.gold} />
        <rect x="-6" y="-300" width="12" height="290" fill={P.cream} />
        <path d="M6 -290 L170 -40 L6 -40 Z" fill={P.cream} />
      </g>
      <path d={wave(t + 0.7, 1400, 54, 70, 2.8)} fill={P.navy} />
      <path d={wave(t + 1.4, 1480, 40, 110, 1.9)} fill={P.navyDeep} />
      <Grain />
    </Scene>
  );
};
