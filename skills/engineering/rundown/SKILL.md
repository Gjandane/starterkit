---
name: rundown
description: "Write a checklist of copy-paste commands for a whole effort, rebuilt from ticket status on every run, and print the next unchecked step."
disable-model-invocation: true
argument-hint: "[effort path, e.g. .scratch/<effort>]"
---

# Rundown

Turn the effort's tickets into `.scratch/<effort>/rundown.md`: a checklist of commands the user pastes one at a time. Mechanical work. Tickets in, file out. Ask nothing beyond the effort path, pick no tier, give no advice.

Rebuild the whole file on every run. Ticket status is the only source of truth; a box the user ticked by hand is overwritten.

## Process

### 1. Pick the effort

Take the path from the user. Without one, list the folders in `.scratch/`: one folder is the effort, several means ask which, none means tell the user to run `/interview-with-docs` first.

### 2. Read

- **Tickets.** On a local tracker, `.scratch/<effort>/issues/*.md`. On a real tracker, the parent issue or spec reference the user gives; read its child issues, their `## Run` sections and their blocking links through the operations in `docs/agents/issue-tracker.md`.
- **Tier table.** `docs/agents/model-tiers.md`, the column of the harness you are running in.
- **Nothing else.** Skip the spec body and the code. The one exception: the section headings of `.scratch/<effort>/ideas.md`, to see whether it has a Picked section.

Per ticket take: title, `Blocked by`, `Status`, `Type:` (wayfinder decision tickets only), Model tier, Effort, Where, Constraints, `**Prerequisite:** yes`. A field the ticket lacks prints as `not set`.

A ticket is **done** when its Status is `resolved` or `done` (local) or the issue is closed (tracker). A ticket with a `Type:` line is a **decision ticket**; every other ticket is a **build ticket**.

### 3. Resolve harness, commands and model names

Name the harness you run in: Claude Code or Codex.

| Harness     | Command syntax              | Tier column   |
| ----------- | --------------------------- | ------------- |
| Claude Code | `/starterkit:<skill> <arg>` | Claude Code   |
| Codex       | `$<skill> <arg>`            | Codex         |

Print the model name from the table in place of the tier. With no tier table, print the bare tier (`heavy`, `standard`, `light`) and add one line under the title: "No model tier table. Run `/setup-skills` to map tiers to model names." Write the setup command and every other command in the file, `/rundown` included, in the harness's own syntax.

### 4. Write the file

Sections in this order. Every step has the same shape:

````markdown
- [ ] **<ticket title>**: `<model>` · `<effort>` · `<where>`. <one-clause note>
  ```
  <command>
  ```
````

- The model, effort and Where sit on one line. The note appears only for a ticket with Constraints (state them in a clause), a step only a human can do, or a Where of `desktop` (say the plugin must be installed in the desktop app, see the README Install section). A step with none of these has no note.
- The command goes in its own code block, one command per block.
- A done step is `[x]`.
- Steps with no ticket (spec steps, the alternative, Retro, Ship) show the model name only, plus Ship's `low`. Drop the separators they do not use.
- Tags ("interview", "same session", "optional", "fresh session", "can run in parallel") close the line after the note, in parentheses.
- Write the title without its ticket number.

**Title and harness line.**

```markdown
# Rundown: <effort>

Harness: <Claude Code or Codex>. Commands in its syntax, model names from its column of the tier table.
```

With no tier table, say "tiers" in place of "model names" in that line and add the setup line right below it.

**Rules.** A short list:

- Fresh session per step unless the step says "same session".
- Set the model and effort before you paste the command.
- Steps marked "interview" are conversations. Run one at a time.

**Before you start.** Only when a ticket carries `**Prerequisite:** yes`. List each Prerequisite ticket as a build step (shape above) with the note "Prerequisite: finish before the build". Leave Prerequisite tickets out of the build waves.

**Spec steps.** In order, each tagged "same session" except where noted. Tier `heavy` for the interview, `standard` for the rest:

1. Brainstorm, only when `ideas.md` exists and has no Picked section.
2. Interview, marked "interview": the `interview-with-docs` skill.
3. The `to-spec` skill with `.scratch/<effort>/interview-log.md`.
4. The `review-spec` skill, labelled optional, with `<spec path>`.
5. The `to-tickets` skill with `<spec path>`. The `to-spec` skill prints the spec path, so these two steps carry the placeholder.

With decision tickets, list each before step 2 as its own step: command is the `wayfinder` skill with the ticket reference, tagged "interview" when its type is `interview` or `prototype`.

With any build ticket present, the spec steps have already run: collapse them to the line "Spec steps: done."

**Build.** Open with the alternative: the line "Or build everything on one branch:" and the `builder-spec` skill command with the spec path placeholder, model `heavy`. It has no checkbox and is never the next step. Then the waves.

Compute waves from `Blocked by` over all build tickets, done or not, so a wave keeps its number across runs. Wave 1 is every ticket whose blockers are all Prerequisite tickets or none; wave N is every ticket whose blockers all sit in earlier waves. Heading: "Wave N" plus the ticket numbers its tickets wait on, for example "Wave 3 (waits on 03, 05)". Within a wave, list tickets in number order. Each step runs the `builder` skill with the ticket reference (file path locally, issue number on a real tracker). A wave whose tickets are all done collapses to one line: "Wave N: done (<ticket numbers>)." Tag a ticket whose Where is `cloud` with "can run in parallel" when another `cloud` ticket sits in its wave. Make no parallel claim for other tickets.

With no build tickets, write the heading and one placeholder line: "No tickets yet. Run `/rundown` again after `to-tickets`." Never invent build steps.

**Retro.** One step, the `retro` skill, note "run before clearing the last build session".

**Ship.** One step, the `ship` skill with the effort path: `standard`, `low`, tagged "fresh session".

### 5. Print

Print the first unchecked step of the file, its command included, and the path of the file. When every box is checked, say so.

Done when the file is written and the next step is printed.
