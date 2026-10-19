import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";

const anton = loadAnton("normal", { weights: ["400"], subsets: ["latin"] });
const montserrat = loadMontserrat("normal", { weights: ["600", "800", "900"], subsets: ["latin"] });

export const fonts = {
  display: anton.fontFamily,
  body: montserrat.fontFamily,
};
