import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A balance scale: a weight drops onto one pan, the beam swings and settles.
// Metaphor: value for value, exchange, fairness, justice, reward.

const PIVOT_Y = 920;
const ARM = 340;

export const Scale: React.FC<IllustrationProps> = ({ t, duration }) => {
  const drop = ramp(t, 0.3, 0.8);
  // Damped swing after the weight lands.
  const since = Math.max(0, t - 0.8);
  const settle = -12 * (1 - Math.exp(-since * 2.5));
  const wobble = since > 0 ? 9 * Math.exp(-since * 2.2) * Math.sin(since * 9) : 0;
  const angle = settle + wobble; // degrees, negative = left side down
  const rad = (angle * Math.PI) / 180;
  const lx = W / 2 - ARM * Math.cos(rad);
  const ly = PIVOT_Y - ARM * Math.sin(rad);
  const rx = W / 2 + ARM * Math.cos(rad);
  const ry = PIVOT_Y + ARM * Math.sin(rad);
  const chain = 260;

  const Pan: React.FC<{ x: number; y: number; children?: React.ReactNode }> = ({ x, y, children }) => (
    <g>
      <line x1={x} y1={y} x2={x - 110} y2={y + chain} stroke={P.cream} strokeWidth="4" />
      <line x1={x} y1={y} x2={x + 110} y2={y + chain} stroke={P.cream} strokeWidth="4" />
      <path d={`M${x - 150} ${y + chain} Q${x} ${y + chain + 90} ${x + 150} ${y + chain} Z`} fill={P.gold} />
      {children}
    </g>
  );

  return (
    <Scene t={t} duration={duration} origin="50% 50%">
      <Backdrop glowY={0.5} />
      {/* Stand */}
      <rect x={W / 2 - 16} y={PIVOT_Y} width={32} height={600} fill={P.goldDeep} />
      <path d={`M${W / 2 - 220} 1500 Q${W / 2} 1430 ${W / 2 + 220} 1500 Z`} fill={P.goldDeep} />
      {/* Beam */}
      <line x1={lx} y1={ly} x2={rx} y2={ry} stroke={P.gold} strokeWidth="22" strokeLinecap="round" />
      <circle cx={W / 2} cy={PIVOT_Y} r={34} fill={P.cream} />
      {/* Left pan gets the weight */}
      <Pan x={lx} y={ly}>
        <g transform={`translate(${lx} ${ly + chain - 30 - 600 * (1 - drop)})`} opacity={drop > 0 ? 1 : 0}>
          <path d="M-70 0 L70 0 L50 -110 L-50 -110 Z" fill={P.cream} />
          <rect x="-26" y="-140" width="52" height="34" rx="10" fill="none" stroke={P.cream} strokeWidth="10" />
        </g>
      </Pan>
      {/* Right pan holds coins */}
      <Pan x={rx} y={ry}>
        {[0, 1, 2].map((k) => (
          <ellipse key={k} cx={rx - 40 + k * 40} cy={ry + chain - 18 - (k === 1 ? 20 : 0)} rx={40} ry={14} fill={P.cream} />
        ))}
      </Pan>
      <Grain />
    </Scene>
  );
};
