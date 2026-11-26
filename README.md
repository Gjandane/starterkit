# starterkit

Agent skills for Claude Code that take a piece of work from idea to shipped commit. You get interview, spec, tickets, build, review and ship, plus a set of docs that carry what you decided from one piece of work to the next.

starterkit is a fork of [Matt Pocock's skills](https://github.com/mattpocock/skills) (v1.3.1, MIT). Most of the good ideas here are his. I changed the parts that kept breaking for me, and the [changes section](#what-changed-from-mattpocockskills-and-why) explains each one.

## Install

You need Claude Code 2.1.275 or later. Run this once in a terminal:

```bash
claude plugin install starterkit --marketplace gjandane/starterkit
```

This installs the plugin for your user, so it works in the CLI and in Code tab sessions of the Claude desktop app.

You can also install it from inside a Claude Code session:

```
/plugin marketplace add gjandane/starterkit
/plugin install starterkit@starterkit
```

To check it loaded, type `/starterkit:guide` in a session. You should get the guide skill.

To update later:

```bash
claude plugin marketplace update starterkit
```

## First steps in a repo

1. Run `/starterkit:setup-skills` once per repo. It asks where your issues live (GitHub, GitLab or local markdown files), which triage labels you use and how your docs are laid out, then writes that into `AGENTS.md`.
2. If the repo is older than the skills, run `/starterkit:bootstrap-context`. It reads the code and writes the docs the other skills expect.
3. Not sure what to run next? Ask `/starterkit:guide`. It answers in plain English and suggests one command.

The main flow for a feature looks like this. The steps in brackets are optional.

```
[brainstorm] -> interview-with-docs -> to-spec -> [review-spec] -> to-tickets
     -> rundown -> builder (per ticket) or builder-spec (whole spec)
     -> [retro] -> ship
```

## What changed from mattpocock/skills, and why

I used the upstream skills on real repos for a while. They work well for one piece of work done in one session. They fell apart in two places. In an existing repo, every interview started from zero. And across sessions, nothing survived a closed context window. Almost every change below fixes one of those two problems.

I kept upstream's folder layout and most skill names, so you can diff the two repos and see what moved.

### New skills

- **brainstorm.** The interview narrows from its first question, which is the wrong mode when you don't know what you want yet. brainstorm offers 3 to 5 ideas per turn and saves them in an ideas file you can come back to. It ends with a list of picked ideas for the interview.
- **bootstrap-context.** A repo that never used these skills has no glossary and no architecture doc, so the interview has nothing to read. This skill writes those docs from the existing code. You correct its list of modules before it starts. It never overwrites a doc that already exists.
- **review-spec.** The agent that wrote a spec can't see its own gaps. review-spec starts two fresh agents that never saw the interview. They report what to cut, what's missing and what contradicts itself, as one numbered list. You accept findings by number.
- **rundown.** Upstream left me rereading tickets to work out the next command. rundown writes a checklist of copy-paste commands for the whole effort and prints the next unchecked one. It rebuilds the list from ticket status every time you run it, and the skills that change tickets (`to-tickets`, `wayfinder`, `builder`, `builder-spec`) refresh an existing generated checklist for you, so you stop rerunning it after every build.
- **ship.** Upstream had no step that closes a piece of work, so the docs drifted away from the code after every build. ship updates the architecture doc to match what was built, marks the spec as shipped and deletes the scratch folder. All of that lands in one commit, and it asks every question before it writes anything.

### Changed skills

- **The interview reads the repo first.** Upstream started cold, and I re-explained the architecture every session. Now an Orient step matches what you want to change against the glossary and the module list. It reads only the docs that match, then gives you a summary of at most 10 lines before the first question.
- **The interview saves a log after every round.** A long interview used to die with its context window. Now `interview-log.md` records settled decisions, open questions and parked ideas. A new session picks up where the old one stopped.
- **Questions are easier to read.** I ran `/wait-what` after almost every round, so its rules are now part of the question format. Each question has one line on why it comes now, a yes/no question and a recommended answer. Reply "yes" to accept.
- **A living architecture doc.** The glossary holds words and ADRs hold single decisions. Nothing described the system as it is today. `ARCHITECTURE.md` fills that gap in at most 200 lines, with one short entry per module.
- **Specs are kept.** Upstream specs lived in a scratch folder and got lost. Now each spec is a numbered file in `docs/specs/` with an index, so a later change to an old feature can find the spec behind it.
- **Tickets say how to run them.** Each ticket now records a model tier, an effort level, where to run it (CLI, desktop or cloud), the steps that verify it and its constraints. `rundown` turns those into commands.
- **builder reads less and checks more.** It reads the ticket, the spec, the glossary, the architecture doc and the ADRs for the modules it touches, and nothing else. After code review it runs the ticket's verify steps. If one fails, the ticket stays open. It leaves build notes for `ship`.
- **Works in Codex too.** Upstream told the agent to call Claude Code's `Skill` tool when one skill loads another, and Codex has no such tool. Those lines now say "Load the X skill". `AGENTS.md` was a symlink, which breaks on Windows, and is now a real file. I test mostly in Claude Code, so treat Codex support as less proven.

### Renamed skills

| Upstream | Here | Why |
|---|---|---|
| `grilling` | `interview` | Says what it does |
| `grill-me` | `interview-me` | Follows `interview` |
| `grill-with-docs` | `interview-with-docs` | Follows `interview` |
| `implement` | `builder` | Pairs with `builder-spec` |
| `implement-spec` | `builder-spec` | Builds a whole spec |
| `ask-matt` | `guide` | It's a guide to this plugin, not Matt |
| `setup-matt-pocock-skills` | `setup-skills` | Shorter, and this is a different plugin |

### Removed

- The `misc` and `deprecated` skill folders.
- Upstream's publishing setup (docs site pages, changesets, release workflow, issue templates). This is a smaller project and doesn't need them.

## Skill reference

Skills split by who can start them. **User-invoked** skills run only when you type them, for example `/starterkit:interview-me`. They run a flow. **Model-invoked** skills can be typed too, and the agent also reaches for them by itself when the task fits. They hold the reusable rules. A user-invoked skill may load model-invoked skills but never another user-invoked one.

### Engineering

**User-invoked**

- **[guide](./skills/engineering/guide/SKILL.md).** Ask which skill or flow fits your situation, or how your repo works. Plain-English answer, at most one next command, writes no file.
- **[interview-with-docs](./skills/engineering/interview-with-docs/SKILL.md).** An interview that also builds your project's domain model. It sharpens terms and updates `GLOSSARY.md` and ADRs as it goes.
- **[triage](./skills/engineering/triage/SKILL.md).** Move issues through a fixed set of triage states.
- **[improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/SKILL.md).** Scan a codebase for places to simplify, show them in an HTML report, then interview you on the one you pick.
- **[bootstrap-context](./skills/engineering/bootstrap-context/SKILL.md).** Write the missing docs (architecture doc, glossary, ADRs, spec index) from an existing codebase. Resumable, never overwrites.
- **[setup-skills](./skills/engineering/setup-skills/SKILL.md).** Configure a repo for the engineering skills (issue tracker, triage labels, doc layout). Run once per repo before the others.
- **[to-spec](./skills/engineering/to-spec/SKILL.md).** Turn a finished interview log into a numbered spec file with an index line. No interview, only synthesis.
- **[review-spec](./skills/engineering/review-spec/SKILL.md).** Two reviewers who never saw the interview check a draft spec for things to cut, gaps and conflicts. One numbered list, accept by number.
- **[to-tickets](./skills/engineering/to-tickets/SKILL.md).** Break a plan, spec or conversation into thin end-to-end tickets. Each lists what blocks it and how to run it (model tier, effort, where, verify steps). Written to a local file or to a real tracker with native blocking links.
- **[builder](./skills/engineering/builder/SKILL.md).** Build one ticket. Prints its run line, drives `tdd` under the ticket's constraints, runs `code-review` and the verify steps before committing, and leaves build notes for `ship`.
- **[builder-spec](./skills/engineering/builder-spec/SKILL.md).** Build a whole spec on one branch. Sub-agents build every unblocked ticket in parallel under the `builder` rules. A stopped ticket stays open while the rest continue. Ends with `code-review` and a list of open tickets.
- **[ship](./skills/engineering/ship/SKILL.md).** Close a finished effort in one commit. Updates the architecture doc, marks the spec shipped, deletes scratch.
- **[wayfinder](./skills/engineering/wayfinder/SKILL.md).** Plan work too big for one session as a map of decision tickets, then settle them one at a time.
- **[retro](./skills/engineering/retro/SKILL.md).** After a session, suggest fixes to the agent's setup (navigation, checks, coding standards, steering files, tools), most severe first.

**Model-invoked**

- **[rundown](./skills/engineering/rundown/SKILL.md).** Create or rebuild the effort's checklist on request and print the next unchecked step. Skills that change a ticket (`to-tickets`, `wayfinder`, `builder`, `builder-spec`) refresh an existing generated checklist; it never creates one unasked.
- **[prototype](./skills/engineering/prototype/SKILL.md).** Build throwaway code to answer one design question. Either one HTML file for logic and state, or several very different UI versions you can switch between.
- **[diagnosing-bugs](./skills/engineering/diagnosing-bugs/SKILL.md).** A strict loop for hard bugs and slowdowns. First build a command that reliably shows the bug, then shrink it, list causes, test them one by one, fix, and keep the repro as a test.
- **[research](./skills/engineering/research/SKILL.md).** A background agent reads primary sources for a question and saves a Markdown file with every claim linked to its source.
- **[tdd](./skills/engineering/tdd/SKILL.md).** Red-green-refactor, one small slice at a time.
- **[domain-modeling](./skills/engineering/domain-modeling/SKILL.md).** Keep the project glossary honest. Challenges fuzzy terms, tests them with edge cases, and updates `GLOSSARY.md` and ADRs inline.
- **[codebase-design](./skills/engineering/codebase-design/SKILL.md).** Rules and vocabulary for deep modules, meaning a lot of behaviour behind a small interface that you can test through that interface.
- **[code-review](./skills/engineering/code-review/SKILL.md).** Two separate reviews of committed changes since a commit or branch, or uncommitted work including new files. Standards checks it against the repo's coding standards and common code smells. Spec checks it against the ticket or spec it came from.
- **[pr](./skills/engineering/pr/SKILL.md).** The shape of a pull request body. A small visual of the change, before/after proof, and a note on how hard it is to undo and how much could break.
- **[wizard](./skills/engineering/wizard/SKILL.md).** Generate an interactive bash script that walks you through steps only a human can do, like setting up credentials or clicking through a third-party dashboard.

### Productivity

**User-invoked**

- **[brainstorm](./skills/productivity/brainstorm/SKILL.md).** 3 to 5 ideas per turn, saved in a resumable ideas file. Ends with a picked list and a pointer to the interview.
- **[interview-me](./skills/productivity/interview-me/SKILL.md).** Get interviewed about a plan or design until every open decision is settled. Saves no files.
- **[handoff](./skills/productivity/handoff/SKILL.md).** Compact the current conversation into a handoff document so another agent can continue.
- **[larper](./skills/productivity/larper/SKILL.md).** Draft a short LinkedIn post about your repo for readers who don't code, after a short interview on what it says and which insights go in. Printed in chat, never posted.
- **[sketchnotes](./skills/productivity/sketchnotes/SKILL.md).** Plan illustrated study notes from a topic or your Markdown files. A short interview on your goal, what you know and what you must see, then an outline of each learning objective with its sources, study question and proposed drawing. A saved House style then draws one new sample of the hardest passage. A fresh design gives three proposals to compare, each in its own Look and structure. With a reference image, the three try its Look in three structures, once you approve its palette, adjusted where two colours would print too alike in greyscale. The sample you approve sets the drawing rules for the whole set, and you can save a fresh design's rules under a name for the next subject.
- **[teach](./skills/productivity/teach/SKILL.md).** Learn a new skill or concept over several sessions, with the current folder as the lesson workspace.
- **[to-questionnaire](./skills/productivity/to-questionnaire/SKILL.md).** Turn a decision only someone else can make into a Markdown questionnaire for them to fill in.
- **[wait-what](./skills/productivity/wait-what/SKILL.md).** Run it when a reply doesn't make sense. The agent explains again with the context you were missing, using your glossary's words.

**Model-invoked**

- **[inking](./skills/productivity/inking/SKILL.md).** Drawing tools for printable study pages, used by `sketchnotes` and `builder`. Draws a page in your style rules with the fonts it ships, renders it at paper size with Chrome or Edge, finds ink that crosses a label, and assembles the pages into one study-set PDF.
- **[interview](./skills/productivity/interview/SKILL.md).** The interview loop itself, used by `interview-me`, `interview-with-docs`, `triage`, `wayfinder` and `improve-codebase-architecture`.
- **[writing-for-agents](./skills/productivity/writing-for-agents/SKILL.md).** How to write skills, `AGENTS.md`/`CLAUDE.md` and other docs an agent reads.

## Working on the plugin

Clone the repo and load your checkout in the CLI:

```bash
claude --plugin-dir <path-to-checkout>
```

Rules for editing skills are in [AGENTS.md](./AGENTS.md). Run `bash scripts/check.sh` before committing.

## License

MIT, same as upstream. See [LICENSE](./LICENSE). The fonts in `skills/productivity/inking/fonts/` are under the SIL Open Font License, each with its licence beside it.
