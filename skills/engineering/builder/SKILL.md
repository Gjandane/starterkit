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

Load the `tdd` skill where possible, at pre-agreed seams, with the Constraints stated in the same message.

Run typechecking regularly and single test files regularly. Run the full test suite once at the end.

## Contradictions

While reading and building, compare what you find with the docs and the ticket.

- A contradiction outside the ticket's path, or a stale doc while the ticket is still buildable: note it for Build notes and carry on.
- The ticket cannot be built without breaking an ADR or a Rule across modules, or the ticket's design is wrong: stop, state the contradiction with the ADR, Rule or criterion it hits, and ask.

Context docs (glossary, ADRs, Architecture doc, specs, Spec index) are read-only here. Record a mismatch in Build notes; `ship` reconciles the docs.

## Finish

1. Load the `code-review` skill and review the work. Fix what it raises.
2. Run the ticket's **Verify** steps, every step, in the order written. A failed step is fixed and re-run. A step that cannot run in this place (the ticket's Where is not here, a needed tool or service is missing) stops the skill: commit nothing, write no Build notes, leave the ticket open, and say which step needs which place. With no ticket this step is the full test suite alone.
3. Commit the work to the current branch.
4. Write `## Build notes` on the ticket: appended to the ticket file on a local tracker, a comment on a real tracker. At most five one-line notes, covering Modules added or removed, Interface names changed, new cross-module calls, and the mismatches found. Empty is written as `none`. Then resolve the ticket the way the issue tracker closes work, ticking the acceptance criteria that are met first. Skip this step when there is no ticket.
5. When this run changed a ticket, pass the resolved ticket to `rundown` for its guarded refresh, after Build notes and resolution. Load the `rundown` skill. Leave its refreshed `rundown.md` uncommitted and local, including on a real tracker.

When a refresh happened, end with the next step `rundown` printed. When a guard skipped the refresh, end with this line, exactly: "Tickets changed. Run `/rundown` to refresh the checklist." A run that changed no ticket loads nothing and prints neither ending.
