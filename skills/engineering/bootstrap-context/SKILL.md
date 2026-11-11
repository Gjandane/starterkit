---
name: bootstrap-context
description: "Write the missing Context docs (Architecture doc, glossary, ADRs, Spec index) from an existing codebase."
disable-model-invocation: true
---

Brownfield bootstrap: write the Context docs a repo lacks, from its code. Load the `domain-modeling` skill. It owns the three shapes this skill writes: `ARCHITECTURE-FORMAT.md`, `GLOSSARY-FORMAT.md` and `ADR-FORMAT.md`.

## Rules

- **Fill the gaps only.** A Context doc that exists is input, never a target. Write only missing files.
- **Code wins.** The README, agent files (`AGENTS.md`, `CLAUDE.md`, `docs/agents/`) and existing docs are hints. When a hint and the code disagree, the code goes in the draft and the conflict goes on the conflict list.
- **Review gate.** Context docs stay untouched until the user has seen the draft once (step 8). Everything before that lives in Scratch.
- **Uncommitted.** Leave every written file uncommitted.
- **Tiers.** This skill runs at tier `standard`. Module sub-agents run at tier `light`, the flow tracer at `standard`. Map a tier to a model with the tier table in `docs/agents/model-tiers.md`. With no table, sub-agents inherit the current model; say so once.

## Scratch

State lives in `.scratch/bootstrap/`. Write each file the moment its content arrives:

| File | Written at |
|---|---|
| `plan.md` | step 1: missing docs, hint list |
| `modules.md` | steps 2 and 3: kind of repo, confirmed sections and Modules |
| `reports/<section>.md` | step 4: one per section |
| `flows.md` | step 5: candidate flows and the tracer's report |
| `why.md` | step 6: questions and answers |
| `terms.md` | step 7: terms and verdicts |
| `draft/` | step 8: every drafted file, conflict list in `draft/conflicts.md` |

**Resume.** On start, after the step 1 refusal check, read `.scratch/bootstrap/`. Each step whose file exists is done: skip it and its questions. A section with a saved report is not rescanned. Say in one line where the run resumes.

## Steps

1. **Check.** Look for the glossary (`GLOSSARY.md` at the root), ADRs (`docs/adr/` with at least one ADR) and the Architecture doc (`ARCHITECTURE.md` beside the glossary). All three exist: stop, say the Context docs are complete, and tell the user to run `/interview-with-docs`. Otherwise save `plan.md`: which docs are missing, and every claim the hints make about structure, terms or decisions.

2. **Kind of repo.** Detect single app, monorepo or library from the manifests (`package.json` workspaces, `pnpm-workspace.yaml`, `Cargo.toml` workspace, `go.work`, `pyproject.toml` and the like) and the folder tree. Propose only these three kinds. A multi-context layout is a later choice for the interview.

3. **Module list.** Apply the Module rule (one top-level source folder with its own interface) to the tree, the manifests and the README. Read no source. When an Architecture doc exists, take its Modules as the list. Group the Modules into about 12 sections. Show the kind of repo and the grouped list in one message; the user corrects both. Save `modules.md`. Done when the user has confirmed the list. No sub-agent reads source before this.

4. **Scan.** Dispatch one read-only sub-agent per section at tier `light`, with the brief below. Save each report to `reports/<section>.md` on arrival. Without sub-agents, scan the sections yourself one by one and save each report before starting the next. Done when every section has a saved report.

5. **Flows.** From the reports, pick 2 to 5 candidate flows: the paths a request, job or call takes across Modules. Dispatch one read-only sub-agent at tier `standard` to trace them, with the candidates and the Module list. It returns each flow as numbered steps naming Module and file, and any candidate it could not trace. Save both to `flows.md`. Skip when the Architecture doc exists. A library with no runtime flow skips this step and drafts `## Public API` instead.

6. **Why-round.** Skip when ADRs exist. Gather the unexplained decisions from the reports. Keep those that pass all three ADR tests from `domain-modeling` (hard to reverse, surprising without context, a real trade-off), about 10 at most, most surprising first. Ask them in one round, one question each:

   ```
   ❓ **Q1** - **<decision, a few words>**
   Context: <one line: what the code does and where>

   a) Why: <your best reading of the code> ⭐
   b) Other why (type it)
   c) Don't know
   d) Accident or legacy
   ```

   Glossary terms in bold. Shorthand answers ("1a 2c 3d") are accepted; end the round with one line that says so. Save `why.md`. A given why (a, or b with text) becomes an ADR draft. "Don't know" and "accident or legacy" write nothing.

7. **Glossary seed.** Skip when a glossary exists. From the reports' candidate terms keep the recurring domain terms, about 20 at most, general programming words left out. The user confirms, renames or drops each, in one list with shorthand answers. Ask once about each synonym conflict (two words for one concept). Save `terms.md`.

8. **Draft and review.** Into `draft/`, write each missing doc:
   - Architecture doc in the `ARCHITECTURE-FORMAT.md` shape, with the optional sections for the kind of repo. Derive `## Shape` and `## Modules` from the reports and `## Flows` from `flows.md`. Every `Specs:` line reads `none`. `Last updated: Brownfield bootstrap (no spec)`. `## Rules across modules` holds only rules backed by an ADR or stated by the user, else `none yet`. Count the lines; past 200, group small Modules.
   - Glossary from `terms.md`, ADRs from the given whys in `why.md`.
   - `conflicts.md`: each hint the code contradicts, hint against code, with paths.

   Show the drafted Architecture doc (or, when it exists already, the other drafts) and the conflict list. The user edits or approves. Done when the user approves after this one review pass.

9. **Write.** Copy the approved drafts into place: `ARCHITECTURE.md`, `GLOSSARY.md`, `docs/adr/NNNN-<slug>.md`, and `docs/specs/README.md` when missing as an empty Spec index:

   ```markdown
   # Specs

   One line per spec: number, title, status, one-line gist, amends or supersedes link.
   ```

   Write no specs for existing code. Delete `.scratch/bootstrap/` last, after every file is in place.

10. **Done.** Print the files written, the files skipped (they existed), and "run `/interview-with-docs` to start work".

## Module sub-agent brief

Read-only. Read only the paths of the Modules in your section. Return, per Module:

- the six fields of the Architecture doc's Module section, one line each, `none` written out: `Does`, `Lives in`, `Interface` (entry file and its main exports), `Uses` (other Modules), `ADRs` (existing ADRs that cover it, else `none`), `Specs` (always `none`)
- external services it calls (APIs, databases, queues)
- candidate glossary terms: domain words that recur in names and types, each with one line on what it seems to mean
- unexplained decisions: choices the code makes that a reader would question, each with path and one line
- hint conflicts: each hint from `plan.md` about these Modules that the code contradicts, with path

No file dumps. At most 40 lines per Module.
