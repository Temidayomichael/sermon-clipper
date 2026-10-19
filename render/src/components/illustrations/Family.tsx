import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A family steps into the light one by one and joins hands.
// Metaphor: family, children, parenting, generations, inheritance, community, the church family.

const Person: React.FC<{ x: number; base: number; h: number; c: string; show: number }> = ({ x, base, h, c, show }) => {
  const head = h * 0.13;
  return (
    <g opacity={show} transform={`translate(${x} ${base + 40 * (1 - show)})`}>
      <circle cx="0" cy={-h + head} r={head} fill={c} />
      <path d={`M${-h * 0.16} ${-h + head * 2.3} Q0 ${-h + head * 1.9} ${h * 0.16} ${-h + head * 2.3} L${h * 0.2} ${-h * 0.42} L${-h * 0.2} ${-h * 0.42} Z`} fill={c} />
      <rect x={-h * 0.15} y={-h * 0.44} width={h * 0.12} height={h * 0.44} rx={h * 0.04} fill={c} />
      <rect x={h * 0.03} y={-h * 0.44} width={h * 0.12} height={h * 0.44} rx={h * 0.04} fill={c} />
    </g>
  );
};

export const Family: React.FC<IllustrationProps> = ({ t, duration }) => {
  const base = 1440;
  const people = [
    { x: 300, h: 560, c: P.navyDeep, at: 0.1 },
    { x: 460, h: 330, c: P.navySoft, at: 0.45 },
    { x: 620, h: 280, c: P.navySoft, at: 0.7 },
    { x: 790, h: 520, c: P.navyDeep, at: 0.3 },
  ];
  const hands = ramp(t, 1.0, 1.5);
  const glow = ramp(t, 0, 1.2);
  return (
    <Scene t={t} duration={duration} origin="50% 62%">
      <Backdrop glowY={0.62} />
      <circle cx={W / 2} cy={1150} r={460} fill={P.gold} opacity={0.75 * glow} filter="url(#softer)" />
      <circle cx={W / 2} cy={1150} r={280} fill={P.gold} opacity={0.9 * glow} />
      <ellipse cx={W / 2} cy={base + 8} rx={460} ry={36} fill={P.navyDeep} opacity="0.7" />
      {people.map((p, i) => (
        <Person key={i} x={p.x} base={base} h={p.h} c={p.c} show={ramp(t, p.at, p.at + 0.5)} />
      ))}
      {/* Joined hands: arcs between neighbours */}
      {[[0, 1], [1, 2], [2, 3]].map(([a, b], i) => {
        const pa = people[a];
        const pb = people[b];
        const ya = base - pa.h * 0.5;
        const yb = base - pb.h * 0.5;
        return (
          <path key={i} d={`M${pa.x + 50} ${ya} Q${(pa.x + pb.x) / 2} ${Math.max(ya, yb) + 50} ${pb.x - 50} ${yb}`} stroke={P.navyDeep} strokeWidth="26" fill="none" strokeLinecap="round" opacity={hands} />
        );
      })}
      <Grain />
    </Scene>
  );
};
