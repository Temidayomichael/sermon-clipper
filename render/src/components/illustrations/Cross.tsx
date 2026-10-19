import { Backdrop, Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A cross on a hill at sunrise; clouds part and light spreads.
// Metaphor: salvation, the finished work of Christ, redemption, forgiveness, the gospel, mercy.

export const Cross: React.FC<IllustrationProps> = ({ t, duration }) => {
  const rise = ramp(t, 0, 1.4);
  const part = ramp(t, 0.3, 1.6);
  const cx = W / 2;
  const hill = 1340;
  const rays = Array.from({ length: 14 }, (_, i) => {
    const a = Math.PI + (i / 13) * Math.PI;
    const r = 1300 * rise;
    return (
      <polygon key={i} points={`${cx},${hill - 300} ${cx + Math.cos(a - 0.05) * r},${hill - 300 + Math.sin(a - 0.05) * r} ${cx + Math.cos(a + 0.05) * r},${hill - 300 + Math.sin(a + 0.05) * r}`} fill={P.gold} opacity={i % 2 ? 0.14 : 0.26} />
    );
  });
  return (
    <Scene t={t} duration={duration} origin="50% 60%">
      <Backdrop glowY={0.6} />
      {rays}
      <circle cx={cx} cy={hill - 120 - 200 * rise} r={190} fill={P.gold} opacity="0.85" />
      <circle cx={cx} cy={hill - 120 - 200 * rise} r={330} fill={P.gold} opacity="0.35" filter="url(#softer)" />
      {/* Clouds parting */}
      <ellipse cx={cx - 300 - 260 * part} cy={820} rx={330} ry={90} fill={P.navyDeep} opacity="0.9" />
      <ellipse cx={cx + 300 + 260 * part} cy={880} rx={330} ry={90} fill={P.navyDeep} opacity="0.9" />
      {/* Hill */}
      <path d={`M0 ${hill + 60} Q${cx} ${hill - 80} ${W} ${hill + 60} L${W} ${H} L0 ${H} Z`} fill={P.navyDeep} />
      {/* Cross */}
      <rect x={cx - 26} y={hill - 560} width={52} height={520} fill={P.navyDeep} />
      <rect x={cx - 170} y={hill - 450} width={340} height={48} fill={P.navyDeep} />
      <Grain />
    </Scene>
  );
};
