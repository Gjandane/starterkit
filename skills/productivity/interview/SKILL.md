---
name: interview
description: Interview the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'interview' trigger phrases.
---

Inside a repo, start with the Orient step unless the invoking skill says to skip it: read [ORIENT.md](./ORIENT.md) and follow it before round 1.

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

## Question format

Write each question so the user can answer it without asking for context. One context line per question, in Simplified Technical English (short sentences, one idea each, active voice). Put glossary terms in **bold**, spelled as in `GLOSSARY.md`.

Use the default shape, about 4 lines. Word the question so "yes" accepts the recommendation:

```
❓ **Q1** - **<title>**
Why now: <one line: what makes this decision necessary>
<yes/no question>

➡️ Yes. <one-line reason>
```

Switch to lettered options only when there are three or more real choices, 5 to 6 lines. Each option says what it leads to. Mark the recommendation with ⭐, and "yes" takes it:

```
❓ **Q1** - **<title>**
Context: <one line>

a) <option> → <what it leads to> ⭐
b) <option> → <what it leads to>
c) <option> → <what it leads to>
```

Separate questions with `---`.

Ask a possible **Prerequisite** as a normal question in either shape, so the user decides it.

Accept shorthand answers: "1 yes 2a 3b", "yes to all". After the last question, end the round with one line that says so, for example: "Answer in shorthand: `1 yes 2a 3b` or `yes to all`."

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

When a decision needs a quick throwaway to judge, suggest `/prototype`.

## Interview log

Keep an Interview log unless the invoking skill says to write none. It holds the current state, so a new session can resume from the file alone. Read [INTERVIEW-LOG.md](./INTERVIEW-LOG.md) before round 1, or when given a log path to resume. The Orient step creates the log; outside a repo, create it at the start of round 1. It covers the format, when to save, and where deferred decisions and off-topic ideas go.

## Docs as you go

Skip this section when the invoking skill says to write no Context docs. Otherwise, load the `domain-modeling` skill. When an answer settles a decision that is hard to reverse, surprising without context and a real trade-off, write the ADR right then. When an answer resolves a term, add it to the glossary right then.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Ask the user to confirm you have reached a shared understanding. After they confirm:

1. Set the log's `Status:` to `done` and save it.
2. If the concern came from a picked idea in an ideas file, flip that idea from `picked` to `interviewed`.

Act on the result only after both steps.
