---
name: builder
description: "Build one ticket (or whatever the user describes): read the right context, run the ticket's Verify steps before committing, leave Build notes."
disable-model-invocation: true
---

Build the ticket the user names, or the work the user describes when no ticket is given.

The issue tracker should have been provided to you (`docs/agents/issue-tracker.md`). If a ticket reference is given and the tracker is not, tell the user to run `/setup-skills`.

## Read

This is the skill's own reading rule, not the Orient step. Read, in this order:

1. The ticket, fetched from the issue tracker. State its title. When the reference is ambiguous, ask.
2. The spec the ticket links, in full.
3. The glossary and the Architecture doc, in full (paths in `docs/agents/context-docs.md`, else `GLOSSARY.md` and `ARCHITECTURE.md` at the root). A missing one is skipped without comment.
4. Only the ADRs linked from the `ADRs:` field of the Modules the ticket text names or touches.

Stop reading there: the Spec index, other specs and a code-exploring sub-agent all stay closed. The code the ticket touches is read as the work needs it.

With no ticket, apply the same rule to whatever of items 2 to 4 exists for the described work. There is no run line, no Verify and no Build notes, and the full test suite is the only check.

## Start

Print the ticket's run line, `<Model tier> · <Effort> · <Where>`, and proceed. A missing field prints `not set`.

Read the ticket's **Constraints** before any code. Hold them as hard limits, and repeat them to `tdd` when loading it.

## Build

Load the `tdd` skill where possible, at pre-agreed seams, with the Constraints stated in the same message. A sketchnote content Issue and a sketchnote assembly Issue follow their own sections below instead.

Run typechecking regularly and single test files regularly. Run the full test suite once at the end.

Use the repo's existing check commands before writing a verification helper. Edit one-off ticket and Rundown changes directly. When a reusable runner is needed, stream child-process output as it runs so progress and failures stay visible.

## Sketchnote content Issue

An Issue with an `## Approved rules` section, or an older one that names a Learning objective, a study question and an approved sample, builds illustrated pages, so `tdd` does not apply. The Constraints still bind.

Work from the Issue, the spec it links and the three rules files in the Issue's set folder: `style.json`, `principles.md` and `print.json`. They are the set's approved rules, whatever a saved House style says now, so use them unchanged. They are also the only style input: except for the older Issue below, leave the sample image and its sources closed. Where the two differ, `principles.md` outranks the `inking` example. Keep the Issue's density and colour roles. A missing rules file stops the skill before it draws: name the file, commit nothing and leave the Issue open.

An older Issue's set folder is the one holding the approved sample. Use the rules files there, and write a missing `style.json` or `print.json` from the sample's HTML into this objective's folder.

Choose the structure and orientation of each page to show the answer to the study question, and add pages until every label reads at print size. Draw every concept or operation that the answer needs, unfamiliar technologies included, as a drawing that shows what it does. Several can share one diagram whose parts each trace. Every page has its own panel arrangement and drawings: the approved sample shows the rules on one passage only.

Load the `inking` skill. Take the icons through its proof sheet, then draw, render and check each page with it. Save each page source as `<set folder>/<NN>-<slug>/page-<n>.src.html`, which renders to `page-<n>.html` and its PNG beside it. The set folder sits outside Scratch because `/ship` deletes Scratch. `<NN>` is the objective's number as two digits, and `<slug>` is a short kebab-case name for it.

Run Finish step 1 now, so that the rounds check its fixes. Finish then starts at step 2.

Before Finish, check the pages in rounds. Open every PNG, and a greyscale copy of it. Then run a **round**: two fresh sub-agents on the `standard` tier, the reader and then the inspector, or both parts yourself where there are none. Copy the two briefs below, word for word, to the top of `<NN>-<slug>/checks.md`. Each sub-agent's prompt is its brief from there, word for word, plus the paths of the files it gets:

- The **reader** gets only the PNGs and the study question. It answers from the drawings, naming the one that shows each step, and lists every drawing it cannot explain.
- The **inspector** gets the PNGs and their greyscale copies, the reader's answer, the Issue, its passages, `icons.md` and the three rules files. It returns kept, broken or not applicable, with the evidence, for each of these: every must-see detail drawn and covered by the reader's answer; every bullet of `principles.md` on every panel; every fact and spelling against its passage; every icon against `icons.md`; every colour cue with its symbol, inside its role and distinct in grey. Not applicable is only for a bullet of `principles.md` that the page's panel count or orientation cannot hold, with the reason. It also rules each drawing the reader cannot explain a page fault, or a source limit where explaining it takes a fact that no passage gives, quoting the passage line that stops short.

Paste both replies into `checks.md` whole, as they returned: under `## Round <n>`, the reader's below a `Reader:` line and the inspector's below an `Inspector:` line, then your fixes. After pasting a round's replies, and before that round's fixes, run `ink.py rounds` on the objective's `checks.md` and `icons.md`: a reply it names as missing comes from its sub-agent now, on the pages as they are.

The verdicts are the inspector's: fix every page fault and every broken verdict, re-render, and run another full round with new sub-agents. Any later edit to a page takes a round too. Done when `ink.py check` exits 0 on every page, `ink.py rounds` exits 0 on both records, and the latest round in `checks.md` has no page fault and no broken verdict.

When four rounds end short of done, on the proof sheet or on the pages, stop before Finish: commit nothing, tick no box, leave the Issue open, and end with one question to the user that names what is left. Their answer either starts more rounds or accepts what is left, which then goes into Build notes.

In Finish step 4, add a `## Pages` section beside Build notes: the page `.html` files in reading order, one repo-relative path per line. It does not count toward the five notes.

## Sketchnote assembly Issue

An Issue that assembles a study set's PDF from content Issues' `## Pages` builds no new pages, so `tdd` does not apply. The Constraints still bind.

Read the spec's objective order and every content Issue's `## Pages`. A content Issue that is unresolved or has no `## Pages` stops the skill: name it and leave the Issue open.

Make the **page list**: the objectives in the spec's study order, each with its one content Issue, then each objective's pages in its Issue's order. Every objective has an Issue, every path in the list exists and appears once, and no `page-<n>.html` in a `<NN>-<slug>/` folder is missing from it. A missing Issue, a duplicate or a stray file goes to the user as one question.

Load the `inking` skill and run its `assemble` on the page list: `--print` the set's `print.json`, `--out <set folder>/study-set.pdf`, outside Scratch, and `--renders` a new temporary folder. A set without a `print.json` gets one in that folder, written from the sample's HTML. When `assemble` stops for a missing package or browser, tell the user what to install.

Open each render beside its page PNG: each must-see detail is shown, each label is whole, readable and spelled right, and every colour fill is present.

This Issue edits no page. A fault that `assemble` lists or a render shows goes to the user as one question naming the page, the fault and its content Issue, where the fix takes a check round: commit nothing and leave the Issue open.

Done when `assemble` exits 0 and every render passes.

In Finish step 4, add a `## PDF` section beside Build notes: the final PDF's repo-relative path on one line. It does not count toward the five notes.

## Contradictions

While reading and building, compare what you find with the docs and the ticket.

- A contradiction outside the ticket's path, or a stale doc while the ticket is still buildable: note it for Build notes and carry on.
- The ticket cannot be built without breaking an ADR or a Rule across modules, or the ticket's design is wrong: stop, state the contradiction with the ADR, Rule or criterion it hits, and ask.

Context docs (glossary, ADRs, Architecture doc, specs, Spec index) are read-only here. Record a mismatch in Build notes; `ship` reconciles the docs.

## Finish

1. Load the `code-review` skill. Supply working-tree mode against `HEAD`, the ticket or described work, and the changed paths owned by this run. Fix what the review raises.
2. Run the ticket's **Verify** steps, every step, in the order written. A failed step is fixed and re-run. A sub-agent that runs a step starts on the `standard` tier: the model `docs/agents/model-tiers.md` maps it to. A step that cannot run in this place (the ticket's Where is not here, a needed tool or service is missing) stops the skill: commit nothing, write no Build notes, leave the ticket open, and say which step needs which place. With no ticket this step is the full test suite alone.
3. Commit the work to the current branch.
4. Write `## Build notes` on the ticket: appended to the ticket file on a local tracker, a comment on a real tracker. At most five one-line notes, covering Modules added or removed, Interface names changed, new cross-module calls, and the mismatches found. Empty is written as `none`. Then resolve the ticket the way the issue tracker closes work, ticking the acceptance criteria that are met first. When git tracks the ticket file, commit it by path, so that a merge of this branch carries the notes and the status. Skip this step when there is no ticket.
5. When this run changed a ticket, pass the resolved ticket to `rundown` for its guarded refresh, after Build notes and resolution. Load the `rundown` skill. Leave its refreshed `rundown.md` uncommitted and local, including on a real tracker.

When a refresh happened, end with the next step `rundown` printed. When a guard skipped the refresh, end with this line, exactly: "Tickets changed. Run `/rundown` to refresh the checklist." A run that changed no ticket loads nothing and prints neither ending.
