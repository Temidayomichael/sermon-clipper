import { P } from "./palette";

export const W = 1080;
export const H = 1920;

/** Shared backdrop: navy gradient, warm glow, and the filters every scene uses. */
export const Backdrop: React.FC<{ glowY?: number }> = ({ glowY = 0.45 }) => (
  <>
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor={P.navyDeep} />
        <stop offset="1" stopColor={P.navy} />
      </linearGradient>
      <radialGradient id="warm" cx="0.5" cy={glowY} r="0.65">
        <stop offset="0" stopColor={P.gold} stopOpacity="0.6" />
        <stop offset="0.6" stopColor={P.gold} stopOpacity="0.12" />
        <stop offset="1" stopColor={P.gold} stopOpacity="0" />
      </radialGradient>
      <filter id="soft"><feGaussianBlur stdDeviation="8" /></filter>
      <filter id="softer"><feGaussianBlur stdDeviation="18" /></filter>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" />
        <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.09 0" />
      </filter>
    </defs>
    <rect width={W} height={H} fill="url(#bg)" />
    <rect width={W} height={H} fill="url(#warm)" />
  </>
);

export const Grain: React.FC = () => <rect width={W} height={H} filter="url(#grain)" />;

/** SVG wrapper with a slow camera push-in over the cutaway. */
export const Scene: React.FC<{ t: number; duration: number; origin?: string; children: React.ReactNode }> = ({
  t,
  duration,
  origin = "50% 60%",
  children,
}) => (
  <svg
    width={W}
    height={H}
    viewBox={`0 0 ${W} ${H}`}
    style={{ transform: `scale(${1 + 0.07 * (t / Math.max(duration, 0.1))})`, transformOrigin: origin }}
  >
    {children}
  </svg>
);
