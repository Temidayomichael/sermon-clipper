import { Backdrop, Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A door swings open and light floods out across the floor.
// Metaphor: open doors, opportunity, a new season, access, favour, breakthrough.

export const Door: React.FC<IllustrationProps> = ({ t, duration }) => {
  const open = ramp(t, 0.3, 1.5);
  const x0 = 360;
  const x1 = 720;
  const top = 760;
  const bottom = 1420;
  // The door leaf swings toward the viewer: its far edge moves left and grows taller.
  const edgeX = x1 - (x1 - x0) * 1.15 * open;
  const grow = 70 * open;

  return (
    <Scene t={t} duration={duration} origin="50% 58%">
      <Backdrop glowY={0.6} />
      {/* Wall */}
      <rect x="0" y="560" width={W} height={bottom - 560} fill={P.navyDeep} opacity="0.85" />
      {/* Light pouring through the frame */}
      <rect x={x0} y={top} width={x1 - x0} height={bottom - top} fill={P.cream} opacity={0.25 + 0.75 * open} />
      <polygon points={`${x0},${bottom} ${x1},${bottom} ${x1 + 520 * open},${H} ${x0 - 520 * open},${H}`} fill={P.gold} opacity={0.55 * open} />
      <circle cx={(x0 + x1) / 2} cy={(top + bottom) / 2} r={420} fill={P.gold} opacity={0.4 * open} filter="url(#softer)" />
      {/* Frame */}
      <rect x={x0 - 26} y={top - 26} width={x1 - x0 + 52} height={bottom - top + 26} fill="none" stroke={P.gold} strokeWidth="22" />
      {/* Door leaf */}
      <polygon points={`${x0},${top} ${edgeX},${top - grow} ${edgeX},${bottom + grow} ${x0},${bottom}`} fill={P.navySoft} stroke={P.goldDeep} strokeWidth="6" />
      <circle cx={x0 + (edgeX - x0) * 0.86} cy={(top + bottom) / 2} r={14} fill={P.gold} />
      {/* Floor */}
      <rect x="0" y={bottom} width={W} height={H - bottom} fill={P.navy} opacity="0.6" />
      <Grain />
    </Scene>
  );
};
