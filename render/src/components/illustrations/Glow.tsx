import { Backdrop, Grain, Scene, W } from "./common";
import { IllustrationProps, P, ramp } from "./palette";

// Neutral placeholder: drifting bokeh lights. Used when a clip asks for an illustration not drawn yet.

export const Glow: React.FC<IllustrationProps> = ({ t, duration }) => {
  const show = ramp(t, 0, 0.8);
  return (
    <Scene t={t} duration={duration}>
      <Backdrop glowY={0.6} />
      {Array.from({ length: 22 }, (_, i) => {
        const x = (i * 263) % W;
        const y = 820 + ((i * 197) % 900) - t * (20 + (i % 5) * 12);
        const r = 30 + ((i * 41) % 90);
        return <circle key={i} cx={x} cy={y} r={r} fill={i % 3 ? P.gold : P.cream} opacity={(0.12 + (i % 4) * 0.06) * show} filter="url(#soft)" />;
      })}
      <Grain />
    </Scene>
  );
};
