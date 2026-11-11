# Orient step

Step one of the interview, inside a repo. Skip it outside a repo. It reports and never edits a Context doc or decides a **Prerequisite**. Paths for the Context docs are in `docs/agents/context-docs.md`; when that file is missing, look for `GLOSSARY.md` and `ARCHITECTURE.md` at the root.

## 1. Resume check

Look for `.scratch/*/interview-log.md` files with `Status: open`. When any exist, offer to resume, and ask which when there are several. A path argument resumes that log without the offer. On "no", run fresh from step 2.

On resume, run **light**: read the log, the glossary and the Architecture doc, trust Facts found, and reread a source only when a question needs it. Then recompute the frontier and ask it as the next round. Skip steps 2 to 5.

## 2. Find what relates

"Related" means the words of the concern matched against glossary terms and **Module** names. Do this yourself, with no search sub-agent.

- Multi-context repo: read the context map (`GLOSSARY-MAP.md`) first, then only the matched contexts.
- More than 3 Modules match: ask one narrowing question before reading on.
- No Module matches: say "no existing module matches" and go on. A new feature is the normal path.
- No Context docs at all: run **code-only**. In step 3 read only the ideas file, and in step 4 limit the sub-agent to the paths the concern names, or to the top-level source folders when it names none. Print one line suggesting the Brownfield bootstrap, in place of "no existing module matches". Never block on it.

## 3. Read

In full:

- the glossary
- the Architecture doc
- the Picked section and the picked Idea bucket of `.scratch/<effort>/ideas.md`, when the file exists
- the ADRs and specs linked from matched Modules

By title only: the Spec index and the ADR folder listing.

## 4. Check the code

Skip when no Module matches, except in a code-only run. Otherwise dispatch one read-only sub-agent, limited to the matched Modules' paths. It returns entry points, key files and doc-versus-code mismatches, as a short list with no file dumps.

## 5. Summarize and start

1. Print the bootstrap line and "no existing module matches" first, when they apply. Then print "what I found": at most 10 lines, each a path plus a finding, mismatches included. These lines are the Facts found.
2. Create the Interview log as [INTERVIEW-LOG.md](./INTERVIEW-LOG.md) describes, with Concern, those Facts found, and Open questions seeded from the Picked section plus the round 1 questions.
3. Ask round 1 in the same message.

Done when the summary is printed, the log exists and round 1 is asked.
