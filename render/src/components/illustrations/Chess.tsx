import { P, IllustrationProps, ramp } from "./palette";

// Perspective chessboard with silhouette pieces. A pawn advances; the camera drifts in.
// Metaphor: strategy, kingdom, planning, the opponent's plan.

const W = 1080;
const H = 1920;
const HORIZON = 640;
const CX = W / 2;
const SQ = 420; // width of one square at depth Z = 1, in pixels
const K = 1500; // vertical spread: depth Z = 1 sits at HORIZON + K

// Project board coordinates (X across in squares, Z depth >= 1) to the screen.
const proj = (X: number, Z: number) => ({ x: CX + (X * SQ) / Z, y: HORIZON + K / Z });

const Pawn: React.FC<{ s: number; c: string }> = ({ s, c }) => (
  <g transform={`scale(${s})`} fill={c}>
    <circle cx="0" cy="-118" r="26" />
    <path d="M-16 -96 Q0 -88 16 -96 L22 -40 Q36 -30 34 -14 L-34 -14 Q-36 -30 -22 -40 Z" />
    <rect x="-46" y="-16" width="92" height="16" rx="5" />
  </g>
);

const King: React.FC<{ s: number; c: string }> = ({ s, c }) => (
  <g transform={`scale(${s})`} fill={c}>
    <rect x="-6" y="-262" width="12" height="44" rx="3" />
    <rect x="-20" y="-248" width="40" height="12" rx="3" />
    <path d="M-30 -214 Q0 -230 30 -214 L24 -176 L-24 -176 Z" />
    <path d="M-24 -176 L24 -176 L34 -50 Q50 -38 46 -16 L-46 -16 Q-50 -38 -34 -50 Z" />
    <rect x="-58" y="-18" width="116" height="18" rx="6" />
  </g>
);

const Rook: React.FC<{ s: number; c: string }> = ({ s, c }) => (
  <g transform={`scale(${s})`} fill={c}>
    <path d="M-40 -170 h18 v16 h12 v-16 h20 v16 h12 v-16 h18 v40 h-80 Z" />
    <path d="M-30 -130 L30 -130 L36 -44 Q48 -34 46 -16 L-46 -16 Q-48 -34 -36 -44 Z" />
    <rect x="-56" y="-18" width="112" height="18" rx="6" />
  </g>
);

export const Chess: React.FC<IllustrationProps> = ({ t, duration }) => {
  const push = 1 + 0.08 * (t / Math.max(duration, 0.1));
  const advance = ramp(t, 0.4, 1.4); // the hero pawn moves one square forward

  // Board squares: X from -4..4, Z rows from near (1.0) to far (6.5)
  const rows = 14;
  const zs = Array.from({ length: rows + 1 }, (_, i) => 1 + i * 0.55);
  const squares: React.ReactElement[] = [];
  for (let r = 0; r < rows; r++) {
    for (let c = -5; c < 5; c++) {
      const a = proj(c, zs[r]);
      const b = proj(c + 1, zs[r]);
      const d = proj(c, zs[r + 1]);
      const e = proj(c + 1, zs[r + 1]);
      const dark = (r + c + 100) % 2 === 0;
      squares.push(
        <polygon
          key={`${r}-${c}`}
          points={`${a.x},${a.y} ${b.x},${b.y} ${e.x},${e.y} ${d.x},${d.y}`}
          fill={dark ? P.navySoft : P.gold}
          opacity={0.9}
        />,
      );
    }
  }

  // Place a piece standing on square (col, row); returns screen position + scale.
  const at = (col: number, row: number) => {
    const z = (zs[row] + zs[row + 1]) / 2;
    const p = proj(col + 0.5, z);
    return { x: p.x, y: p.y, s: 4.4 / z };
  };
  // Back rank of dark pieces (blurred, fills the upper frame), a few mid pieces, and light pieces near.
  const pieces = [
    ...[-4, -3, -2, -1, 0, 1, 2, 3].map((col, i) => ({
      kind: i === 4 ? "king" : i === 0 || i === 7 ? "rook" : "pawn",
      col,
      row: 9,
      c: P.navyDeep,
    })),
    ...[-3, -1, 2].map((col) => ({ kind: "pawn", col, row: 6, c: P.navyDeep })),
    { kind: "king", col: 1, row: 4, c: P.navyDeep },
    { kind: "pawn", col: 2, row: 2, c: P.cream },
    { kind: "rook", col: -3, row: 1, c: P.cream },
  ];
  const hero = at(0, 1);
  const heroTo = at(0, 2);
  const hx = hero.x + (heroTo.x - hero.x) * advance;
  const hy = hero.y + (heroTo.y - hero.y) * advance;
  const hs = hero.s + (heroTo.s - hero.s) * advance;

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ transform: `scale(${push})`, transformOrigin: "50% 60%" }}>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={P.navyDeep} />
          <stop offset="1" stopColor={P.navy} />
        </linearGradient>
        <filter id="far"><feGaussianBlur stdDeviation="9" /></filter>
        <filter id="near"><feGaussianBlur stdDeviation="6" /></filter>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" />
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.09 0" />
        </filter>
        <radialGradient id="glow" cx="0.5" cy="0.45" r="0.6">
          <stop offset="0" stopColor={P.gold} stopOpacity="0.55" />
          <stop offset="1" stopColor={P.gold} stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width={W} height={H} fill="url(#sky)" />
      <rect width={W} height={H} fill="url(#glow)" />
      <g>{squares}</g>
      {pieces
        .sort((a, b) => b.row - a.row)
        .map((p, i) => {
          const q = at(p.col, p.row);
          const Comp = p.kind === "king" ? King : p.kind === "rook" ? Rook : Pawn;
          return (
            <g key={i} transform={`translate(${q.x},${q.y})`} filter={p.row >= 6 ? "url(#far)" : p.row <= 1 ? "url(#near)" : undefined}>
              <ellipse cx="0" cy="0" rx={60 * q.s} ry={14 * q.s} fill={P.navyDeep} opacity="0.35" />
              <Comp s={q.s} c={p.c} />
            </g>
          );
        })}
      {/* Hero pawn in the foreground, slightly soft like a shallow depth of field */}
      <g transform={`translate(${hx},${hy})`}>
        <ellipse cx="0" cy="0" rx={60 * hs} ry={14 * hs} fill={P.navyDeep} opacity="0.4" />
        <Pawn s={hs} c={P.navyDeep} />
      </g>
      <rect width={W} height={H} filter="url(#grain)" />
    </svg>
  );
};
