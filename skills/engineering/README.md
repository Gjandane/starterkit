# Engineering

Skills I use daily for code work.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[guide](./guide/SKILL.md)**: Ask which skill or flow fits your situation, or how your repo works. Plain-English answer, at most one next command, writes no file.
- **[bootstrap-context](./bootstrap-context/SKILL.md)**: Write the missing Context docs (Architecture doc, glossary, ADRs, Spec index) from an existing codebase. Resumable, never overwrites.
- **[interview-with-docs](./interview-with-docs/SKILL.md)**: Interview session that also builds your project's domain model, sharpening terminology and updating `GLOSSARY.md` and ADRs inline.
- **[triage](./triage/SKILL.md)**: Move issues through a state machine of triage roles.
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)**: Scan a codebase for deepening opportunities, present them as a visual HTML report, then interview you on whichever one you pick.
- **[setup-skills](./setup-skills/SKILL.md)**: Configure this repo for the engineering skills (issue tracker, triage labels, domain doc layout). Run once per repo.
- **[to-spec](./to-spec/SKILL.md)**: Turn a done Interview log into a numbered spec file with a Spec index line.
- **[review-spec](./review-spec/SKILL.md)**: Review a draft spec with reviewers who never saw the interview, on three axes: Cut, Gaps, Conflicts. One numbered list, accept by number.
- **[to-tickets](./to-tickets/SKILL.md)**: Break any plan, spec, or conversation into a set of tracer-bullet tickets, each declaring its blocking edges and Run metadata (Model tier, effort, where, Verify), whether as text in a local file or as native blocking links on a real tracker.
- **[builder](./builder/SKILL.md)**: Build one ticket with the right context and no more: prints its run line, drives `/tdd` with the ticket's Constraints, runs `/code-review` then the ticket's Verify steps before committing, and leaves Build notes for `ship`.
- **[ship](./ship/SKILL.md)**: Close a finished effort in one commit: update the Architecture doc to what now exists, mark the spec shipped, delete Scratch. Every question comes before the first write.
- **[builder-spec](./builder-spec/SKILL.md)**: Build a whole spec on one integration branch: implementer sub-agents build the task graph's ready frontier in parallel under the `/builder` rules, a stopped ticket stays open while the rest continue, and it ends with `/code-review` and a report of open tickets.
- **[wayfinder](./wayfinder/SKILL.md)**: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on the issue tracker, resolved one at a time until the way to the destination is clear.
- **[retro](./retro/SKILL.md)**: Suggest improvements to the coding agent's environment (navigation, automated checks, coding standards, steering files, tooling) after a session, most severe first.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[rundown](./rundown/SKILL.md)**: Create or rebuild the effort's checklist on request and print the next unchecked step. After resolving a ticket, `builder` refreshes an existing generated checklist.
- **[prototype](./prototype/SKILL.md)**: Build a throwaway prototype to answer a design question: a single shareable HTML file for state/logic, or several toggleable UI variations.

- **[diagnosing-bugs](./diagnosing-bugs/SKILL.md)**: Disciplined diagnosis loop for hard bugs and performance regressions: build a feedback loop that goes red on this bug → minimise → hypothesise → instrument → fix → regression-test.
- **[research](./research/SKILL.md)**: Investigate a question against high-trust primary sources and capture the findings as a cited Markdown file in the repo, run as a background agent.
- **[tdd](./tdd/SKILL.md)**: Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **[domain-modeling](./domain-modeling/SKILL.md)**: Actively build and sharpen a project's domain model by challenging terms, stress-testing with scenarios, and updating `GLOSSARY.md` and ADRs inline.
- **[codebase-design](./codebase-design/SKILL.md)**: Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface.
- **[code-review](./code-review/SKILL.md)**: Two-axis review of the diff since a fixed point: **Standards** (does it follow the repo's coding standards, plus a Fowler smell baseline?) and **Spec** (does it faithfully build the originating issue/spec?), run as parallel sub-agents.
- **[pr](./pr/SKILL.md)**: The shape a pull request body should take: a summary as the smallest visual that makes the change clear, before/after evidence that it works, and a merge-danger call (one-way or two-way door, plus blast radius).
- **[wizard](./wizard/SKILL.md)**: Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover.
