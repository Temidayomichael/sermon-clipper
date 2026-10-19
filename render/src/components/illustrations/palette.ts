// Duotone palette taken from the reference style: warm gold light, deep navy dark.
export const P = {
  gold: "#E9B824",
  goldDeep: "#C9951A",
  cream: "#F7E9BC",
  navy: "#14204A",
  navyDeep: "#0A1230",
  navySoft: "#2A3A73",
  red: "#D8262F",
};

export type IllustrationProps = {
  /** Seconds since the cutaway started. */
  t: number;
  /** Total cutaway length in seconds. */
  duration: number;
};

/** Clamp-and-ease helper: 0→1 between a and b (seconds). */
export const ramp = (t: number, a: number, b: number) => {
  const x = Math.min(1, Math.max(0, (t - a) / (b - a)));
  return x * x * (3 - 2 * x); // smoothstep
};
