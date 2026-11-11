---
name: to-spec
description: "Turn a finished Interview log into a numbered spec file at docs/specs/ and add its index line. No interview, just synthesis."
disable-model-invocation: true
---

Turn the Interview log into a spec. Synthesize; the only question for the user is the one seam and `Amends:`/`Supersedes:` check in step 3.

Use the glossary's vocabulary throughout and respect ADRs in the area.

## Process

1. Read the Interview log first: the path given, else the one in `.scratch/<effort>/interview-log.md` the user means (ask when several). When its `Status:` is `open`, stop: write nothing, tell the user to resume the interview.

2. Read the Orient reading path for the Modules the log names: glossary and Architecture doc in full, then only the ADRs and specs linked from those Modules. Fall back to the Spec index (`docs/specs/README.md`) for work not yet built. Facts found in the log stands in for code exploration.

3. Sketch the seams at which you will test the feature. Prefer existing seams, at the highest point possible. The fewer seams across the codebase, the better; the ideal number is one. Explore code only as far as this needs.

   From the specs on matched Modules, and the index's `draft` or `building` specs touching them, propose `Amends:` or `Supersedes:` when one applies. Ask the user to confirm the proposed seams and that line, and wait for the answer. Step 4 starts only after they reply. Leave the old spec alone.

4. Write the spec to `docs/specs/NNNN-<slug>.md`, whatever the tracker. A tracker issue only links to the file.
   - `NNNN` is the highest number in `docs/specs/` plus one, 4 digits, `0001` when empty. Slug is short kebab-case.
   - Header lines, in order: `Status: draft`, `Amends: <link>` or `Supersedes: <link>` (only when one applies), `Effort: .scratch/<effort>/`. Then a blank line and `# <Title>`.
   - Every Settled decision appears in the body. Never cite `D` numbers.
   - Parked items become the Out of Scope list.
   - Implementation Decisions name Modules (as the Architecture doc names them) and their interfaces. Facts found lists files; translate each to its owning Module.
   - Copy each `Prerequisite` decision that names a Module into `## Prerequisites`, with its Module. A `Prerequisite` decision that names no Module goes to Implementation Decisions as a plain decision; tell the user in one line. Omit the section when no entry names a Module.
   - Use the template below.

5. In the same step, append the index line to `docs/specs/README.md`, creating the index if absent (heading `# Specs`). One list line:

   ```
   - 0002 [Credit notes](0002-credit-notes.md), draft: <one-line gist>. Amends [0001 Recurring invoices](0001-recurring-invoices.md)
   ```

   Drop the trailing `Amends`/`Supersedes` part when none applies.

6. End with this line, exactly: "Spec saved to `<path>`. Optional: run `/review-spec <path>` in this session. Then run `/to-tickets <path>`."

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Prerequisites

Each `Prerequisite` decision from the Interview log that names a Module. Omit when none.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

The log's Parked items, each with why it waits.

## Further Notes

Any further notes about the feature.

</spec-template>
