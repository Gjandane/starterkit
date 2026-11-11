Review standards for this plugin: the judgement calls no script can make. Read at review, alongside [AGENTS.md](./AGENTS.md).

`scripts/check.sh` already enforces the mechanical rules (manifest and README placement, invocation flags, chain wording, em-dashes, dropped and renamed names). Report a mechanical breach only when the script misses it, and say the script needs the rule.

## Names

- **Distinct trigger word.** A model-invoked skill's name and description lead with a word that is rare in everyday requests, so the skill fires only when meant. Flag a name that doubles as a common word (a skill named after an ordinary verb or noun fires on unrelated requests).
- **One word, one concept.** A skill name, a tag, a status, a ticket type and a role each get their own word unless they are the same thing. Flag a word that now carries two meanings in one file, and two words that name one role.
- **Sibling shape.** A new or renamed skill matches the grammatical form of the skills beside it (verb names among verb names).

## Wording

- **Reword for meaning.** A sentence changed to satisfy a check still says what it said before and matches the wording of the rest of its file. Flag a file that now uses two words for one action.
- **Reread after bulk replace.** Every sentence touched by a search-and-replace reads as written by hand: articles agree (`a` / `an`), the verb fits its object, capitalisation fits its position.
- **Skill wording follows `writing-for-agents`.** Positive targets over prohibitions, one source of truth per meaning, every step ending on a checkable completion criterion.

## Flow

- **Flow map is current.** A diff that adds, renames, removes or re-routes a user-reachable skill also updates the Flow map in [`guide`](./skills/engineering/guide/SKILL.md).
- **Every printed command exists.** A command a skill tells the user to type names a skill in the manifest, with the plugin prefix.
