# Productivity

General workflow tools, not code-specific.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[brainstorm](./brainstorm/SKILL.md)**: Widen before narrowing: batches of 3 to 5 ideas per turn, kept in a resumable ideas file. Ends with a Picked section and a pointer to the interview.
- **[interview-me](./interview-me/SKILL.md)**: Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved.
- **[handoff](./handoff/SKILL.md)**: Compact the current conversation into a handoff document so another agent can continue the work.
- **[larper](./larper/SKILL.md)**: Draft a short LinkedIn post about the repo in plain language, after a short interview on what it says and which Insights go in. Printed in chat, never posted.
- **[sketchnotes](./sketchnotes/SKILL.md)**: Plan illustrated study notes from a topic or Markdown files: an interview on the study goal, prior knowledge and must-see details, then a sourced outline of each Learning objective with its study question and proposed drawing, and a print sample of one hard passage to approve: one in a saved House style, or a pick of three proposals in a fresh design you can save under a name, each in its own Look, or all in a reference image's Look once you approve its greyscale-safe palette.
- **[teach](./teach/SKILL.md)**: Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.
- **[to-questionnaire](./to-questionnaire/SKILL.md)**: Turn a decision you can't answer alone into a Markdown questionnaire for the one person who can (filled in async, or together over a meeting).
- **[wait-what](./wait-what/SKILL.md)**: Fire this the moment a message doesn't land. The agent re-pitches it with the context you're missing, in plain English, using your `GLOSSARY.md` vocabulary.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[inking](./inking/SKILL.md)**: Draw a printable sketchnote page in given style rules, render it at paper size with the fonts it ships, check that no ink crosses a label, and assemble the pages into one PDF.
- **[interview](./interview/SKILL.md)**: Interview the user relentlessly about a plan, decision, or idea until every branch of the design tree is resolved.
- **[writing-for-agents](./writing-for-agents/SKILL.md)**: Writing documents for agents: skills, AGENTS.md/CLAUDE.md, and any doc an agent reaches by a pointer.
