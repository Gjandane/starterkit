---
name: inking
description: "Inking: draw a printable sketchnote page in given style rules, render it at paper size, and check that no ink crosses a label. Use when a sketchnote sample, page or study-set PDF has to be drawn, rendered, checked or assembled."
---

The drawing tools for sketchnote pages. Ink each page from three inputs, each in its own file so that one can change without the others:

- **Page source**, `<page>.src.html`: the composition and drawings of one page, in plain SVG.
- **Style rules**, `style.json`: how ink, lettering, hatching, shadows, arrows and colour cues look.
- **Print rules**, `print.json`: paper dimensions and safe margins in mm.

Orientation belongs to the page, so each render names it.

Use the rules files you are given, unchanged. To write or change one, read [RULES.md](RULES.md) first.

## Draw

A page source is an HTML fragment that fills the safe area. Its board is one SVG whose `viewBox` is the safe area in mm, so that 1 unit prints as 1 mm (A4 portrait with 12 mm margins: `0 0 186 273`):

```html
<svg class="board" viewBox="0 0 186 273">
  <text class="title shadow" x="2" y="22" font-size="21">How a lock lifts a boat</text>
  <rect class="ink shadow" x="1" y="32" width="182" height="74"/>
  <path class="ink arrow" d="M76 74 C86 71 98 71 108 74"/>
</svg>
```

Draw ordinary SVG shapes and mark them. The style decides how each mark looks:

| Mark | On | Effect |
| --- | --- | --- |
| `class="ink"` | a shape | Redraws its outline as an uneven pen line. A shape without it stays as drawn. |
| `shadow` | an ink shape, any text | An offset shadow behind it. |
| `hatch` | a closed ink shape | Hatched filling. |
| `dashed` | an ink shape | A broken outline. |
| `arrow`, `arrow-both` | an open ink `line`, `polyline` or `path` | A head at the end, or at both ends. |
| `title` | text | The title face and its fill. |
| `ground` | any shape | A flat background that labels may sit across and that may run past the safe margins. |
| `data-cue="<name>"` | an ink shape | That colour cue's look. |
| `data-weight="<n>"` | an ink shape | A pen n times as wide. |

- `fill` colours an ink shape's inside. A closed shape with a shadow and no fill gets white.
- Every `text` is a label in the label face. Print each at 8 pt or more (`font-size` 2.9 on a board in mm).
- Keep outlines and shadows about 1 mm inside the board: wobble and offset carry them outward.

[example/](example/) holds a full page with its rules: `canal-lock.src.html`, `style.json` and `print.json`.

### Icons

An **icon** is any drawing that stands for one concept or operation. Draw it once as a `symbol` with a `viewBox` and place it with `use`, so that every copy is identical. Wherever it recurs it means that same concept, and another concept gets another icon.

Prove each new icon on a **proof sheet** before any page uses it:

1. Name its **job**: what the concept does in the answer. Then draw an object or an action that explains the job to someone who has never met the technology. A figure is doing the job, tool in hand. A box or a line with the concept's name on it explains nothing.
2. Put all new icons together on one page source, `icons.src.html`, beside the page sources: each at the size and with the shadow it has on a page, with a number and no words. Keep `icons.md` beside it, opening with a table: per number, the icon's concept and its job. Copy an icon that another proof sheet of the same set already holds for the same concept.
3. Render the sheet with the page's rules, open its PNG and redraw whatever looks broken. Then take the **cold read**: a fresh sub-agent, given only the PNG and the subject's name, says per number what the drawing shows and what it is for.
4. Take the **verdict** from a second fresh sub-agent, the **judge**, given that cold read and the concepts and jobs from the table. Per number it returns **hit** or **missed** with its reason: a cold read that names another concept, or that fits another icon's concept as well, has missed.

One cold read and its verdict make a **round**. Paste both replies into `icons.md` whole, under `## Round <n>`, below a `Cold read:` line and a `Judge:` line. With no sub-agents, write both yourself. Then run `ink.py rounds <folder>/icons.md` (see Render for how to run it): a reply it names as missing comes from its sub-agent before any icon changes.

The verdicts are the judge's: redraw every missed icon, render the sheet again and repeat steps 3 and 4 with new sub-agents. Done when the latest round is hit for every icon and `rounds` exits 0. After four rounds with an icon still missed, ask the user whether to run more or accept the misses. Once the icons are done or accepted, write the first page source, with the `symbol`s copied in unchanged.

## Render

Run `scripts/ink.py` from this skill's folder by absolute path, with the first of `python3` or `python` that runs.

```bash
python <skill folder>/scripts/ink.py render <page>.src.html --style <style.json> --print <print.json> --orientation <portrait|landscape>
```

It writes `<page>.html`, which carries its fonts and rules and opens anywhere, and `<page>.png` at 150 dpi. Edit the source and render again: the `.html` is output, too long to read for its embedded fonts. The command finds Chrome or Edge itself. When it stops, its message says what to fix or install.

Done when the command prints both paths. A `note:` means the board does not match the safe area and prints at another scale.

## Check

```bash
python <skill folder>/scripts/ink.py check <page>.html [<page>.html ...]
```

It lists each label that ink crosses, that a drawing covers or that prints under 8 pt, and each margin a mark enters, with its place in mm. Move the ink or the label in the source, then render and check again. Mark a background that a label is meant to sit across as a `ground`.

Then open the PNG. The check reads ink, never words: confirm by eye that each label is spelled right, clear of the next and true to the drawing.

Done when `check` exits 0 on every page and every label in its PNG reads whole at print size.

## Read colours

```bash
python <skill folder>/scripts/ink.py colours <image>
```

For a picture somebody else drew, such as a reference image. It lists the colours covering the most of it, white, black and greys included, each as `#rrggbb`, colour name, grey (0 to 255) and share of the picture. Done when it prints the list.

## Compare Looks

```bash
python <skill folder>/scripts/ink.py looks <page>.html [<page>.html ...] [--earlier <set folder or House style .md> ...] [--fixed title ink main-colour cues] [--coloured-paper]
```

For the proposals of one design round, each rendered in its own style rules. Per page it prints the **main colour** (the colour name covering the most of its PNG, panel tints counted, black, white and greys left out), the **title treatment** (title face plus fill), the ink width and each cue in use with its colour name and grey. Then it lists each fault, and exits 1 when there is one:

- two pages with the same title treatment, the same main colour, ink widths under 0.2 mm apart, or palettes with more than one cue colour name in common;
- two cues in use on one page printing under 30 grey levels apart;
- a page whose corners are not white paper.

`--earlier` names each earlier Look: an approved set folder, read from its `approved-sample.png` and saved rules, or a House style file. For each page and earlier Look it prints where the two differ, and faults a page that differs in fewer than two of main colour, title treatment and ink width. A House style has no page, so unless the learner fixed one of them, a page must differ from it in both title treatment and ink width. A `note:` names a comparison the earlier Look's files cannot settle, such as the title of a set saved without style rules: make it by eye.

`--fixed` exempts a choice the learner fixed for every page from its pair check and from the count against earlier Looks, which then asks two of the choices left, or the one left. `--coloured-paper` accepts paper the learner asked to be coloured. Done when it exits 0 and every `note:` is settled.

## Print

```bash
python <skill folder>/scripts/ink.py pdf <page>.html <out>.pdf
```

One page, at its own paper size and orientation. Done when the PDF exists.

## Assemble

```bash
python <skill folder>/scripts/ink.py assemble <page>.html [<page>.html ...] --print <print.json> --out <set folder>/study-set.pdf --renders <folder>
```

Name the pages in reading order. It lists each fault: a page that is missing, listed twice or left out of the list, paper or margins other than `print.json`'s, a `check` finding, a page that spills. With a fault it writes no PDF. Otherwise it merges the pages and renders each merged page to `<folder>/pdf-<k>.png`. It needs `pypdf` and `pymupdf`.

Done when it exits 0 and each render shows its page.
