#!/usr/bin/env bash
# Structural checks for the plugin. Exit 1 if any rule is broken; each failure
# names the file and the rule. Built on scripts/list-skills.sh.
# Usage: scripts/check.sh [plugin-root]   (default: the folder above scripts/)
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${1:-$HERE/..}" && pwd)"
cd "$ROOT"

FAILS=0
fail() { echo "FAIL $1: $2"; FAILS=$((FAILS + 1)); }

EMDASH=$(printf '\xe2\x80\x94')

# Frontmatter value of a key in a SKILL.md, empty if absent.
fm() { awk -v k="$2" 'NR==1&&$0!="---"{exit} NR>1&&$0=="---"{exit} index($0,k":")==1{sub(k": *","");print;exit}' "$1"; }

# Every file the checks read, minus .git and node_modules. In a git checkout:
# tracked plus untracked-not-ignored, so session worktrees under
# .claude/worktrees/ stay out. Outside git: every file.
all_files() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git ls-files -co --exclude-standard -- . ':(exclude).claude/worktrees'
  else
    find . -type f -not -path './.git/*' | sed 's|^\./||'
  fi | grep -Ev '(^|/)node_modules/' | while IFS= read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done | sort
}

declare -A INVOKED # skill name -> user | model
MANIFEST="$(cat .claude-plugin/plugin.json 2>/dev/null)"

mapfile -t SKILLS < <(bash "$HERE/list-skills.sh" 2>/dev/null | grep -E '^skills/' || true)
[ "${#SKILLS[@]}" -gt 0 ] || { fail "skills/" "no SKILL.md found"; }

for f in "${SKILLS[@]}"; do
  dir="$(dirname "$f")"; name="$(basename "$dir")"; bucket="$(basename "$(dirname "$dir")")"

  # Rule: promoted/misc placement against manifest and READMEs
  in_manifest=0; grep -qF "\"./$dir\"" <<<"$MANIFEST" && in_manifest=1
  if [ "$bucket" = misc ]; then
    [ "$in_manifest" = 1 ] && fail "$f" "misc skill is listed in .claude-plugin/plugin.json"
    grep -qF "skills/misc/$name/SKILL.md" README.md && fail "README.md" "misc skill '$name' is referenced in the top-level README"
  else
    [ "$in_manifest" = 1 ] || fail "$f" "promoted skill missing from .claude-plugin/plugin.json skills array"
    grep -qF "$dir/SKILL.md" README.md || fail "$f" "promoted skill not linked to its SKILL.md in README.md"
    grep -qF "./$name/SKILL.md" "skills/$bucket/README.md" 2>/dev/null || fail "$f" "promoted skill not linked in skills/$bucket/README.md"
  fi
  if [ "$bucket" = misc ]; then
    grep -qF "./$name/SKILL.md" skills/misc/README.md 2>/dev/null || fail "$f" "skill not linked in skills/misc/README.md"
  fi

  # Rule: invocation flags in both harnesses agree
  yaml="$dir/agents/openai.yaml"
  has_fm=0; [ "$(fm "$f" disable-model-invocation)" = true ] && has_fm=1
  has_yaml=0; [ -f "$yaml" ] && grep -Eq '^[[:space:]]*allow_implicit_invocation:[[:space:]]*false' "$yaml" && has_yaml=1
  if [ "$has_fm" = 1 ] || [ "$has_yaml" = 1 ]; then
    INVOKED[$name]=user
    [ "$has_fm" = 1 ] || fail "$f" "user-invoked skill lacks 'disable-model-invocation: true' (set in openai.yaml only)"
    [ "$has_yaml" = 1 ] || fail "$yaml" "user-invoked skill lacks 'allow_implicit_invocation: false' (set in SKILL.md only)"
  else
    INVOKED[$name]=model
  fi
done

# Text files to scan, minus licence text.
mapfile -t TEXT < <(all_files | grep -E '\.(md|sh|yaml|json)$' | grep -Ev '(^|/)LICENSE$')

for f in "${TEXT[@]}"; do
  # Rule: no em-dash anywhere in prose or code comments
  grep -qF "$EMDASH" "$f" && fail "$f" "contains an em-dash"

  # Rule: no skill-tool chain wording, in any file (self excluded: it holds the patterns)
  [ "$f" = scripts/check.sh ] && continue
  grep -Eq '[Cc]alls? the `?"?Skill"?`? tool|Skill tool (twice|with)|[Cc]all the Skill' "$f" \
    && fail "$f" "chain site names the Skill tool (write: Load the \`x\` skill.)"
  case "$f" in
    skills/*) grep -Eq 'Skill tool|`Skill`' "$f" && fail "$f" "names the Skill tool" ;;
  esac

  # Rule: no chain to a user-invoked skill
  while IFS= read -r span; do
    for n in $(grep -oE '`[a-z0-9-]+`' <<<"$span" | tr -d '`'); do
      [ "${INVOKED[$n]:-}" = user ] && fail "$f" "chains to user-invoked skill '$n' (\"$span\")"
    done
  done < <(grep -oEi '\bloads? (the )?`[a-z0-9-]+`( (and|,) `[a-z0-9-]+`)* skills?' "$f" || true)

  # Rule: dropped names are gone
  grep -Eq 'domain\.md' "$f" && fail "$f" "references dropped name 'domain.md'"

  # Rule: renamed skills keep no old name (grilling, grill-me, grill-with-docs,
  # implement, implement-spec) and no word built on grill (Grill log, grilled).
  # "implement" is an ordinary verb, so only its skill-name forms count:
  # backticked, after / or : (slash command, path), or as a frontmatter name.
  # README.md is exempt: its changes section maps old names to new ones.
  [ "$f" = README.md ] && continue
  old=$(grep -oEi '\bgrill[a-z-]*|\bimplement-spec\b|`implement`|[/:]implement\b|^name: implement\r?$' "$f" | sort -u | tr '\n' ' ')
  [ -n "$old" ] && fail "$f" "uses a renamed skill's old name: $old(now interview, interview-me, interview-with-docs, builder, builder-spec)"
done

# Rule: no reference to the origin repo or its author, in any file. Exempt: LICENSE
# (the MIT notice must stay), this script (holds the pattern) and, once one exists,
# the README credits line.
while IFS= read -r f; do
  case "$f" in LICENSE|README.md|scripts/check.sh) continue ;; esac
  grep -Eqi 'matt[- ]?pocock|aihero' "$f" && fail "$f" "names the origin repo or author (matt pocock / aihero)"
done < <(all_files)

if [ "$FAILS" -gt 0 ]; then echo "$FAILS check(s) failed"; exit 1; fi
echo "all checks passed"
