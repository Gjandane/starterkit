---
name: to-tickets
description: Break a spec, plan, or the current conversation into tracer-bullet tickets, each declaring its blocking edges and Run metadata (Model tier, effort, where, Verify), published to the configured tracker.
disable-model-invocation: true
---

# To Tickets

Break a spec, plan, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it and its **Run metadata** (how to run it).

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-skills`.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

When the source is a spec file, read the spec, the glossary and the Architecture doc in full. The spec carries the settled decisions, so the Interview log stays closed. When the spec has no `Reviewed:` line, say so in one line ("Spec not reviewed; proceeding.") and carry on.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Prerequisites come first.** Each entry in the spec's `## Prerequisites` section becomes its own ticket, marked `Prerequisite`, numbered before every other ticket, and listed in the blockers of every ticket that touches its Module, even one another blocker already gates. An entry that names no Module becomes no ticket; say so in one line: "Prerequisite '<entry>' names no Module; no ticket made."

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

Give each ticket its Run metadata by the rules below.

<run-metadata>

- **Model tier**: `heavy`, `standard` or `light`. Default `standard`. `heavy` when the ticket touches a Module boundary, creates an interface other tickets depend on, or is hard to undo. `light` for mechanical work. Record the tier only, never a model name.
- **Effort**: `low`, `medium` or `high`. Default `medium`. `high` when the acceptance criteria leave design open, `low` when they fully specify the work.
- **Where**: `desktop`, `cli` or `cloud`, the least-capable place that works. `desktop` only when Verify needs the browser (the plugin must then be installed in the Claude desktop app, since `--plugin-dir` is CLI only), `cloud` only when the ticket is safe to run unattended, otherwise `cli`.
- **Verify**: the steps that show the ticket works, each one a thing to run or check. Verify sits apart from the acceptance criteria: criteria say what must be true, Verify says how to see it.
- **Constraints** (optional): limits the builder must respect that the criteria do not state.

</run-metadata>

**Every Verify step runs somewhere.** `Where` names the harness surface; the **environment** is what the step runs against (a test command, a dev server, a deploy target, seeded data, a device). For each Verify step, find that environment in the repo: scripts, config files, README, deploy config. A step with an environment it can run against passes. A step whose environment the repo cannot provide (a UI that only runs once deployed, a seeded database nothing seeds, a device with no emulator) has a **missing environment**. Collect each one per ticket.

A missing environment becomes a proposed **environment ticket**: a ticket that sets it up, numbered before the tickets it serves and listed in the blockers of every ticket whose Verify needs it. Its own Verify shows the environment up (the server answers, the deploy loads). Do not mark it `Prerequisite` until the user approves it in the quiz.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **Run**: Model tier, effort and where, on one line (for example `heavy · high · cli`)
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?
- Any tier, effort or where to change? (for example "3 light")

For each missing environment, name it per ticket ("03 and 04 Verify against a deployed web app; the repo has no deploy config or local server") and show the proposed environment ticket beside it. Ask: add the ticket as a Prerequisite, or keep the Verify steps as written? On approval, mark the environment ticket `Prerequisite: yes`. When the user keeps the steps as written, publish them unchanged. With no missing environment, say nothing about environments.

Overrides ride in the same reply; there is no separate Run metadata round. Iterate until the user approves the breakdown, and publish the Run metadata as last approved.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets. **How** depends on the tracker `/setup-skills` configured; the tickets are the same either way, only the shape of the blocking edges and Run metadata changes:

- **Local files** → write one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (Prerequisites, then other blockers, first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the local ticket template below: one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (Prerequisites, then other blockers, first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. If the source was an existing issue, make each ticket its sub-issue (tracker doc's operation). Apply the `ready-for-agent` triage label unless instructed otherwise; the tickets are agent-grabbable by construction. Run metadata, Verify included, lives in the issue body's `## Run` section; labels carry triage state only.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

**Model tier:** standard
**Effort:** medium
**Where:** cli
**Constraints:** the limits, or omit the line when none
**Prerequisite:** yes (only on a Prerequisite ticket; omit otherwise)

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

**Verify:**

- Verify step 1
- Verify step 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Run

**Model tier:** standard
**Effort:** medium
**Where:** cli
**Constraints:** the limits, or omit the line when none
**Prerequisite:** yes (only on a Prerequisite ticket; omit otherwise)

**Verify:**

- Verify step 1
- Verify step 2

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit this section when blockers were set as native edges.

</issue-template>

In either form, avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

### 6. Flip the spec to `building`

When the source is a spec file, change its `Status:` line from `draft` to `building`, and change `draft` to `building` in its line in the Spec index (`docs/specs/README.md`). When the status is anything other than `draft`, leave the spec and its index line as they are.

### 7. End

End with this line, exactly: "Tickets changed. Run `/rundown` to refresh the checklist."
