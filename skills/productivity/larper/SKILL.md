---
name: larper
description: Draft a short LinkedIn post about this repo in plain language, after a short interview on what the post says. Printed in chat, never posted.
disable-model-invocation: true
---

Draft a LinkedIn post that shows off this repo to a reader who does not code: what it does, the problem it solves and how. The draft is printed in chat. The user posts it themselves, and the repo stays untouched.

An **Insight** is a lesson or choice from the project that the user approved for the post. The user may bring their own. You propose one only from a source in the repo: an ADR, a spec decision, a commit.

## Process

1. **Read the repo.** Read the README, the Context docs (paths in `docs/agents/context-docs.md`, else `GLOSSARY.md`, `ARCHITECTURE.md`, `docs/adr/` and `docs/specs/`) and the recent git log. Stop reading there. Take the repo link from `git remote`, written as the `https://` address a browser opens. In a thin repo (no README and no Context docs), read the git log and the top-level folder names instead. Done when you can say in two sentences what the project does and which problem it solves, or you know that only the user can.

2. **Interview.** Load the `interview` skill. Skip its Orient step, and write no Interview log and no Context docs. The design tree has these branches, and each recommended answer comes from step 1:
   - **Reader:** which reader who does not code the post is for (a recruiter, a client, a former colleague).
   - **Angle:** what the user is proudest of, and the one thing the reader takes away.
   - **Problem:** the problem the project solves, in the user's words. In a thin repo, also what the project does.
   - **Insights:** a list of up to 6 candidate Insights, labelled `I1` to `I6`, each one line followed by its source in the repo. The user replies with the labels to keep (`I1 I3`) and any Insights of their own. A candidate with no source is left off the list, and a repo with no sourced candidate gets the line "No Insight found in the repo" in place of the list.
   - **Repo URL:** asked only when there is no git remote.

   A post carries 2 to 3 Insights. When the user approves more than 3, ask which to keep. When they approve fewer than 2, the post carries what they approved, and with none it has no Insight part. Done when every branch is settled and the user confirms the shared understanding.

3. **Write the post.** Follow Post rules below. Then audit the draft: ask "what makes this read as AI-written?" and fix each tell you find. Print it in chat, with 2 alternative hooks under it. When the user replies with changes in plain words, apply them and print the post again. Done when the post is printed and every Post rule holds.

## Post rules

**Order:**

1. Hook: 2 lines that carry the Angle. LinkedIn shows these before "see more", so they carry the reason to read on.
2. The problem.
3. What the project does and how.
4. The approved Insights.
5. The repo link.
6. 3 hashtags, on the last line.

**Length:** 120 to 200 words, counted from the hook through the last Insight. The link, the hashtags and the alternative hooks are outside the count.

**Voice:** first person, confident and plain. State what was built and what it changed. The post is sincere; the skill's name is the only joke.

**Reader:** the Reader from the interview, who does not code, follows every sentence. Each technical term is swapped for everyday words or explained in a few words. The work is described in words: code, file names and commands stay out of the post.

**Plain language:**

- Every claim is a fact the repo or the user backs. A word that only praises (excited, thrilled, game-changing, powerful, seamless) is cut.
- Use the plain word: "use", "is", "has", "help", "many". Words that mark AI text (delve, showcase, pivotal, crucial, enhance, foster, landscape, testament, underscore, leverage, serves as, boasts) get the plain word in their place.
- Sentences read as a person talks: uneven lengths, direct statements, one idea each. Each names who acts, in the active voice. A trailing "-ing" clause (highlighting, ensuring, reflecting) becomes its own sentence with a fact, or is cut.
- A list has as many items as there are facts, and the last sentence before the link adds a fact.
- A point is stated once, as what it is. Cut a question the next sentence answers, and a "not X, but Y" contrast.
- Plain text, no emoji.
