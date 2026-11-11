---
name: guide
description: Ask how the skills fit together or how your repo works. Plain-English answer, at most one next command, no file written.
disable-model-invocation: true
argument-hint: "[your question]"
---

# Guide

You don't remember every skill, so ask. The answer is plain English with at most one recommended next command. This skill is read-only.

## Process

### 1. Classify the question

- **Plugin side**: which skill fits, what comes next in the flow, what a skill does, how skills relate.
- **Repo side**: how the user's code or domain works, what a term means, why something is shaped as it is.
- **Neither**: answer in one line and name the skill that fits (a bug to chase is `/diagnosing-bugs`, a concept to learn is `/teach`). Stop there.

A question with both sides gets the plugin side first, then the repo side. Read only what each side needs.

### 2. Plugin side

Read the Flow map below. Before stating what a skill does or recommending a step be skipped, read that skill's `SKILL.md`: the map is for orientation only.

Asked what to run next mid-effort (a `.scratch/<effort>/` folder with tickets or an Interview log exists), point at `/rundown`: it holds the whole checklist and prints the next unchecked step. That command is the whole recommendation.

### 3. Repo side

There is no map here. Read the Orient reading path on demand, matched the way the Orient step matches:

1. Match the words of the question against glossary terms and **Module** names, yourself, in conversation. More than 3 Modules match: ask one narrowing question first. None match: say "no existing module matches" and go on.
2. Read the glossary and the Architecture doc in full (paths in `docs/agents/context-docs.md`, else `GLOSSARY.md` and `ARCHITECTURE.md` at the root). In a multi-context repo, read `GLOSSARY-MAP.md` first, then only the matched contexts.
3. Read only the ADRs and specs linked from the matched Modules. The Spec index (`docs/specs/README.md`) is the fallback for work not yet built.
4. Cite the doc each part of the answer came from.

When the docs do not answer, say so and name where in the code to look: the matched Module's `Lives in` path and its Interface file. The user reads the code from there.

With no Context docs, answer the plugin side only and suggest `/bootstrap-context`.

### 4. An effort in progress

When the question concerns an effort that has not shipped, also read that effort's Scratch (`.scratch/<effort>/`: Interview log, ideas file, tickets, Rundown), read-only, and label that part of the answer "not yet shipped". Take the effort the question names, the only folder when there is one, and ask which when there are several.

### 5. Answer

- Missing context first: one or two sentences the user lacked, then the answer.
- Plain English, short sentences. Put glossary terms in **bold**, in the sense `GLOSSARY.md` gives them.
- At most one recommended next command, none for pure information.

Done when the answer is given, its sources are named, and no file is touched.

## Flow map

A **flow** is a path through the skills. Most paths run along one **main flow**, and the on-ramps merge onto it. Everything else is standalone, or a vocabulary layer that runs underneath.

### The main flow: idea to ship

The route most work travels. You have an idea and want it built.

1. **`/brainstorm`** (optional) widens before narrowing: batches of ideas, never a decision. It saves `.scratch/<effort>/ideas.md` and ends with a `## Picked` section. Skip it when the idea is already sharp.
2. **`/interview-with-docs`** sharpens the idea in an interview, after its **Orient step** reads the Context docs and lists what it found. It keeps an **Interview log** and writes `GLOSSARY.md` terms and ADRs as it goes. (Outside a repo, `/interview-me` runs the same interview and saves nothing; see Standalone.) A question that needs a runnable answer (state, business logic, a UI you have to see) gets a detour: `/handoff` out, `/prototype` in the new session, `/handoff` back what you learned.
3. **`/to-spec`** turns the finished Interview log into a numbered spec in `docs/specs/` and adds its line to the Spec index. No interview.
4. **`/review-spec`** (optional) reads the draft spec with reviewers who never saw the interview, on three axes: Cut, Gaps, Conflicts. Recommended after `/to-spec`, never required.
5. **`/to-tickets`** splits the spec into tracer-bullet tickets, each with its **blocking edges** and **Run metadata** (Model tier, effort, where, Verify). It flips the spec from `draft` to `building`.
6. **`/rundown`** writes the checklist of commands for the effort and prints the next unchecked step. Run it again whenever tickets change.
7. **Build**, in a fresh session per step:
   - **`/builder`** one ticket at a time, blockers first. Each ticket is self-contained, so the last one's context is disposable.
   - **`/builder-spec`** for the whole spec in one run. It reads the tickets as a **task graph**, runs implementer sub-agents across the ready **frontier** in parallel, and lands everything on one **integration branch**. A stopped ticket stays open and the rest continue; it ends with a code review and a report of open tickets.

   Either way the code is built by driving **`/tdd`** (one red-green slice at a time) and closed out with **`/code-review`**, a two-axis review (Standards and Spec) of the diff. Reach for `/tdd` on its own to build a behaviour test-first, and `/code-review` on its own to review any branch or PR against a fixed point. When the work goes up as a pull request, **`/pr`** shapes the body. It is model-invoked, so the agent reaches for it whenever it writes one. Small work needs no spec: `/builder` takes a plain description too.
8. **`/retro`** (optional) looks back over the build and suggests changes to the agent's **environment**, not the code: navigation pointers, automated checks, coding standards, steering files, tooling. Run it in the session it looks back on, before clearing.
9. **`/ship`** closes the effort in one commit: it updates the Architecture doc to what now exists, marks the spec `shipped` and deletes Scratch.

Keep the interview, `/to-spec`, `/review-spec` and `/to-tickets` in **one unbroken session**: the Rundown tags them "same session", so they build on the same thinking. When the **smart zone** runs out before `/to-tickets`, start a fresh session and resume from the Interview log (see Phase boundaries).

### On-ramps

A starting situation that generates work, then merges onto the main flow.

- **A repo with code but no Context docs** → **`/bootstrap-context`** (the **Brownfield bootstrap**). It writes the missing Architecture doc, glossary, ADRs and Spec index from the code, never overwrites, and is resumable. Merge onto the main flow at `/interview-with-docs`, whose Orient step then has something to read.
- **Bugs and requests piling up** → **`/triage`**. It moves issues through triage roles and produces agent-ready issues, which `/builder` later picks up. Triage is for issues **you didn't create**: tickets from `/to-tickets` are already agent-ready.
- **Something's broken** → **`/diagnosing-bugs`**. For the hard ones: the bug that resists a first glance, the flake, the regression between two known-good states. It builds a **tight feedback loop** (one command that goes red on *this* bug) before it theorises, then fixes with a regression test. When no seam can lock the bug down, that is the finding, and `/improve-codebase-architecture` is the skill for it.
- **A huge, foggy effort: a greenfield project or a feature too big for one session** → **`/wayfinder`**. It charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time, producing **decisions, not deliverables**, until the way is clear. Slower and denser than `/interview-with-docs`, so save it for the idea you cannot hold in one session. When the map clears it hands off: merge onto the main flow at `/to-spec`, which collapses the linked decisions into a buildable plan. Go straight to `/builder` only when the effort turned out small.

### Codebase health

Not feature work, just upkeep.

- **`/improve-codebase-architecture`** surfaces **deepening opportunities** whenever you have a spare moment. Picking one starts an interview session on that candidate. `/codebase-design` (below) is the bench you design the chosen one on.

### Vocabulary underneath

Two model-invoked references that run beneath the other skills, each the single source of truth for its vocabulary. Reach for them directly when the **words**, not the process, are the problem.

- **`/domain-modeling`**: sharpen the project's domain language: challenge a fuzzy term, resolve an overloaded word, record a hard-to-reverse decision as an ADR. It is the discipline `/interview-with-docs` drives to keep `GLOSSARY.md` clean.
- **`/codebase-design`**: the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) for designing a module's *shape*. `/tdd` and `/improve-codebase-architecture` both speak it.

### Standalone

Off the main flow entirely.

- **`/interview-me`**: the same interview as `/interview-with-docs`, but it writes no Interview log. For when you are not in a repo (a plan, a design, a piece of writing). In a repo use `/interview-with-docs`.
- **`/interview`**: the interview primitive itself. `/interview-me` and `/interview-with-docs` are the two named ways in, and `/triage`, `/wayfinder` and `/improve-codebase-architecture` run it internally. Reach for it directly only when you want the interview with no wrapper.
- **`/prototype`**: a throwaway program that answers one design question (does this state model feel right, what should this UI look like). The answer folds into the real code; the prototype is kept as a **primary source** on a throwaway branch out of main.
- **`/research`**: delegate reading legwork to a **background agent**. It investigates a question against **primary sources** and leaves a cited Markdown file. Take the file into the main flow at `/brainstorm` or `/interview-with-docs`.
- **`/to-questionnaire`**: for when the thing blocking you is in someone else's head. It interviews you about the send (who, what you need back) and writes them a questionnaire. What comes back is material for `/interview-with-docs` or `/to-spec`.
- **`/wizard`**: for steps only a **human** can take (credentials, CI secrets, a third-party dashboard, a one-off cutover). It generates an interactive bash script that opens each URL and captures each value. Model-invoked, so the agent reaches for it when it hits a wall only you can pass.
- **`/wait-what`**: the corrective for a message that did not land. The agent re-pitches what it just said with the context you were missing, in plain English, in the `GLOSSARY.md` vocabulary.
- **`/handoff`**: write a portable markdown file so another session can pick up the work.
- **`/teach`**: learn a concept over multiple sessions, using the current directory as a stateful workspace.
- **`/writing-for-agents`**: the reference for writing documents agents consume: skills, `AGENTS.md`, pointed-at docs.

### Precondition

**`/setup-skills`**: run once per repo, before the first engineering flow. It configures the issue tracker, triage labels, Context docs layout, model tiers and the agent-skills block. Re-run it to fill what is missing.

## Phase boundaries

A **phase** is a chunk of work inside a session: the interview, the implementation, the QA. At the **boundary** between two phases you have five options, and picking between them is the fuzziest decision in this map: **Continue**, **`/clear`**, **`/handoff`**, a **subagent**, **`/compact`**.

Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered tree: the five questions, the reasoning behind each branch, and why the primary-source cost makes **Continue** the one to rule out first. Decide **at** a boundary; mid-phase, continue or split the rest into subagents.
