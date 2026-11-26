# Study set

The Issues of a sketchnote study set. A builder opens one in a fresh worktree and session, so each Issue holds or names everything its pages need, and the handoff commit puts every named file on the branch.

## Content Issue

One per numbered Learning objective, in study order, with all of that objective's images and pages. Use the tracker's ticket template, with a `**Spec:**` line under `**Scratch:**` and, after the template's last section, these sections copied from the spec. `<set folder>` is the path the spec records:

```markdown
**Spec:** `<repo-relative spec path>`

## Learning objective

Objective <N> of <total>: <what the learner can explain or do>

Study question: <question>
Proposed drawing: <drawing, with any planned images>
Must-see details: <details, or none>
Source passages:
- <original locator>: "<quote>"

## Approved rules

Set folder: `<set folder>`. Its three rules files are fixed for this set, whatever a saved House style says now.

- Drawing rules: `<set folder>/style.json` and `<set folder>/principles.md`
- Print rules: `<set folder>/print.json` (<paper and its mm, margins in mm, any bleed or safe zone>)
- Density: <name>, <words per page>
- Colour roles:
  - `<cue>`: <meaning>. Symbol: <symbol>.
- Sample image: `<set folder>/approved-sample.png`, these rules on one passage. Each page chooses its own structure, orientation and drawings.

## Drawing tools

Load the `inking` skill (starterkit plugin). Its folder holds `SKILL.md` (marks and commands), `RULES.md` (the fields of the rules files), `fonts/` (each face with its licence) and `scripts/ink.py` (`render`, `check` for ink on labels, `pdf`).
```

- Copy each passage, must-see detail and colour role in full. Keep these paths, repo-relative, on any tracker: they are how a fresh session finds the rules.
- **Verify** steps fit the objective: match each factual check to the quoted passage that supports it, run the ink-on-label check, check the drawing and its must-see details at print size, then answer the study question from the finished pages.
- One acceptance criterion has the builder add a `## Pages` section listing its page files in reading order. Its presence marks the objective as drawn, so publish the Issue without it.

## Assembly Issue

One, last, blocked directly by every content Issue. It assembles the PDF in study and page order, from each content Issue's `## Pages`, keeping each page's own orientation, and names the set folder and its `print.json`.

Its Verify runs the `inking` skill's `assemble` to exit 0, then opens `<set folder>/study-set.pdf`: its page count and sequence match the spec and each content Issue's `## Pages`, and each page is turned the way its page PNG is and shows its must-see details, labels that are whole and spelled right, and its colour fills.

## Handoff commit

Once the Issues are published and the spec reads `building`, make one commit on the current branch, by path:

- the set folder
- the spec and the Spec index
- on a local tracker, the effort's `issues/` folder
- each untracked file among `docs/agents/` and the agent instructions that point there (`AGENTS.md` or `CLAUDE.md`), where the builder finds its tracker

Where git ignores one of these paths or a hook rejects the commit, stop, name the path and the rule, and ask.

Done when `git ls-tree -r --name-only HEAD` lists every one of these files, and every path under an Issue's Approved rules. Tell the user: "Handoff committed as `<sha>` on `<branch>`. Cut a fresh worktree from that branch."
