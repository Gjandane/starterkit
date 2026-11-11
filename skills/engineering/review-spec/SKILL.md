---
name: review-spec
description: "Review a draft spec with reviewers who never saw the interview: Cut, Gaps, Conflicts. One numbered list, one reply."
disable-model-invocation: true
---

Review a draft spec with fresh eyes. You propose and the user decides; never settle a question yourself.

Recommended after `/to-spec`, never required. Works on any draft spec.

## Process

1. Take the spec path from the user, else ask. Read the spec header: `Effort:` names the folder of the Interview log, `.scratch/<effort>/interview-log.md`. Stop when the spec is missing.

2. Dispatch two read-only sub-agents in parallel. Neither sees this conversation, so each prompt is self-contained: spec path, the paths below, and its axes. Each returns findings as a list, capped at 5 per axis.

   Orient reading path, given to both: the glossary and Architecture doc in full (paths in `docs/agents/context-docs.md`, else `GLOSSARY.md` and `ARCHITECTURE.md` at the root), then only the ADRs and specs linked from the Modules the spec touches. The Spec index (`docs/specs/README.md`) is the fallback for work not yet built.

   - **Fresh-eyes** reads the spec and the Orient reading path. Axes:
     - **Cut**: a section, story or decision the problem does not need.
     - **Gaps**: something the spec needs and lacks, such as a story with no decision behind it, an unnamed Module, a Prerequisite that names no Module or a missing test seam.
   - **Conflicts** reads the same plus the Interview log. Axis:
     - **Conflicts**: a spec line that contradicts a Settled decision, an ADR or a glossary term. Cite the Settled decision by its `D` number.

   Every finding quotes the spec line and is one of:
   - **Edit**: the exact change to the draft.
   - **Open question**: a question only the user can settle.

   Without sub-agents, tell the user to run this skill in a fresh session, so the spec is read cold. Do Cut and Gaps first from the spec and the Orient reading path, then open the Interview log and do Conflicts.

3. Screen Cut findings against the Interview log. Fresh-eyes never saw it, so you do. Read the Settled decisions; every Cut **Edit** that removes the last spec line carrying a Settled decision becomes an **Open question** that cites that decision's `D` number. Dropping a Settled decision reopens the interview, so only the user can accept it.

4. Print one numbered list, numbers running across all axes, under the headings Cut, Gaps, Conflicts. Each line: number, kind (Edit or Open question), the quoted spec line, the finding. An axis with no findings says "none". At most 5 per axis. When a reviewer returns more, keep the 5 that matter most.

5. End with one line asking the user to reply once with the numbers to accept, for example "accept 1, 4". Ask nothing else. Any number not named is rejected.

6. Apply the reply in one pass:
   - Accepted **Edit**: apply it to the spec draft.
   - Accepted **Open question**: append it to Open questions in the Interview log as the next `Q` number, tagged `(Spec review)`, and set the log's `Status:` to `open`.
   - Rejected finding: leave no record, in the spec or the log.

7. Check the edited spec against the Interview log: every Settled decision still appears in the spec body. A Settled decision the spec no longer carries, whatever dropped it, is listed with its `D` number and the line that carried it, just before the closing line.

8. Add `Reviewed: <today's date>` directly under the spec's `Status:` line, replacing an earlier `Reviewed:` line.

9. When any Open question was accepted, end with: "Interview log reopened. Resume the interview with `<log path>`, then rerun `/to-spec`." Otherwise end with: "Review applied to `<spec path>`. Next: `/to-tickets <spec path>`."

Done when the reply is applied, every Settled decision is in the spec or listed as missing, the `Reviewed:` line is in the spec and the closing line is printed.
