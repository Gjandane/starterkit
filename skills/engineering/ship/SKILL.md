---
name: ship
description: "Close a finished effort in one commit: update the Architecture doc to what now exists, mark the spec shipped, delete Scratch."
disable-model-invocation: true
argument-hint: "[effort path, e.g. .scratch/<effort>]"
---

# Ship

Close one effort. The Architecture doc catches up with the code, the spec freezes as `shipped`, and the effort's Scratch goes, all in **one commit** on the build branch, so one revert undoes the whole ship.

**Questions first.** Every question (the one approval in step 4, the parked-ideas question in step 5) is answered before the first write in step 6. A stop at any question leaves the repo exactly as it was.

Paths: the Context docs sit where `docs/agents/context-docs.md` says, else `GLOSSARY.md` and `ARCHITECTURE.md` at the root, specs in `docs/specs/`, the Spec index at `docs/specs/README.md`. The issue tracker is `docs/agents/issue-tracker.md`.

## Process

### 1. Pick the effort

Take the path from the user. Without one, list the folders in `.scratch/`: one folder is the effort, several means ask which, none means there is nothing to ship; say so and stop.

On a real tracker, also take the parent issue: the reference the user gives, else the `## Parent` section of a ticket.

### 2. Check the tickets

Tickets: `.scratch/<effort>/issues/*.md` on a local tracker, the parent issue's child issues on a real tracker. A ticket is **done** when its Status is `resolved` or `done` (local) or the issue is closed (tracker).

Any ticket not done: stop. List each open ticket as number, title and status, write nothing. No tickets at all passes this check.

### 3. Read

Read only these:

- **The spec.** The file in `docs/specs/` whose `Effort:` line names this effort, else the spec the tickets link. Take its number, `# Title`, `Status:`, and any `Amends:` or `Supersedes:` line.
- **Build notes.** Every ticket's `## Build notes` section (local), or its Build notes comment (tracker).
- **Changed paths.** File names only, from the branch diff: `git diff --name-only $(git merge-base HEAD <default branch>)..HEAD`.
- **The Architecture doc**, in full.

The code itself stays closed, and so does any code-exploring sub-agent: Build notes and changed paths are the whole picture of what changed.

### 4. Show the plan, wait for one approval

Load the `domain-modeling` skill. Its `ARCHITECTURE-FORMAT.md` is the shape of every edit below.

A **touched Module** is one whose `Lives in:` path holds a changed file, or one a Build note says was added or changed. A Module that is only called by a new cross-module call is untouched. Draft the Architecture doc edit:

- Module sections added or removed as Build notes say. A new top-level source folder with its own interface in the changed paths is a new Module.
- On each touched Module, the six fields brought up to date (`Does`, `Interface`, `Uses` from Interface renames and new cross-module calls), and the spec link appended to `Specs:` (replacing `none`). The link uses number and title; an amending spec adds what it amends: `[0007 Recurring invoices](docs/specs/0007-recurring-invoices.md), amends 0001`.
- `## Shape` and `## Flows` changed only where a new or removed cross-module call changes them.
- Each Build note mismatch about the Architecture doc fixed in the doc, in a section the format defines. A mismatch the format gives no place (test setup, anything under "Stays out") is left out of the doc and listed in step 9.
- `Last updated: <NNNN Title>`.
- The doc still under 200 lines. Past that, group small Modules.

Show, in one message:

1. The Architecture doc edit as a diff.
2. The other writes, one line each: the spec flip, its index line, the `superseded` flip and its index line (only with `Supersedes:`), the `Effort:` line removed, the effort folder deleted (or what is kept, see step 5).

Wait for one approval. The user approves, corrects (apply the correction, show the diff again, wait again), or stops. A stop ends the skill with nothing written.

### 5. Parked ideas

Look at `.scratch/<effort>/ideas.md`. No file: skip this step.

- **An idea is still `picked`** (not yet interviewed): ask nothing. The ideas file stays; the rest of the effort folder goes. Say so in one line in step 9.
- **No idea is `picked`**: this is the ship that ends the ideas file. List its `parked` ideas, numbered, and ask which to carry forward (shorthand like "1 3" or "none"). With no `parked` ideas, skip the question.

Carried ideas go to a new effort: propose a slug and write `.scratch/<new-effort>/ideas.md` in the brainstorm shape, each carried idea as a `[picked]` line under `## Unsorted`, with its why. An idea always lands in an ideas file; ticket creation stays with `/to-tickets` after the interview. Ideas not carried are deleted with the folder.

### 6. Write

Every edit, in the working tree:

- The Architecture doc edit, as approved.
- The spec: `Status:` to `shipped`, and its `Effort:` line removed.
- Its index line in `docs/specs/README.md`: status word to `shipped`.
- With `Supersedes:`: the superseded spec's `Status:` to `superseded`, and its index line likewise.
- The new effort's ideas file, when step 5 carried ideas.

These are the only Context doc writes. ADRs and the glossary are read-only here, and a Context doc that does not exist stays missing.

### 7. Delete Scratch

`git rm -r` the effort folder. When an idea is still `picked`, keep `ideas.md` and remove everything else in the folder.

### 8. Commit

One commit on the current branch, the branch the tickets were built on, before its PR merges. Stage only the files steps 6 and 7 wrote or deleted. Message: `ship: <NNNN Title>`.

### 9. Report

On a real tracker, first close the parent issue with a comment linking the spec file, through the tracker doc's close operation. The PR stays as it is.

Then print, in order:

1. The kept ideas file line, when step 5 kept it: "Kept `.scratch/<effort>/ideas.md`: it still holds a `picked` idea."
2. ADR mismatches: each Build note mismatch that involves an ADR, with the ADR path and the code path. Listed for the user, fixed by nobody here. A reversed decision takes a new ADR through an interview. Write "ADR mismatches: none" when there are none.
3. Mismatches left out of the doc: each Build note mismatch the format gave no place, one line each. Write "Left out of the doc: none" when there are none.
4. On a real tracker: "The PR is ready to mark for review."
5. The next command, one line:
   - Carried ideas: `/interview-with-docs` on `.scratch/<new-effort>/ideas.md`.
   - A kept ideas file: `/interview-with-docs` on `.scratch/<effort>/ideas.md`.
   - Otherwise: `/interview-with-docs` for the next piece of work.

Done when the commit exists and the next command is printed.

## Missing inputs

- **No spec.** Draft the doc edit from the diff and Build notes. Skip every step whose input is the spec: the `Specs:` links, the status flips, the index lines, the `Effort:` line. Write `Last updated: <effort> (no spec)`.
- **No Architecture doc.** Skip the edit. The plan in step 4 holds only the other writes and still waits for one approval. In step 9, before the next command, print one line: "No Architecture doc. Run `/bootstrap-context` to write one from the code."
