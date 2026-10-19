import { Backdrop, Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A field of wheat grows tall and sways in golden light.
// Metaphor: harvest, reaping, provision, abundance, increase, souls (the harvest is plenty).

export const Harvest: React.FC<IllustrationProps> = ({ t, duration }) => {
  const grow = ramp(t, 0, Math.max(1, duration * 0.6));
  const stalks = Array.from({ length: 26 }, (_, i) => {
    const x = 30 + i * 41 + ((i * 37) % 23);
    const h = (420 + ((i * 97) % 260)) * grow;
    const base = 1500 + ((i * 53) % 120);
    const sway = Math.sin(t * 1.8 + i * 0.6) * 22;
    const tipX = x + sway;
    const tipY = base - h;
    const front = i % 3 === 0;
    const col = front ? P.gold : P.goldDeep;
    return (
      <g key={i} opacity={front ? 1 : 0.75}>
        <path d={`M${x} ${base} Q${x + sway * 0.3} ${base - h * 0.5} ${tipX} ${tipY}`} stroke={col} strokeWidth={front ? 8 : 6} fill="none" />
        {grow > 0.3
          ? Array.from({ length: 6 }, (_, k) => {
              const yy = tipY + k * 26;
              const xx = tipX - (sway * k) / 40;
              return (
                <g key={k}>
                  <ellipse cx={xx - 14} cy={yy} rx={9} ry={20} fill={col} transform={`rotate(-25 ${xx - 14} ${yy})`} />
                  <ellipse cx={xx + 14} cy={yy} rx={9} ry={20} fill={col} transform={`rotate(25 ${xx + 14} ${yy})`} />
                </g>
              );
            })
          : null}
      </g>
    );
  });
  return (
    <Scene t={t} duration={duration} origin="50% 65%">
      <Backdrop glowY={0.55} />
      <circle cx={W / 2} cy={980} r={200} fill={P.gold} opacity="0.8" />
      <circle cx={W / 2} cy={980} r={380} fill={P.gold} opacity="0.35" filter="url(#softer)" />
      <rect x="0" y="1460" width={W} height={H - 1460} fill={P.navyDeep} />
      {stalks}
      <Grain />
    </Scene>
  );
};
