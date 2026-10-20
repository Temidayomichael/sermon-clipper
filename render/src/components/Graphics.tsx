import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fonts } from "../fonts";
import { Brand, Graphic, GRAPHIC_TOP } from "../types";

/** 0→1 entrance spring and 1→0 exit fade for a graphic. */
function useLife(start: number, duration: number) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(start * fps);
  const enter = spring({ frame: frame - f0, fps, config: { damping: 13, stiffness: 170 } });
  const exit = interpolate(frame, [f0 + (duration - 0.35) * fps, f0 + duration * fps], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return { enter, exit, local: (frame - f0) / fps };
}

const Panel: React.FC<{ brand: Brand; children: React.ReactNode; enter: number; exit: number }> = ({
  brand,
  children,
  enter,
  exit,
}) => (
  <div
    style={{
      position: "absolute",
      top: GRAPHIC_TOP,
      left: 70,
      right: 70,
      background: brand.panel,
      border: "2px solid rgba(255,255,255,0.12)",
      borderRadius: 28,
      padding: "30px 40px",
      color: brand.text,
      boxShadow: "0 24px 60px rgba(0,0,0,0.5)",
      opacity: exit * enter,
      transform: `translateY(${(1 - enter) * 80}px) scale(${0.92 + 0.08 * enter})`,
      backdropFilter: "blur(8px)",
    }}
  >
    {children}
  </div>
);

const Keyword: React.FC<{ g: Extract<Graphic, { type: "keyword" }>; brand: Brand }> = ({ g, brand }) => {
  const { enter, exit } = useLife(g.start, g.duration);
  return (
    <div
      style={{
        position: "absolute",
        top: GRAPHIC_TOP + 30,
        left: 0,
        right: 0,
        textAlign: "center",
        fontFamily: fonts.display,
        fontSize: g.text.length > 12 ? 120 : 160,
        lineHeight: 1,
        textTransform: "uppercase",
        color: brand.accent,
        WebkitTextStroke: "14px #000",
        paintOrder: "stroke fill",
        textShadow: "0 14px 40px rgba(0,0,0,0.6)",
        opacity: exit,
        transform: `scale(${1.6 - 0.6 * enter}) rotate(${(1 - enter) * -6}deg)`,
      }}
    >
      {g.text}
    </div>
  );
};

const List: React.FC<{ g: Extract<Graphic, { type: "list" }>; brand: Brand }> = ({ g, brand }) => {
  const { enter, exit, local } = useLife(g.start, g.duration);
  const step = (g.duration * 0.6) / Math.max(1, g.items.length);
  return (
    <Panel brand={brand} enter={enter} exit={exit}>
      <div style={{ fontFamily: fonts.display, fontSize: 54, color: brand.accent, textTransform: "uppercase", marginBottom: 14 }}>
        {g.title}
      </div>
      {g.items.map((item, i) => {
        const at = g.itemOffsets?.[i] ?? 0.25 + i * step;
        const shown = interpolate(local, [at, at + 0.2], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 20,
              fontWeight: 800,
              fontSize: 48,
              margin: "10px 0",
              opacity: shown,
              transform: `translateX(${(1 - shown) * -40}px)`,
            }}
          >
            <span
              style={{
                width: 56,
                height: 56,
                borderRadius: 14,
                background: brand.accent,
                color: "#111",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: fonts.display,
                fontSize: 36,
                flexShrink: 0,
              }}
            >
              {i + 1}
            </span>
            {item}
          </div>
        );
      })}
    </Panel>
  );
};

const Scripture: React.FC<{ g: Extract<Graphic, { type: "scripture" }>; brand: Brand }> = ({ g, brand }) => {
  const { enter, exit } = useLife(g.start, g.duration);
  return (
    <Panel brand={brand} enter={enter} exit={exit}>
      <div
        style={{
          display: "inline-block",
          fontSize: 24,
          fontWeight: 800,
          letterSpacing: 3,
          background: "rgba(255,255,255,0.12)",
          padding: "6px 14px",
          borderRadius: 8,
          marginBottom: 12,
        }}
      >
        SCRIPTURE
      </div>
      <div style={{ fontFamily: fonts.display, fontSize: 64, color: brand.accent, textTransform: "uppercase" }}>{g.ref}</div>
      {g.text ? (
        <div style={{ fontSize: 40, fontWeight: 600, lineHeight: 1.3, marginTop: 10, fontStyle: "italic" }}>“{g.text}”</div>
      ) : null}
    </Panel>
  );
};

const Quote: React.FC<{ g: Extract<Graphic, { type: "quote" }>; brand: Brand }> = ({ g, brand }) => {
  const { enter, exit } = useLife(g.start, g.duration);
  return (
    <Panel brand={brand} enter={enter} exit={exit}>
      <div style={{ display: "flex", gap: 22 }}>
        <div style={{ width: 10, borderRadius: 5, background: brand.accent, flexShrink: 0 }} />
        <div>
          <div style={{ fontFamily: fonts.display, fontSize: 90, lineHeight: 0.6, color: brand.accent, height: 46 }}>“</div>
          <div style={{ fontSize: 50, fontWeight: 800, lineHeight: 1.22 }}>{g.text}</div>
        </div>
      </div>
    </Panel>
  );
};

export const Graphics: React.FC<{ graphics: Graphic[]; brand: Brand; t: number }> = ({ graphics, brand, t }) => {
  // Only one graphic at a time: the most recent one that is still live.
  const live = graphics.filter((g) => !["cutaway", "insert", "split", "embed"].includes(g.type) && t >= g.start && t < g.start + g.duration);
  const g = live[live.length - 1];
  if (!g) return null;
  switch (g.type) {
    case "keyword":
      return <Keyword g={g} brand={brand} />;
    case "list":
      return <List g={g} brand={brand} />;
    case "scripture":
      return <Scripture g={g} brand={brand} />;
    case "quote":
      return <Quote g={g} brand={brand} />;
    default:
      return null;
  }
};
