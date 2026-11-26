# Launch block

The prompt that runs a whole wave at once: pasted into one Claude Code session, it opens a session per ticket, then merges and cleans up. Copy the block below into the rundown and fill its placeholders:

- `<K>`: the number of ticket lines.
- `<base>`: the Base branch.
- The ticket lines: one per ticket of the wave that is not done, in number order, each with the ticket reference (file path locally, issue number on a real tracker), the model name from the tier table and the effort. The session that runs the block turns the name into a full model id.

Keep every other word as written.

```
Before starting: every ticket below and the spec it links are committed on local <base>, and git status shows no tracked changes besides rundown.md. When either fails, stop and ask me whether to commit them. Record <base>'s commit as the run's start commit.
Open <K> parallel sessions, one per ticket below, each in its own worktree cut from local <base> (user_asked, no confirmation card).
Start prompt for each session: implement the ticket directly, starting immediately, no questions. Never tell a session to invoke /starterkit:builder or any slash command: those are user-only and the session will stall. Use the ticket's content as the spec.
A ticket with an `## Approved rules` section (or an older one that names a Learning objective, a study question and an approved sample) is a sketchnote content Issue: find the `builder` skill's SKILL.md once (under the plugin install, else search for the skill) and tell that session to read its "Sketchnote content Issue" section by absolute path and follow it for the pages, their render, the page checks and `## Pages`, in place of tdd. Every other ticket is implemented directly.
Pass each ticket's model and effort in the start call itself, using full model ids (e.g. claude-opus-5-5, claude-sonnet-5-5), not short names: a model or effort set after starting applies only from the session's next turn. If a call fails, stop and tell me; don't keep retrying.
Each session: finish every requirement in the ticket, run the ticket's Verify steps, tick every checkbox that is met, write ## Build notes on the ticket (at most five one-line notes: Modules added or removed, Interface names changed, new cross-module calls, mismatches with the docs; none when empty), mark the ticket resolved once all are ticked, commit on its branch, report anything unrun. A session can use subagents. Sessions never merge, rebase or push. Sessions never touch rundown.md; only the launching session writes it.
When all sessions report done, check each one's report and diff, then merge one at a time in ticket order: rebase the branch onto local <base>, fast-forward <base> to it. On conflicts, keep both sides' additions. No push. Run every command for a worktree as git -C <worktree> from the main checkout, so your shell's working directory stays there.
After all merges: archive the sessions first (releases Windows folder locks), then git worktree remove --force + git worktree prune, then git branch -d each merged branch. Delete only branches fully merged into <base>.
Then review the merged run as one change: since the start commit, against the run's tickets. Load the `code-review` skill. Fix each place one ticket's text still names something another ticket renamed or removed, and commit the fixes on <base>.
After the last merge, when the run changed a ticket: Load the `rundown` skill. Once, in this launching session.
Report: commit per ticket, unrun Verify steps, conflicts resolved, review fixes, anything not cleaned up. End with the next step rundown printed.

Tickets:
- <ticket reference> | model: <model> | effort: <effort>
```
