---
name: builder-spec
description: "Build every ticket of a spec on one integration branch with implementer sub-agents. A stopped ticket stays open and the rest of the frontier continues. Ends with code review and a report of open tickets."
disable-model-invocation: true
---

Build the spec the user names, or the one the tickets link. The result is the spec's tickets built on a single **integration branch**.

The issue tracker should have been provided to you (`docs/agents/issue-tracker.md`). If not, tell the user to run `/setup-skills`.

The tickets are a **task graph** with blocking relationships. The **frontier** is every open ticket whose blockers are all resolved. Implementer sub-agents run in the background, one per frontier ticket, for maximum concurrency.

## Read

You are the orchestrator. Read once, in this order, and hold it for the whole run:

1. The spec, in full.
2. Every ticket of the spec, fetched from the issue tracker.
3. The glossary and the Architecture doc, in full (paths in `docs/agents/context-docs.md`, else `GLOSSARY.md` and `ARCHITECTURE.md` at the root). A missing one is skipped without comment.

The Spec index, other specs, ADRs and a code-exploring sub-agent stay closed. A ticket's **Status** is the only record of progress: resolved tickets are done and never rebuilt. A re-run therefore picks up from the open tickets, on the integration branch the earlier run left.

A **Prerequisite** ticket is a task for the user, never for a sub-agent. Leave it open and report it.

## Run

1. Create the integration branch, or check it out when it exists. When the tracker closes work through PRs, or the user asks for one, open a **draft** PR after the first merge (a branch with no commits ahead of main cannot open one), marked as closing the spec and tickets. The PR stays draft for the whole run.
2. Start one implementer sub-agent per frontier ticket. Each gets its own worktree on its own branch, and a brief of the **Implementer rules** below plus three pointers: the ticket path, the spec path, the integration branch. Everything else in the tickets and the spec stays out of the brief.
3. When an implementer reports done, merge its branch into the integration branch with a **merger sub-agent**. Merge one at a time.
4. When an implementer reports stopped, the ticket stays open with the reason it gave. Every ticket that waits on it, directly or through other tickets, stays open as "blocked by NN". Nothing else pauses: recompute the frontier after each merge and each stop, and start implementers for the new frontier tickets.
5. The run is over when the frontier is empty and no implementer is running.

## Implementer rules

These are written for the implementer sub-agent. Pass them in the brief.

**Start.** Confirm the worktree is based on the integration branch tip, and reset onto it when not. Read, in this order: the ticket, the spec it links in full, the glossary and the Architecture doc in full (a missing one is skipped), then only the ADRs linked from the `ADRs:` field of the Modules the ticket text names or touches. Stop reading there. The code the ticket touches is read as the work needs it. Print the ticket's run line, `<Model tier> · <Effort> · <Where>` (a missing field prints `not set`), and proceed.

**Build.** Read the ticket's **Constraints** before any code and hold them as hard limits. Load the `tdd` skill where possible, at pre-agreed seams, with the Constraints stated in the same message. Run typechecking and single test files regularly, and the full test suite once at the end.

**Contradictions.** Compare what you find with the docs and the ticket.

- A contradiction outside the ticket's path, or a stale doc while the ticket is still buildable: note it for Build notes and carry on.
- The ticket cannot be built without breaking an ADR or a Rule across modules, or its design is wrong: stop. Commit nothing, write no Build notes, and report stopped with the contradiction and the ADR, Rule or criterion it hits.

Context docs (glossary, ADRs, Architecture doc, specs, Spec index) are read-only. Never touch `rundown.md`: the orchestrator alone refreshes it, so no worktree carries its own copy back. Record a mismatch in Build notes; `ship` reconciles the docs.

**Verify.** Merge the integration branch tip into your branch, then run the ticket's **Verify** steps, every step, in the order written. A failed step is fixed and re-run. A step that cannot run in this place (the ticket's Where is not here, a needed tool or service is missing) is a stop: commit nothing, write no Build notes, and report stopped with which step needs which place.

**Finish.** Commit the work to your branch. Write `## Build notes` on the ticket: appended to the ticket file on a local tracker, a comment on a real tracker. At most five one-line notes, covering Modules added or removed, Interface names changed, new cross-module calls, and the mismatches found. Empty is written as `none`. On a local tracker, tick the acceptance criteria that are met and set the ticket's status the way the tracker closes work, in the same commit, so the merge carries it. Report done.

## End of run

1. Load the `code-review` skill and review the integration branch against main, covering what merged. Fix what it raises in a single implementer sub-agent, then merge it.
2. On a real tracker, close each ticket that merged the way the tracker closes work, ticking its met acceptance criteria first. On a local tracker the merge already did it.
3. When this run changed a ticket, load the `rundown` skill, once, after the last merge and after closing tickets on a real tracker. Leave its refreshed `rundown.md` uncommitted and local.
4. Report the integration branch, the tickets built, and each open ticket with its reason: the stop an implementer reported, "blocked by NN", or "Prerequisite, needs you". Open tickets are never forced.
5. Clean up every implementer worktree.

When a refresh happened, end with the next step `rundown` printed. When a guard skipped the refresh, end with this line, exactly: "Tickets changed. Run `/rundown` to refresh the checklist." A run that changed no ticket loads nothing and prints neither ending.
