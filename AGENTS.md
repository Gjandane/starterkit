Rules for editing this plugin. The block that `setup-skills` writes into a user's repo is a different text and lives in that skill.

Skills are organized into bucket folders under `skills/`:

- `engineering/`: daily code work
- `productivity/`: daily non-code workflow tools
- `misc/`: kept around but rarely used, not promoted

`scripts/check.sh` enforces the mechanical rules (manifest and README placement, invocation flags, chain wording, em-dashes, old names) and names each broken one; the pre-commit hook runs it with `claude plugin validate . --strict`. After adding or renaming a skill, also run `scripts/load-test.sh`. After editing the `inking` skill's scripts or fonts, also run `python scripts/test_inking.py`. A Verify step that needs a real skill run drives it with `scripts/drive-skill.sh`, one turn per call. Review standards live in [CODING_STANDARDS.md](./CODING_STANDARDS.md).

The plugin ships exactly the **promoted** buckets (`engineering/`, `productivity/`): each promoted skill is in `.claude-plugin/plugin.json`'s `skills` array and linked to its `SKILL.md` from the top-level `README.md` and its bucket `README.md`, with a one-line description. Those READMEs group entries into **User-invoked** and **Model-invoked**; `misc/` skills appear only in the flat `misc/README.md`.

Every `SKILL.md` is either user-invoked (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`, reachable only by the human) or model-invoked (model- or user-reachable). See [.agents/invocation.md](./.agents/invocation.md).

Every chain site (a skill telling the agent to run another skill) uses one sentence that names the skill and no tool or path: "Load the `interview` skill." For two skills: "Load the `interview` and `domain-modeling` skills." Never name the `Skill` tool. A chain target is always model-invoked; never chain to a user-invoked skill.

Write or edit every skill with the `writing-for-agents` skill (and its `SKILL-MECHANICS.md`). Load it before proposing any wording.

[`guide`](./skills/engineering/guide/SKILL.md) holds the Flow map of every user-reachable skill and how they relate. Whenever you add, rename, remove, or change how a user-reachable skill fits the flows, re-read `guide`'s `SKILL.md` and update the Flow map. A skill it never mentions, or a stale one it still routes to, is a map that lies.

Only `setup-skills` writes the agent-skills block and the agent docs in a user's repo. Any change there keeps the second-run rule.

No em-dashes anywhere in this repo's prose (`SKILL.md` files, `README.md`s, ADRs, code comments). Where a sentence reaches for one, rewrite it with a comma, colon, period, parentheses, or a conjunction, whichever the sentence actually wants; never do a blind character substitution.
