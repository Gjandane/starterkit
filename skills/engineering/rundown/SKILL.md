---
name: rundown
description: "Rundown: use when the user asks to refresh or rebuild the effort's checklist of commands. Rebuilds from ticket status and prints the next unchecked step."
argument-hint: "[effort path, e.g. .scratch/<effort>]"
---

# Rundown

Turn the effort's tickets into `.scratch/<effort>/rundown.md`: a checklist of commands in run order, start to finish, that the user pastes one step or one wave at a time. Mechanical work. Tickets in, file out. Pick no tier, give no advice.

Rebuild the whole file on every run. Ticket status is the only source of truth; a box the user ticked by hand is overwritten.

## Process

### 1. Pick the effort

Choose the entry path from what the user asked this turn:

- **Requested.** The user asked for the rundown, by typing `/rundown` or in words. Take the effort path from the user. Without one, list the folders in `.scratch/`: one folder is the effort, several means ask which, none means tell the user to run `/interview-with-docs` first. Create or overwrite its `rundown.md`, including a hand-written file.
- **Guarded.** Every other load, including a chain after a ticket change, follows these guards in order. Ask nothing; on any failed guard, skip silently and return to the caller without writing a file or printing a next step.
  1. Take the changed ticket supplied by the caller. Read its `**Scratch:**` line as the effort's folder. With no pointer, a local ticket uses the effort folder containing its `issues/` folder; a real-tracker ticket is skipped. Use these exact pointers, never a search of issue text.
  2. Open only that effort's existing `rundown.md`. Its first line must be `# Rundown: <effort>` and the next line must start with `Harness:`. Leave a missing file or any other shape alone.
  3. Read the `Source:` line immediately below `Harness:`. It must name a readable issues folder on a local tracker or a parent issue or spec reference on a real tracker. Use that source for the tickets in step 2. A missing, ambiguous or unreadable source is a failed guard.

The guarded path updates only this file. Keep the refreshed file uncommitted. On a real tracker it stays local; post nothing.

### 2. Read

- **Tickets.** On the requested path, use `.scratch/<effort>/issues/*.md` on a local tracker, or the parent issue or spec reference the user gives on a real tracker. On the guarded path, use only the existing file's `Source:`. Read the source's tickets, their `## Run` sections and their blocking links through the operations in `docs/agents/issue-tracker.md`. Record that same source in the generated file.
- **Tier table.** `docs/agents/model-tiers.md`, the column of the harness you are running in.
- **Base branch.** On Claude Code, the branch checked out now (`git branch --show-current`).
- **Nothing else.** Skip the spec body and the code. The one exception: the section headings of `.scratch/<effort>/ideas.md`, to see whether it has a Picked section.

Per ticket take: number, title, `Blocked by`, `Status`, `Type:` (wayfinder decision tickets only), Model tier, Effort, Where, Constraints, `**Prerequisite:** yes`. A field the ticket lacks prints as `not set`.

Derive each ticket's **Blocks**: the numbers of the tickets that list it in their `Blocked by`.

A ticket is **done** when its Status is `resolved` or `done` (local) or the issue is closed (tracker). A ticket with a `Type:` line is a **decision ticket**; every other ticket is a **build ticket**.

### 3. Resolve harness, commands and model names

Name the harness you run in: Claude Code or Codex.

| Harness     | Command syntax              | Tier column   |
| ----------- | --------------------------- | ------------- |
| Claude Code | `/starterkit:<skill> <arg>` | Claude Code   |
| Codex       | `$<skill> <arg>`            | Codex         |

Print the model name from the table in place of the tier. With no tier table, print the bare tier (`heavy`, `standard`, `light`) and add one line under the title: "No model tier table. Run `/setup-skills` to map tiers to model names." Write the setup command and every other command in the file, `/rundown` included, in the harness's own syntax.

### 4. Write the file

Sections in this order, which is the order the user runs them: each under a `##` heading, each wave under a `###` heading inside Build. Every step has the same shape:

````markdown
- [ ] **<NN> <ticket title>**. Blocked by: <numbers>. Blocks: <numbers>. Model: `<model>`, effort: `<effort>`, where: `<where>`. <one-clause note>
  ```
  <command>
  ```
````

- An empty `Blocked by` or `Blocks` prints `nothing`.
- The note appears only for a ticket with Constraints (state them in a clause), a step only a human can do, or a Where of `desktop` (say the plugin must be installed in the desktop app, see the README Install section). A step with none of these has no note.
- The command goes in its own code block, one command per block.
- A done step is `[x]`.
- Only steps with a ticket tick automatically from its status. Spec steps still collapse to done once build tickets exist; Retro and Ship stay unchecked.
- A **build step** is the step of one build ticket, Prerequisite or not. Its command runs the `builder` skill with the ticket reference (file path locally, issue number on a real tracker), then the **completion sentence** on the same line, exactly: "Finish every requirement in the ticket, then tick every checkbox in the ticket. You can use subagents to finish the ticket."
- Steps with no ticket (spec steps, the alternative, Retro, Ship) show the title and the model name only, plus Ship's `low` effort. Drop the fields they do not have.
- Tags ("interview", "same session", "optional", "fresh session") close the line after the note, in parentheses.

A build step on Claude Code:

````markdown
- [ ] **03 Export a report**. Blocked by: 01. Blocks: 05, 06. Model: `sonnet`, effort: `medium`, where: `cli`.
  ```
  /starterkit:builder .scratch/<effort>/issues/03-export-a-report.md Finish every requirement in the ticket, then tick every checkbox in the ticket. You can use subagents to finish the ticket.
  ```
````

**Title, harness and source lines.** Keep these three lines adjacent, with no blank lines between them:

```markdown
# Rundown: <effort>
Harness: <Claude Code or Codex>. Commands in its syntax, model names from its column of the tier table.
Source: <issues folder path, or parent issue or spec reference>
```

Use the issues folder path on a local tracker, or the parent issue or spec reference on a real tracker. With no tier table, say "tiers" in place of "model names" in the harness line and add the setup line below the source line.

**Rules.** A short list:

- One session per step: start a fresh session before each command, unless the step says "same session".
- Set the model and effort before you paste the command.
- Steps marked "interview" are conversations. Run one at a time.
- The tickets of one wave do not block each other. Run them one at a time, or all at once. On Claude Code the last sentence reads: "To run a wave all at once, paste its launch block into one session; it opens a session per ticket." On Codex: "To run a wave all at once, give each ticket its own session."

**Order.** The whole run at a glance: a code block with one line per section below, in run order. A wave line lists its ticket numbers, tagged "(parallel)" with two or more tickets not done and "(done)" with none.

```
Before you start: 01
Spec steps: done
Wave 1: 02, 03, 04 (parallel)
Wave 2: 05
Wave 3: 06, 07 (done)
Retro
Ship
```

**Before you start.** Only when a ticket carries `**Prerequisite:** yes`. List each Prerequisite ticket as a build step with the note "Prerequisite: finish before the build". Leave Prerequisite tickets out of the build waves.

**Spec steps.** In order, each tagged "same session" except where noted. Tier `heavy` for the interview, `standard` for the rest:

1. Brainstorm, only when `ideas.md` exists and has no Picked section.
2. Interview, marked "interview": the `interview-with-docs` skill.
3. The `to-spec` skill with `.scratch/<effort>/interview-log.md`.
4. The `review-spec` skill, labelled optional, with `<spec path>`.
5. The `to-tickets` skill with `<spec path>`. The `to-spec` skill prints the spec path, so these two steps carry the placeholder.

With decision tickets, list each before step 2 as its own step: command is the `wayfinder` skill with the ticket reference, tagged "interview" when its type is `interview` or `prototype`.

With any build ticket present, the spec steps have already run: collapse them to the line "Spec steps: done."

**Build.** Open with the alternative: the line "Or build everything on one branch (model `<heavy model>`):" and the `builder-spec` skill command with the spec path placeholder. It has no checkbox and is never the next step. Then the waves.

Compute waves from `Blocked by` over all build tickets, done or not, so a wave keeps its number across runs. Wave 1 is every ticket whose blockers are all Prerequisite tickets or none; wave N is every ticket whose blockers all sit in earlier waves. Within a wave, list every build step in number order, the done ones as `[x]`.

The heading counts the wave's tickets that are not done: "Wave N: one session" for one, "Wave N: up to K sessions in parallel" for K of two or more. A wave whose tickets are all done collapses to one line: "Wave N: done (<ticket numbers>)."

On Claude Code, a wave with two or more tickets not done opens with its **launch block**: the line "Paste this block into one session to run the whole wave:", then one code block built from [LAUNCH-BLOCK.md](LAUNCH-BLOCK.md). After it, the line "Or one ticket at a time:" and the wave's build steps. The launch block has no checkbox; the build steps carry them. On Codex a wave is its build steps alone.

With no build tickets, write the heading and one placeholder line: "No tickets yet. Run `/rundown` again after `to-tickets`." Never invent build steps.

**Retro.** One step, the `retro` skill with no argument: `heavy`, note "run before clearing the last build session".

**Ship.** One step, the `ship` skill with the effort path: `standard`, `low`, tagged "fresh session".

### 5. Print

Print the first unchecked step of the file, its command included, and the path of the file. When that step sits under a launch block, print the launch block in its place. When every box is checked, say so.

Done when the file is written and the next step or launch block is printed.
