# Reference Look

A reference image supplies one whole Look: palette, lettering, ink, shadows, arrows and cue treatment. The learner compares that Look in three structures. Take the Look alone: every drawing, word and mark on a page is the set's own. Paper stays white, even when the image's background is tinted, unless the learner asked for coloured paper.

## Palette (step 6)

Start once every colour role has its meaning and symbol.

1. Load the `inking` skill. Open the image and run the skill's Read colours on it: every hex taken from the image comes from that list.
2. Write `.scratch/<effort>/samples/reference-look.md` with the lines `approved-sample.md` lists under `## Look` (step 8): what the image shows for each, with the closest faces `inking` ships, and widths and offsets in mm.
3. Give each role one of the image's cue colours, with the cue treatment the image gives it. A role beyond the image's cue colours gets a new colour in the same manner, marked as added.
4. Compute the grey of every cue in use, by step 5's formula, and the gap between every pair. While any pair is under 30 apart, change lightness alone: hue and saturation stay, as few colours move as the rule allows, each as little as it allows, and each stays visible on white paper. A palette whose pairs are all at least 30 apart keeps the image's colours.
5. Write `print.json`, then draw the swatch sheet `samples/palette.src.html` with `palette.style.json`: the reference Look with one cue per role, each cue named for its colour (`green`), as in every proposal. Per role the sheet shows the symbol, the meaning and two plain filled swatches, the image's colour and the colour to be used, each labelled with its hex and grey. One further shape per role carries its `data-cue`, so that Compare Looks measures it. Render the sheet, run Compare Looks on it alone until it exits 0, and set every used colour's grey and every gap to the figures from its greys.

Give the learner the sheet's PNG path and, in chat, one line per role (symbol, image colour and grey, colour to be used and grey), then the gap of every pair. Say which colours moved and why, or that none had to. Ask the **Reference palette** question: approve these colours, or say what to change. A change redraws the sheet and asks again.

End the turn on that question: proposals are drawn only in an approved palette. Record the approval as a Settled decision with each role's hex and symbol and a link to the sheet. A later change to any colour returns here before a page uses it.

## Three structures (step 7)

- **One Look:** write one set of style rules from `reference-look.md` and the approved palette, and copy it unchanged to `a.style.json`, `b.style.json` and `c.style.json`. Structure is the one thing that differs between the pages, so the choices after a round are **Pick**, **Combine** and **Keep one Look**.
- **Compare Looks:** pass `--fixed title ink main-colour cues`. The pairs match by design, and the round is checked against no earlier Look. Each cue hex it prints equals its approved swatch.
- **Against the image:** judge lines on enlarged patches: an outline, a shadow and an arrow head, cut at one scale from the reference image and from each PNG. A whole page hides a thin pen. Then open the image beside each PNG and check lettering and cue treatment. Where one differs, correct `reference-look.md` and all three style files together, and redraw until all match.
- **`compare.html`:** above the proposals, show the swatch sheet's PNG and the reference image, linked where it lies. The line for each proposal names its structure.
