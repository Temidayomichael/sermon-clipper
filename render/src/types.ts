export type Word = { w: string; start: number; end: number; hl: boolean };

export type Graphic =
  | { type: "keyword"; start: number; duration: number; text: string }
  | { type: "list"; start: number; duration: number; title: string; items: string[]; itemOffsets?: number[] }
  | { type: "scripture"; start: number; duration: number; ref: string; text?: string }
  | { type: "quote"; start: number; duration: number; text: string }
  | CutawayGraphic;

/** Full-screen illustrated cutaway. `visual` is an illustration name or "broll:<file in public/broll>". */
export type CutawayGraphic = {
  type: "cutaway";
  start: number;
  duration: number;
  visual: string;
  emphasis?: string[];
  keyword?: string;
};

export type Brand = { accent: string; panel: string; text: string };

export type ClipProps = {
  id: string;
  hook: string;
  duration: number;
  fps: number;
  video: string;
  music: string | null;
  words: Word[];
  graphics: Graphic[];
  zooms: number[];
  edits?: number[];
  crop: { t: number; x: number; fit?: boolean; cut?: boolean }[];
  brand: Brand;
  sfxVolume: number;
  musicVolume: number;
};

// Layout bands on the 1080x1920 canvas (bottom ~380px stays clear for platform UI).
export const W = 1080;
export const H = 1920;
export const HOOK_TOP = 150;
export const GRAPHIC_TOP = 960;
export const CAPTION_TOP = 1380;
