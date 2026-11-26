#!/usr/bin/env bash
# Drive one turn of a headless Claude Code session with this plugin loaded, for
# Verify steps that need a real skill run. Streams text and tool calls as they
# happen, then prints the session id to pass to the next turn.
# Usage: scripts/drive-skill.sh <workdir> <prompt> [session-id]
#   workdir     scratch folder outside this repo, as /c/... or C:/...; made if missing
#   session-id  resume that session (the last line of the previous turn)
# Env: MODEL (default sonnet), TOOLS (space-separated allowed tools).
# Each turn's raw stream-json is kept in <workdir>/.drive/ for later checks.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || echo "$ROOT")"
REPO="$(cd "$REPO" && pwd)"

[ $# -ge 2 ] || { sed -n '5,8p' "$0"; exit 2; }
command -v claude >/dev/null 2>&1 || { echo "FAIL claude CLI not found"; exit 1; }
# First interpreter that runs: on Windows, python3 can be a Store stub that only prints a hint.
PY=""; for c in python3 python; do "$c" -c "" >/dev/null 2>&1 && { PY="$c"; break; }; done
[ -n "$PY" ] || { echo "FAIL python not found"; exit 1; }

# Check the folder before creating it, so a mistyped path never lands in the repo.
# On Windows, turn C:/... or C:\... into /c/... first, or it reads as relative.
WARG="$1"; command -v cygpath >/dev/null 2>&1 && WARG="$(cygpath -u "$1")"
case "$WARG" in /*) WORK="$WARG" ;; *) WORK="$(pwd)/$WARG" ;; esac
case "$WORK/" in "$REPO"/*) echo "FAIL workdir must be outside $REPO"; exit 1 ;; esac
mkdir -p "$WORK" || exit 1
WORK="$(cd "$WORK" && pwd)"; PROMPT="$2"; SID="${3:-}"
[ -d "$WORK/.git" ] || git -C "$WORK" init -q

ARGS=(--plugin-dir "$ROOT" --add-dir "$ROOT" -p "$PROMPT"
  --model "${MODEL:-sonnet}" --permission-mode acceptEdits
  --allowedTools "${TOOLS:-Read Write Edit Glob Grep WebSearch WebFetch Agent Bash}"
  --output-format stream-json --verbose)
[ -n "$SID" ] && ARGS+=(--resume "$SID")

mkdir -p "$WORK/.drive"
LOG="$WORK/.drive/turn-$(date +%Y%m%d-%H%M%S).jsonl"

(cd "$WORK" && claude "${ARGS[@]}" </dev/null) | tee "$LOG" | "$PY" -u -c '
import json, sys
code = 0
for line in sys.stdin:
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
        for c in ev.get("message", {}).get("content", []):
            if c.get("type") == "text":
                print(c["text"], flush=True)
            elif c.get("type") == "tool_use":
                arg = json.dumps(c.get("input", {}))[:160]
                print("> " + c.get("name", "?") + " " + arg, flush=True)
    elif ev.get("type") == "result":
        for d in ev.get("permission_denials") or []:
            print("DENIED " + d.get("tool_name", "?"), flush=True)
        if ev.get("is_error"):
            print("FAIL turn ended in error: " + str(ev.get("subtype")), flush=True)
            code = 1
        print("session: " + str(ev.get("session_id")), flush=True)
sys.exit(code)
'
STATUS=$?
echo "log: $LOG"
exit $STATUS
