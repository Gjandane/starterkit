---
name: setup-skills
description: "Configure this repo for the engineering skills: issue tracker, triage labels, Context docs layout, model tiers and the agent-skills block. Run once before first use; re-run to fill what is missing."
disable-model-invocation: true
---

# Setup Skills

Write the agent docs and the agent-skills block the other skills rely on:

- `docs/agents/issue-tracker.md`: where issues live
- `docs/agents/triage-labels.md`: the five triage role strings (only with `triage` installed)
- `docs/agents/context-docs.md`: paths of the Context docs and the rules for using them
- `docs/agents/model-tiers.md`: Model tier to model name, per harness
- the `## Agent skills` block in `AGENTS.md`, with `@AGENTS.md` imported from `CLAUDE.md`

This skill creates no Context docs (glossary, ADRs, Architecture doc, specs) and does no harness detection. Flow: explore, ask, show one draft of everything, write. Commit nothing.

## Process

### 1. Explore

Read what exists; assume nothing:

- `git remote -v`: GitHub, GitLab or neither
- `AGENTS.md` and `CLAUDE.md`: which exist, and any `## Agent skills` block in either
- `docs/agents/`: which of this skill's docs exist already
- An upstream setup: an `## Agent skills` block with a `### Domain docs` sub-block, in `CLAUDE.md` or `AGENTS.md`. The file that sub-block points to is the upstream domain doc
- `GLOSSARY.md`, `GLOSSARY-MAP.md`, `docs/adr/`, `ARCHITECTURE.md`, `docs/specs/`: only to choose the next-step line in step 5
- `.scratch/`: a local-markdown tracker already in use
- Source files present or not
- `triage` installed: a `triage` skill folder beside this one, or `triage` in your available skills
- Monorepo signals: `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. Their absence means single-context, which is almost every repo

### 2. Ask

Ask a section only when its doc is absent. One section, one answer, then the next. Lead each with the recommended answer so one word accepts it. A section that exploration settled is skipped.

**Issue tracker.** If a remote points at GitHub, recommend GitHub; at GitLab (`gitlab.com` or self-hosted), GitLab. With no remote, recommend local markdown. Offer:

- **GitHub**: Issues via the `gh` CLI
- **GitLab**: Issues via the [`glab`](https://gitlab.com/gitlab-org/cli) CLI
- **Local markdown**: files under `.scratch/<feature>/`, good for solo repos or no remote
- **Other** (Jira, Linear, etc.): the user describes the workflow in one paragraph; record it as freeform prose

The GitHub and GitLab seeds carry a "PRs as a request surface" flag, defaulted off. Leave it off and do not raise it.

**Triage labels.** Only with `triage` installed. Ask one question: "Keep the default triage labels? (recommended: yes)". The defaults are `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On no, collect the user's existing label strings per role so `triage` applies them instead of creating duplicates.

**Multi-context.** Only on monorepo signals. Otherwise write single-context without asking. On signals, ask which layout the user wants.

Model tiers need no question: both columns are seeded.

### 3. Draft

Show one draft of everything to write:

- the `## Agent skills` block and the file it goes in
- the `@AGENTS.md` import for `CLAUDE.md`, when missing
- the content of each doc to be created
- on a migration (step 4), the moved block and the upstream domain doc being replaced, labelled as migration

Let the user edit it. Write nothing before they approve. When every doc exists and the block already matches, there is nothing to draft: go to step 5.

### 4. Write

**Docs.** Write each absent doc into `docs/agents/`, starting from the seeds in this folder. Never overwrite an existing doc. Adjust `context-docs.md` to the chosen layout (single or multi) by keeping only that layout's paths.

- [issue-tracker-github.md](./issue-tracker-github.md), [issue-tracker-gitlab.md](./issue-tracker-gitlab.md), [issue-tracker-local.md](./issue-tracker-local.md): trackers. "Other" is written from the user's description, and carries the same ticket template with Run metadata, the Model tier and Effort lines for wayfinder tickets, and the rule that specs are files in `docs/specs/` that the tracker only links to
- [triage-labels.md](./triage-labels.md): only with `triage`, with the user's overrides applied
- [context-docs.md](./context-docs.md)
- [model-tiers.md](./model-tiers.md)

When the triage labels ran on GitHub or GitLab, create each configured label the tracker lacks (`gh label create` / `glab label create`).

**Block.** The block always goes in `AGENTS.md`, created if absent. Update an existing `## Agent skills` block in place; leave the rest of the file alone. Keep each summary line already in the block. Write a missing one from the choice made: `GitHub Issues via gh`, `GitLab Issues via glab`, `Local markdown under .scratch/<feature>/`, or one line from the user's description; `Default five-role vocabulary` or `Custom labels for the five roles`; `Single-context` or `Multi-context`. A second run over an unchanged repo then writes nothing.

```markdown
## Agent skills

When a skill says "Load the `X` skill" and this harness has no skill tool, find that skill's `SKILL.md` and read it.

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Context docs

[single-context or multi-context]. See `docs/agents/context-docs.md`.

### Model tiers

Tickets record a Model tier, never a model name. See `docs/agents/model-tiers.md`.
```

Write the `### Triage labels` sub-block only with `triage`. List no skills in the block.

**Import.** `CLAUDE.md` gets a line `@AGENTS.md` when it lacks one. When neither file exists, create both: `AGENTS.md` with the block, `CLAUDE.md` holding only the import.

**Migration.** The one exception to never overwriting, and the draft showed it first:

- Upstream block in `CLAUDE.md`: rewrite it to the text above in `AGENTS.md` (created if absent), and put the import where the block stood in `CLAUDE.md`. Keep the rest of `CLAUDE.md` as it is. An upstream block already in `AGENTS.md` is rewritten in place.
- The `### Domain docs` sub-block becomes `### Context docs` with summary `Single-context` or `Multi-context`. Keep the user's Issue tracker and Triage labels summaries.
- Upstream domain doc: write `context-docs.md` in its place, with no layout question: multi-context when the repo has `GLOSSARY-MAP.md` or the upstream block says multi-context, otherwise single-context. Then delete the upstream doc.

### 5. Done

Print:

- files written
- files skipped (already present)
- files deleted (migration only)
- when the kept `issue-tracker.md` has no `## Ticket template` section: name it and say it predates the ticket template, so the user can compare it with this skill's seed
- one next-step line: when the repo has source and any of the glossary, ADRs or Architecture doc is missing, "run `bootstrap-context` to write the missing Context docs from the code"; otherwise "run `/interview-with-docs` to start"

Editing `docs/agents/*.md` by hand is fine. Re-running fills only what is missing.
