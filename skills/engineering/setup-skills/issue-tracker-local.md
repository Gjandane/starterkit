# Issue tracker: Local Markdown

Issues for this repo live as markdown files in `.scratch/`. Specs are files in `docs/specs/` (see `context-docs.md`); a ticket links to its spec and never holds it.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## Ticket template

```markdown
# NN: <title>

**What to build:** ...

**Blocked by:** NN, NN

**Status:** ready-for-agent

**Model tier:** standard
**Effort:** medium
**Where:** cli
**Constraints:** (optional)
**Prerequisite:** yes (only when it applies)

- [ ] Acceptance criterion

**Verify:**

- How to check the work
```

Model tier is `heavy`, `standard` or `light`. Effort is `low`, `medium` or `high`. Where is `desktop`, `cli` or `cloud`. No model names.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`interview`/`task`), followed by `Model tier:` and `Effort:` lines; a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
