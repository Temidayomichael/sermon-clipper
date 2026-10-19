import { Chess } from "./Chess";
import { Clock } from "./Clock";
import { Coins } from "./Coins";
import { Cross } from "./Cross";
import { Crown } from "./Crown";
import { Door } from "./Door";
import { Family } from "./Family";
import { Glow } from "./Glow";
import { Harvest } from "./Harvest";
import { House } from "./House";
import { Lamp } from "./Lamp";
import { Lion } from "./Lion";
import { Mountain } from "./Mountain";
import { IllustrationProps } from "./palette";
import { Prayer } from "./Prayer";
import { Rings } from "./Rings";
import { Road } from "./Road";
import { Scale } from "./Scale";
import { Seed } from "./Seed";
import { Storm } from "./Storm";

/**
 * Animated illustrations available to cutaways. Keep the list (and the one-line meanings) in sync with
 * prompts/pick_clips.md. "glow" is the neutral placeholder for requested-but-not-yet-drawn visuals.
 */
export const ILLUSTRATIONS: Record<string, React.FC<IllustrationProps>> = {
  chess: Chess, // strategy, kingdom, planning, opposition
  seed: Seed, // sowing and reaping, work, growth
  coins: Coins, // money, wealth, increase, profit
  scale: Scale, // value exchange, fairness, justice, reward
  house: House, // home, rent, landlord, household
  crown: Crown, // God, kingdom, glory, authority
  prayer: Prayer, // prayer, intercession, fasting, devotion
  rings: Rings, // marriage, covenant, relationships
  storm: Storm, // trials, fear, faith in the storm
  lion: Lion, // boldness, courage, authority
  door: Door, // open doors, opportunity, new season
  mountain: Mountain, // obstacles, climbing, vision, goals
  road: Road, // choices, decisions, direction, journey
  lamp: Lamp, // the Word, revelation, wisdom
  clock: Clock, // time, seasons, timing, waiting
  cross: Cross, // salvation, redemption, mercy, the gospel
  family: Family, // family, children, generations
  harvest: Harvest, // harvest, provision, abundance, souls
  glow: Glow, // neutral placeholder
};
