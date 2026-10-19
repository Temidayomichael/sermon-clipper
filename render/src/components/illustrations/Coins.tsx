import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// Stacks of gold coins rise one after another with an arrow climbing over them.
// Metaphor: money, wealth, increase, profit, prosperity.

const BASE = 1520;
const COIN_W = 150;
const COIN_H = 34;

const Coin: React.FC<{ x: number; y: number; light?: boolean }> = ({ x, y, light }) => (
  <g>
    <rect x={x - COIN_W / 2} y={y - COIN_H} width={COIN_W} height={COIN_H} fill={light ? P.goldDeep : "#8E6A12"} />
    <ellipse cx={x} cy={y} rx={COIN_W / 2} ry={22} fill={light ? P.goldDeep : "#8E6A12"} />
    <ellipse cx={x} cy={y - COIN_H} rx={COIN_W / 2} ry={22} fill={light ? P.cream : P.gold} />
    <ellipse cx={x} cy={y - COIN_H} rx={COIN_W / 2 - 18} ry={13} fill="none" stroke={P.goldDeep} strokeWidth="4" />
  </g>
);

export const Coins: React.FC<IllustrationProps> = ({ t, duration }) => {
  const stacks = [3, 6, 9, 13];
  const xs = [210, 420, 650, 880];
  const span = Math.max(1.2, duration - 0.8);
  const arrow = ramp(t, 0.6, 0.6 + span);
  const tops = stacks.map((n, i) => BASE - n * COIN_H * ramp(t, 0.15 + i * 0.35, 0.65 + i * 0.35) - COIN_H);
  const pts = xs.map((x, i) => [x, tops[i] - 90] as const);
  const path = `M${pts[0][0] - 120} ${pts[0][1] + 140} ` + pts.map(([x, y]) => `L${x} ${y}`).join(" ");
  const len = 1400;

  return (
    <Scene t={t} duration={duration} origin="50% 70%">
      <Backdrop glowY={0.6} />
      <ellipse cx={W / 2} cy={BASE + 30} rx={520} ry={60} fill={P.navyDeep} opacity="0.7" />
      {stacks.map((n, i) => {
        const shown = Math.round(n * ramp(t, 0.15 + i * 0.35, 0.65 + i * 0.35));
        return (
          <g key={i}>
            {Array.from({ length: shown }, (_, k) => (
              <Coin key={k} x={xs[i]} y={BASE - k * COIN_H} light={k === shown - 1} />
            ))}
          </g>
        );
      })}
      <path d={path} stroke={P.cream} strokeWidth="16" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - arrow)} />
      {arrow > 0.95 ? (
        <path
          d={`M${pts[3][0] - 40} ${pts[3][1] - 10} L${pts[3][0] + 30} ${pts[3][1] - 40} L${pts[3][0] + 10} ${pts[3][1] + 30} Z`}
          fill={P.cream}
        />
      ) : null}
      {/* Sparkles */}
      {[0, 1, 2].map((i) => {
        const s = ramp(t, 1.4 + i * 0.3, 1.7 + i * 0.3) * (1 - ramp(t, 2.0 + i * 0.3, 2.4 + i * 0.3));
        const [x, y] = [[300, 1000], [760, 880], [560, 1150]][i];
        return <path key={i} d={`M${x} ${y - 40 * s} L${x + 10 * s} ${y} L${x} ${y + 40 * s} L${x - 10 * s} ${y} Z`} fill={P.cream} />;
      })}
      <Grain />
    </Scene>
  );
};
