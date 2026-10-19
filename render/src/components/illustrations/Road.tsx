import { Backdrop, Grain, H, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// A road runs toward the horizon and splits in two; lane markings rush toward the viewer.
// Metaphor: choices, decisions, direction, destiny, the narrow way, journey.

export const Road: React.FC<IllustrationProps> = ({ t, duration }) => {
  const split = ramp(t, 0.4, 1.4);
  const HZ = 860;
  const cx = W / 2;
  const dashes = Array.from({ length: 10 }, (_, i) => {
    const p = ((i / 10 + t * 0.45) % 1); // 0 at horizon -> 1 at bottom
    const y = HZ + 60 + Math.pow(p, 2.2) * (H - HZ);
    const h = 12 + p * 110;
    const w = 4 + p * 26;
    return <rect key={i} x={cx - w / 2} y={y} width={w} height={h} fill={P.cream} opacity={0.3 + 0.7 * p} />;
  });
  const fork = 1020;
  return (
    <Scene t={t} duration={duration} origin="50% 55%">
      <Backdrop glowY={0.45} />
      <circle cx={cx} cy={HZ} r={260} fill={P.gold} opacity="0.5" filter="url(#softer)" />
      {/* Ground */}
      <rect x="0" y={HZ} width={W} height={H - HZ} fill={P.navyDeep} />
      {/* Main road */}
      <polygon points={`${cx - 30},${fork} ${cx + 30},${fork} ${cx + 560},${H} ${cx - 560},${H}`} fill={P.navySoft} />
      {/* Two branches toward the horizon */}
      <polygon points={`${cx - 30},${fork} ${cx - 4},${fork} ${cx - 10 - 260 * split},${HZ} ${cx - 40 - 260 * split},${HZ}`} fill={P.navySoft} />
      <polygon points={`${cx + 4},${fork} ${cx + 30},${fork} ${cx + 40 + 260 * split},${HZ} ${cx + 10 + 260 * split},${HZ}`} fill={P.gold} opacity={0.4 + 0.6 * split} />
      {dashes}
      {/* Signpost */}
      <g transform={`translate(${cx + 290} 1240)`} opacity={split}>
        <rect x="-8" y="0" width="16" height="320" fill={P.goldDeep} />
        <path d="M-150 10 L120 10 L160 50 L120 90 L-150 90 Z" fill={P.gold} transform={`rotate(${-8 * split})`} />
        <path d="M150 120 L-120 120 L-160 160 L-120 200 L150 200 Z" fill={P.cream} transform={`rotate(${6 * split})`} />
      </g>
      <Grain />
    </Scene>
  );
};
