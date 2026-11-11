#!/usr/bin/env bash
# Load test: start a headless Claude Code session with this plugin and confirm
# every skill in the manifest registers as a slash command. Exit 1 if any is missing.
# Makes one small model call, so it needs a logged-in claude CLI.
# Usage: scripts/load-test.sh [plugin-root]   (default: the folder above scripts/)
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${1:-$HERE/..}" && pwd)"
MANIFEST="$ROOT/.claude-plugin/plugin.json"

command -v claude >/dev/null 2>&1 || { echo "FAIL claude CLI not found"; exit 1; }

PLUGIN="$(grep -oE '"name"[[:space:]]*:[[:space:]]*"[^"]+"' "$MANIFEST" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
mapfile -t NAMES < <(grep -oE '"\./skills/[^"]+"' "$MANIFEST" | tr -d '"' | sed 's|.*/||' | sort)
[ -n "$PLUGIN" ] && [ "${#NAMES[@]}" -gt 0 ] || { echo "FAIL could not read plugin name or skills from $MANIFEST"; exit 1; }

# Run from a neutral folder with an absolute path: a relative --plugin-dir
# resolves against the caller's folder and silently loads nothing.
INIT="$(cd "${TMPDIR:-/tmp}" && claude --plugin-dir "$ROOT" -p "Reply with the single word ok" \
  --model haiku --output-format stream-json --verbose 2>&1 | grep -m1 '"subtype":"init"')"
[ -n "$INIT" ] || { echo "FAIL no init event from claude (not logged in?)"; exit 1; }

FAILS=0
for n in "${NAMES[@]}"; do
  grep -qF "\"$PLUGIN:$n\"" <<<"$INIT" || { echo "FAIL $PLUGIN:$n did not register"; FAILS=$((FAILS + 1)); }
done

if [ "$FAILS" -gt 0 ]; then echo "$FAILS skill(s) failed to load"; exit 1; fi
echo "all ${#NAMES[@]} skills registered as /$PLUGIN:<name>"
echo "to try them by hand: claude --plugin-dir \"$ROOT\""
