# Rules files

Copy [example/style.json](example/style.json) and [example/print.json](example/print.json), then change values. Every field is required, so a saved file keeps meaning the same thing. `ink.py render` names each missing, unknown or out-of-range field. Colours are `#rrggbb`, and lengths are printed mm.

## `style.json`

| Field | Controls |
| --- | --- |
| `ink.color`, `ink.width_mm` | Pen colour and width. |
| `ink.wobble_mm` | How far an outline strays. 0 is ruled straight, 0.35 is a steady hand, 1 is loose. |
| `ink.unevenness` | How much the line's weight varies, 0 to 1. |
| `lettering.label_font`, `lettering.title_font` | For labels: `Patrick Hand` (hand-drawn, narrow), `Itim` (hand-drawn, wide), `National Park` (clean), `Architects Daughter` (hand-lettered, wide), `Short Stack` (rounded marker, very wide) or `Comic Neue` (casual and clean). For titles: `Londrina Solid` (heavy and narrow), `Cabin Sketch` (wide and hatched by itself, with a `solid` fill), `Titan One` (heavy and rounded), `Sniglet` (bold and bubbly, wide) or `Knewave` (brush marker, slanted). |
| `lettering.title_fill` | `solid`, `hatched` or `outline`. |
| `lettering.title_outline_mm` | Outline of a hatched or outline title. |
| `hatch.angle_deg`, `hatch.spacing_mm`, `hatch.width_mm` | Hatching in shapes and titles. |
| `shadow.dx_mm`, `shadow.dy_mm`, `shadow.color` | Offset shadows. Positive is right and down. |
| `arrow.head`, `arrow.length_mm`, `arrow.angle_deg`, `arrow.weight` | `open`, `filled` or `none`; the barbs' length and half-angle; their weight against the shaft. |
| `cues.<name>.color`, `cues.<name>.treatment` | A colour cue's look: `fill`, `hatch` or `outline`. Use any number of cues, `{}` for none. |

## `print.json`

| Field | Controls |
| --- | --- |
| `paper.width_mm`, `paper.height_mm` | The sheet, either way round: each page's orientation turns it. A4 is 210 x 297, Letter 215.9 x 279.4. |
| `margins_mm.top`, `.right`, `.bottom`, `.left` | The safe margins of the page as it is read. |

For a print shop's bleed, the paper is the trim size plus the bleed on each side, and each margin is the bleed plus the safe zone.

## Fonts

[fonts/](fonts/) holds each face with its SIL Open Font License beside it. Patrick Hand, Itim, Londrina Solid, Cabin Sketch, Architects Daughter, Short Stack, Comic Neue, Titan One, Sniglet and Knewave are the google/fonts files unmodified; National Park is a static build of version 1.009. Pages embed the faces their style names.
