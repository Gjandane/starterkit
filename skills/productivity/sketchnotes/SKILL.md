---
name: sketchnotes
description: Plan illustrated study notes from a topic or your Markdown files, in a saved House style or a fresh design. A short interview, a sourced outline, then a print sample of one hard passage to approve.
disable-model-invocation: true
argument-hint: "<topic> | <file.md> [file.md ...] [--style <name>] [<reference image>]"
---

Plan a set of illustrated study notes for a learner. The input is a topic, or one or more Markdown files, with a House style name or a reference image when the learner has one. The run writes an **outline**: each **Learning objective** in study order, with the passages it rests on, the question its pages answer and what to draw. It ends with an **approved sample**: one printed page of a hard passage, in the design the learner approved.

Every claim in the outline cites a **source passage**: a passage from a supplied file, or from a page the research opened and read, and nothing else. A search snippet from an unopened page is not a source passage. A fact with no source passage is a **gap**, and it stays open in the outline.

Each choice that shapes the pages has one owner:

- A **House style** is a learner's reusable drawing and lettering principles: ink, lettering, shadows, arrow treatment and the look of each colour cue. A structure it names is an option a page may take. A saved one is `~/.starterkit/house-styles/<name>.md`, where `~` is the learner's home folder.
- The **study set** owns paper, margins, density and its **colour roles**: what each colour cue means for this subject.
- Each **page** owns its structure, orientation and drawings.

A **Look** is how a sample is drawn: its palette, lettering, ink, shadows, arrows and cue treatment. A House style holds one Look; a fresh design compares three, or takes the one Look a reference image gives it.

## Process

### 1. Read the input

Sort every argument:

- An existing `.md` file is a source.
- An existing image file (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) is the **reference image**.
- The value after `--style`, or a name the learner's words give to a style ("in my <name> style"), is the **style name**.
- Words that only say how to use one of these ("draw it like this picture") belong to it. Other words are the topic.

Sources and no topic is a **Markdown run**. A topic and no sources is a **topic run**. Any other mix (a path with no file there, or sources next to a topic) gets one question: which files to use, and whether the other words are a topic.

Done when you know the run's kind, the style name and the reference image (either may be none) and, for a Markdown run, have read every file in full.

### 2. Choose the design path

List the saved House styles, then take the first row that fits. Names match with case ignored and a space equal to a hyphen.

| Input | Path |
| --- | --- |
| The style name matches a saved House style | **Reuse** that style. An image beside it goes unused: say so. |
| A style name that matches none | Ask. |
| A reference image, no style name | **Fresh design**, in the image's Look. |
| Neither, and at least one saved House style | Ask. |
| Neither, and no saved House style | **Fresh design**. |

Ask means one question, first in the interview's round 1: every saved name and a fresh design, each as a lettered option, even when there are only two. When a requested name was not found, say so in its context line. The answer sets the path.

As soon as the path is reuse, by the table or by the answer, read the whole House style file and say in one line which style the set uses. A reference image on the fresh path supplies the whole Look: read [REFERENCE-LOOK.md](REFERENCE-LOOK.md) now. It changes steps 6 and 7.

Done when the path is known, or its question is written for round 1.

### 3. Interview

Load the `interview` skill. Skip its Orient step and write no Context docs. Its Done step runs in step 9. Keep its Interview log: create `.scratch/<effort>/interview-log.md` at the start of round 1. The log's Concern names the input: the topic, or the file paths.

The design tree has these branches, each with a recommended answer drawn from the input (the topic's usual scope, or what the files cover):

- **Design path:** asked when step 2 says so.
- **Study goal:** what the learner wants to explain or do after studying.
- **Prior knowledge:** what they already know. The outline covers it briefly or skips it.
- **Must-see details:** the facts, terms, figures or examples the pages must show.
- **Information density:** **sparse** (one idea, under 60 words), **balanced** (60 to 150 words) or **dense** (150 to 300 words) per page. Recommend from the study goal.
- **Paper:** A4 with 12 mm printer-safe margins on every side. Letter takes 12.7 mm margins. Print-shop requirements take the shop's trim size, bleed and safe zone as given.
- **Gaps:** on a Markdown run, one question per gap, asked as step 4 finds them.
- **Outline approval:** asked in step 5.
- **Colour roles:** asked in step 5 on the reuse path, in step 6 on a fresh design.
- **Visual design:** sample passage and fixed choices, asked in step 6, on a fresh design only.
- **Reference palette:** asked in step 6, on a fresh design with a reference image.
- **Sample approval:** asked in step 7.

Record the design path, the study goal, the prior knowledge, each must-see detail, the density and the paper size with its margins as Settled decisions.

### 4. Gather sources

Start once every decision step 3 records has settled.

- **Topic run:** load the `research` skill. Its question is the topic, scoped by the study goal, the prior knowledge and the must-see details. Its file is `.scratch/<effort>/research.md`, and each claim in it quotes the passage that supports it. A must-see detail the research finds no passage for is a gap.
- **Markdown run:** work from the supplied files. Compare them with the study goal and each must-see detail. A gap is a fact the goal or a detail needs that no supplied passage states. Ask one question per gap, naming what is missing as a question and never its answer: "Your files do not say <what is missing>. May outside research fill it?" When the learner approves, load the `research` skill for that gap alone. When the learner declines, the gap stays open. Record each gap answer as a Settled decision.

Every research run writes to `.scratch/<effort>/research.md`, adding its own section headed by its question. Earlier sections stay as they are.

A background research agent that is still running is an unfinished prerequisite: say so to the learner and wait for its section.

Done when every research section is written and, on a Markdown run, every gap has an answer.

### 5. Write the outline

Write `.scratch/<effort>/outline.md` in this shape:

```markdown
# Outline: <study set title>

Study goal: <from the interview>
Prior knowledge: <from the interview>
Sources: <the supplied file paths, and research.md when research ran>

## 1. <Learning objective: what the learner can explain or do>
Study question: <the question its pages answer>
Source passages:
- `<file>`, lines <a-b>: "<short quote>"
- <source URL>: "<short quote>"
Proposed drawing: <what to draw, and how it shows the answer>
Must-see details: <the learner's details this objective shows, or none>

## Open gaps
- <fact the study goal needs that no source passage states>. <why it is open>.
```

- Number the objectives in study order: each builds only on earlier objectives and the learner's prior knowledge.
- Cite a supplied file by path and line range, and a research source by the URL `research.md` gives for it. Each quote is one sentence at most.
- Each study question and proposed drawing rests on the passages listed under it.
- Assign every must-see detail that a source passage states to at least one objective. Every gap, including a must-see detail no source passage states, goes to Open gaps and nowhere else.
- With no gap, the Open gaps section reads "None."

Show the whole outline file in chat, then ask the Outline approval question. On the reuse path, ask the Colour roles question in the same round, for the House style's cues. When the learner asks for changes, revise the file and ask again, with the colour roles the change affects. Record the approval as a Settled decision that lists the Learning objectives and links `outline.md`.

A **colour role** is what one colour cue means for this subject, with a symbol so that it reads without colour. Recommend a role only where the outline has a use for it. On the reuse path each role takes one of the House style's cues; on a fresh design the roles settle by meaning and symbol alone, and each proposal gives them its own colours in step 7. In every palette, the greys of the cues in use (0.299 R + 0.587 G + 0.114 B, from 0 to 255) sit at least 30 apart. Record each role as a Settled decision.

Done when the learner approves the outline and, on the reuse path, the colour roles are in the log.

### 6. Set the visual design

Fresh design only: the reuse path goes to step 7. Ask these in one round, each with a recommended answer:

- **Sample passage:** the hardest passage in the outline to draw, named by objective number and source passage. Recommend the one with the most parts or steps.
- **Fixed choices:** "What must stay fixed?", asked once. A fixed choice is any part of the Look, its main colour alone, or coloured paper. Recommend nothing fixed, so that the three proposals differ in everything. Whatever is not fixed varies. A reference image already fixes the whole Look, so with one this question goes unasked.
- **Colour roles:** one per meaning, each with its symbol and no colour yet, as step 5 defines them.

Choose portrait or landscape yourself, to suit the passage (a long sequence runs portrait, a wide comparison landscape). State the choice and one reason in the round; the learner may overrule it.

Record each answer and the orientation as Settled decisions. With a reference image, record its Look as the fixed choice, then settle the palette as [REFERENCE-LOOK.md](REFERENCE-LOOK.md) says.

Done when the sample passage, the fixed choices, the colour roles and the orientation are all in the log, and with a reference image the approved palette too.

### 7. Draw the sample

Load the `inking` skill. The run's rules live in `.scratch/<effort>/samples/`: `style.json` (style rules), `print.json` (the paper and margins as print rules) and `principles.md` (what the style rules cannot say, written in step 8 on a fresh design). On a fresh design each proposal carries its own style rules until one is approved.

Draw, render and check every page with the skill. Then check each PNG against its passage: the same facts, the agreed density, each colour cue used only where its role applies, and every label spelled as its source passage spells it. Fix and re-render until all pass.

#### Reuse: one sample

Choose the hardest passage in the outline, the one with the most parts or steps, and the orientation that suits it. Then choose its structure:

1. Find this style's **last approved sample** in the repo. Its candidates are the `sketchnotes/*/` folders whose `approved-sample.md` names this style on its `House style:` line, and older folders with no `approved-sample.md` whose `style.json` holds the same values as the House style's `## Style rules`. Date each candidate by the last commit of its `approved-sample.png`, or by file time when that file is uncommitted: the latest date wins. Take its structure from the `Structure:` line or, in an older folder, from its `principles.md` and the image itself, opened.
2. Name the shapes the passage has: a sequence, a comparison, a cycle, a diagram of parts, or another it plainly has. A structure fits when its layout alone shows that shape: a cycle closes on itself, and a comparison sets its sides face to face.
3. Choose a fitting structure unlike the last approved sample's. Two samples share a structure when the eye takes the same path through the same kind of arrangement, however many parts each has. When only that sample's structure fits, keep it and tell the learner why no other fits. With no earlier sample, choose the best fit.

Copy the JSON under the House style's `## Style rules` and the bullets under its `## Principles` unchanged into `style.json` and `principles.md`, and write `print.json`. Draw the passage once, as `sample-1.src.html`, in the chosen structure, and check its PNG against every principle too. A principle a page "may" follow is an option: the page meets it whether it takes it or not.

Give the learner the PNG's path, the passage, the orientation and the structure, with one reason for each choice, and the last approved sample's path and structure beside them. Ask the Sample approval question with two choices:

- **Approve** the sample.
- **Revise** it: the learner says what to change. Change the page source or the run's rules, draw `sample-<n+1>` and ask again.

A revision is a local correction. It changes this run, leaves the saved House style as it is, and comes with no question about saving.

#### Fresh design: three proposals

With a reference image, this section applies as changed by [REFERENCE-LOOK.md](REFERENCE-LOOK.md).

Write `print.json`, then draw three **proposals** of the sample passage. Each is one Look in one **structure**: reading path, information hierarchy and where the drawing sits (for example a flow chart, one annotated central drawing, and numbered panels). Three tweaks of one grid is one structure. All three show the same passage, its must-see details and its source facts, at the agreed density, paper and orientation, and keep every fixed choice. Everything else varies, shadows included.

Each proposal's palette gives every colour role its own colour, named for that colour, and keeps the role's symbol. Paper stays white: tints sit inside panels and drawings, and no `ground` reaches the page's edges, unless the learner asked for coloured paper.

Each pair of proposals differs in all of these, except a choice the learner fixed:

- **Structure.**
- **Title treatment:** the title face plus its fill.
- **Ink:** widths at least 0.2 mm apart.
- **Main colour:** the colour covering the most of the rendered page, panel tints counted, black and white left out, compared by colour name.
- **Cue colours:** at most one colour name in common.

Each proposal also differs from every **earlier Look** in at least two of main colour, title treatment and ink width; a fixed choice drops out of that count, and with one of the three left, that one differs. The earlier Looks are every saved House style in `~/.starterkit/house-styles/` and every approved sample in this repo: each `sketchnotes/*/` folder holding an `approved-sample.png`, with or without an `approved-sample.md`. Before drawing, read each one's saved rules and open each approved image. Those files are the whole design history, read afresh each round.

Each proposal sits in `.scratch/<effort>/samples/round-<n>/` as a page source with its own style rules: `a.src.html` with `a.style.json`, then `b` and `c`. Render all three, then run the `inking` skill's Compare Looks on the three pages, with `--earlier` for each earlier Look, `--fixed` for each fixed choice (fixed lettering is `title`, a fixed palette is `main-colour cues`) and `--coloured-paper` when the learner asked for it. Redraw until it exits 0, every comparison it leaves to the eye holds and the three structures differ by eye.

Write `compare.html` in the round folder: the three PNGs side by side with their letters, each above one line naming its structure and its Look (main colour, title treatment, ink width, each role's colour, shadows, arrows), then each one at its paper width in `mm`, so the learner sees it at print size. Give the learner its path and the same line per proposal. Ask the Sample approval question with four choices:

- **Pick** one sample as it is.
- **Combine** elements: the learner names a **base** sample, and each element to borrow with the sample it comes from.
- **Three new Looks**, with anything the learner wants changed.
- **Keep one Look** and try three structures: the learner names the sample whose Look stays.

Ask for whatever a choice leaves unnamed. Letters run on across rounds (`d`, `e`, `f` in round 2), so each names one sample. After a combine or another round, ask this question again: **Pick** stays open to every sample shown in this design session.

##### Combine

Write the revised sample into the latest round folder as `revised.src.html` with `revised.style.json`, then `revised-2` and so on. Both start as copies of the base's files. Change only what carries the borrowed elements: each now matches its source, and the rest, structure included, stays the base's. Render and check it, then run Compare Looks on it alone. A borrowed element that breaks a rule above, such as two cue greys under 30 apart, goes back to the learner with the fault. Show the revised PNG and name the base and each borrowed element with its source.

##### Three new Looks

Draw the round in `round-<n+1>/` by every rule above, its own `compare.html` included. Each new proposal also differs from every Look shown earlier in this session, revised samples included, in at least two of main colour, title treatment and ink width (0.2 mm apart), read from the lines Compare Looks prints for each page. A fixed choice leaves that count; with fewer than two left, the proposal differs in each one left.

##### One Look, three structures

Draw three samples in `round-<n+1>/`, each in an unchanged copy of the kept sample's style rules, with its shadows, arrows and cue marks drawn the same way. The passage, density, paper and orientation stay as agreed. Only structure differs: three reading paths, distinct by eye. Run Compare Looks with `--fixed title ink main-colour cues`, and redraw until it exits 0 and prints the kept sample's main colour on all three. Write `compare.html`.

#### Done

Record each choice as a Settled decision: the sample, proposal or elements chosen, each revision, and why. Done when the learner approves one sample.

### 8. Save the approved sample

`/ship` deletes Scratch, so the approved sample lives outside it, in the **set folder**: `sketchnotes/<effort>/` at the repo root. On a fresh design, the style rules beside the approved sample's page source become `style.json`, and `principles.md` is written from the approved sample, with the Principles bullets [HOUSE-STYLE.md](HOUSE-STYLE.md) lists. Then copy the approved sample to the set folder as `approved-sample.png`, `approved-sample.html` and `approved-sample.src.html`, with `style.json`, `print.json` and `principles.md` beside them. Those three files are the set's **approved rules**: a fixed copy for every page, whatever the saved House style says later.

Beside them, write `approved-sample.md`, the record a later design compares with:

```markdown
# Approved sample: <study set title>

House style: <the reused or saved style's name, or none>
Structure: <the sample's reading path and arrangement, in one line>

## Look

- Palette: <each colour role: its colour's name, #rrggbb and symbol>
- Main colour: <the colour name Compare Looks reports for the approved page>
- Lettering: <label face; title face and fill>
- Ink: <colour and width in mm>
- Shadows: <colour and offset, and what casts one>
- Arrows: <head, weight and the kind of path>
- Cue treatment: <each cue's fill, hatch or outline>
```

Record a Settled decision that names the set folder and its three rules files, links the image and states the design a build session must keep: paper size, margins, density, lettering, palette, and the colour roles with their symbols. The sample illustrates one passage: every other page chooses its own structure, orientation and drawings.

Done when the image opens from its new path, the three rules files and `approved-sample.md` sit beside it and the log names them all.

### 9. Finish

Run the interview's Done step: confirm the shared understanding, then set the log's `Status:` to `done`. On a fresh design, the same round asks one more question: whether to save these drawing rules as a House style, and under what name. On a yes, follow the Save section of [HOUSE-STYLE.md](HOUSE-STYLE.md), then write its name on the `House style:` line of `approved-sample.md`. On the reuse path, the round is the confirmation alone.

Done when the log reads `Status: done` and a House style the learner chose to save exists under its name.

End with this line, exactly: "Approved sample saved to `<image path>`. Interview log at `<log path>`. Next, run `/starterkit:to-spec <log path>`."

## Changing a saved House style

Only when the learner asks, in their own words, for the saved style itself to change, at any point in this session: follow the Update section of [HOUSE-STYLE.md](HOUSE-STYLE.md).
