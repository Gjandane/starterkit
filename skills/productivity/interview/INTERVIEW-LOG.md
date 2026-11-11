# Interview log

The file holds the current state of the interview, so a new session resumes from it alone. It is state, not a transcript: it holds outcomes, never the conversation.

## Location

`.scratch/<effort>/interview-log.md`, one per effort folder.

- When the concern came from a brainstorm, reuse the brainstorm folder for the first picked idea interviewed. Each later picked idea from the same brainstorm gets its own effort folder, and its Concern links back to the brainstorm's ideas file.
- Otherwise, propose a short kebab-case effort folder name.

The Orient step creates the file at its end, before round 1, with Concern, Facts found and Open questions seeded from the Picked section of the ideas file. Make the folder name the first question of round 1. If the user picks another name, move the file there. Record the answer as the `Folder:` line of `## Concern`. The folder is never a Prerequisite.

## Shape

```markdown
Status: open

## Concern
<what the interview is about, in a few lines>
Folder: .scratch/<effort>/

## Settled decisions
- D1: <decision>. <one-line reason>. [ADR 0003](<path>), **<Term>**
- D2 (Prerequisite): <work> on **<Module>**, before the build. <one-line reason>.

## Open questions
- Q1 (interview): <question>
- Q2 (brainstorm): <question>

## Parked
- <decision the user deferred>. <one line on why it waits>.

## Facts found
- `<path>`: <finding>
```

- `Status:` is `open` or `done`. Set `done` only after the user confirms shared understanding.
- Settled decisions are `D1`, `D2`, in the order they settle. A `D` number is never reused or renumbered. Each decision has a one-line reason and links to any ADR or glossary term it produced.
- Open questions are `Q1`, `Q2`, each tagged with its source: `brainstorm`, `interview` or `Spec review`. List every known unsettled question of this effort, also the ones not yet on the frontier. Questions the interview finds get the `interview` tag.
- An accepted **Prerequisite** is a Settled decision tagged `Prerequisite`. It names a Module and the work on it that must finish before the build starts. A decision without both gets no tag.
- A decision the user defers goes to Parked, as `<decision>. <one line on why it waits>.` The reason names what it waits for, never who parked it.
- A settled decision the user takes back (moves out of scope, or defers) leaves Settled decisions and goes to Parked as `Was D<n>: <decision>. <one line on why it waits>.` Its `D` number stays retired.
- Before parking a settled decision, check whether a remaining decision or Open question depends on it. If one does, ask the user before parking.
- A fact a sub-agent finds goes to Facts found, as a path plus a finding.
- An off-topic idea goes to the ideas file, `.scratch/<effort>/ideas.md`, as a list line tagged `parked` under its Idea bucket or `Unsorted`. Create the file if absent. Then go back to the round.

## Saving

Save before you send each round. Rewrite the whole file to the current state:

1. Move each answered question from Open questions to Settled decisions, or to Parked if the user deferred it. The folder answer is the exception (see Location).
2. When a decision settles the effort's scope (which picked idea, which effort folder), rewrite `## Concern` to name that scope. Drop each Open question that belongs to another picked idea. It stays in the ideas file's Picked section for the effort that interviews it.
3. Add the questions of the new round to Open questions.
4. Add new facts to Facts found.

Every round ends with this line, after the shorthand line: "Saved to `<path>`. Safe to continue in a new session." It is the only note about sessions. Add no warning about context size.

## Resuming

Given an Interview log path, read the whole log. Settled decisions stay settled. Recompute the frontier from Open questions and ask it as the next round.
