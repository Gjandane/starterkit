# Launch block

The prompt that runs a whole wave at once: pasted into one Claude Code session, it opens a session per ticket, then merges and cleans up. Copy the block below into the rundown and fill its placeholders:

- `<K>`: the number of ticket lines.
- `<base>`: the Base branch.
- The ticket lines: one per ticket of the wave that is not done, in number order, each with the ticket reference (file path locally, issue number on a real tracker), the model name from the tier table and the effort. The session that runs the block turns the name into a full model id.

Keep every other word as written.

```
Open <K> parallel sessions, one per ticket below, each in its own worktree (user_asked, no confirmation card).
Start prompt for each session: implement the ticket directly, starting immediately, no questions. Never tell a session to invoke /starterkit:builder or any slash command: those are user-only and the session will stall. Use the ticket's content as the spec.
Set model and effort right after starting, using full model ids (e.g. claude-opus-5-5, claude-sonnet-5-5), not short names. If a call fails, stop and tell me; don't keep retrying.
Each session: finish every requirement in the ticket, run the ticket's Verify steps, tick every checkbox that is met, mark the ticket resolved once all are ticked, commit on its branch, report anything unrun. A session can use subagents. Sessions never merge, rebase or push.
When all sessions report done, check each one's report and diff, then merge one at a time in ticket order: rebase the branch onto local <base> (git -C the worktree), fast-forward <base> to it. On conflicts, keep both sides' additions. No push.
After all merges: archive the sessions first (releases Windows folder locks), then git worktree remove --force + git worktree prune, then git branch -d each merged branch. Delete only branches fully merged into <base>.
Report: commit per ticket, unrun Verify steps, conflicts resolved, anything not cleaned up.

Tickets:
- <ticket reference> | model: <model> | effort: <effort>
```
