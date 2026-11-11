---
name: brainstorm
description: Widen before narrowing: propose batches of ideas, never decide.
disable-model-invocation: true
argument-hint: "What do you want ideas for?"
---

Brainstorm with the user. You widen; the user and the interview narrow. Ask no decision questions, write no ADRs, add no glossary terms.

## Start

1. Pick the effort folder `.scratch/<effort>/` (propose a short slug, or reuse the one the user names). The state lives in `.scratch/<effort>/ideas.md`.
2. If `ideas.md` exists, resume from it: read it in full, tell the user the buckets and counts, continue. Never re-propose a `rejected` idea.
3. In a repo, read `GLOSSARY.md` and `ARCHITECTURE.md` in full before the first batch. Follow no links.

## Each turn

1. Capture any idea the user gave, verbatim, as `raw` before anything else.
2. Propose 3 to 5 new ideas: one line each, plus why.
3. Save `ideas.md` (see shape below). Every turn ends saved, so a new session can resume.

The user may add an idea, pick, park or reject at any time. A `rejected` idea keeps a one-line reason.

## Ideas file

```md
## <Idea bucket>

- [raw] <idea>: <why>
- [picked] <idea>: <why>
- [rejected] <idea>: <why>. Rejected: <one-line reason>

## Unsorted

- [parked] <idea>: <why>
```

- Each Idea bucket is a `##` heading. Each idea is one list line with a status tag: `raw`, `picked`, `interviewed`, `parked` or `rejected`.
- Name a bucket once two or more ideas cluster. Every other idea sits in `Unsorted`.
- The interview flips `picked` to `interviewed`. You never do.

## Offers

Offer a side move only when its trigger holds, once, in one line:

- `/research`: ideas hinge on an external fact.
- A persona: the user asks for one.
- `/prototype`: the user cannot choose and the options differ in look, feel or behaviour.

## Ending

The user ends the session. When batches go stale (new ideas only restate old ones), nudge once.

On end:

1. Add `## Picked` at the top of `ideas.md`: each picked idea, a one-paragraph framing, and the open questions you spotted.
2. Tell the user to run `/interview-with-docs` on the Picked section. Do not invoke it.
3. When the picks are too big for one effort, suggest `/wayfinder`.
4. With several picks, tell the user the first interviewed idea reuses this folder and each later one gets its own effort folder whose Concern links back here.
