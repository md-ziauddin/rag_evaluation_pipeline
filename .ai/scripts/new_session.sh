#!/usr/bin/env bash
# Creates a new .ai/sessions/YYYY-MM-DD-HHMM-<agent>.md from the template and
# prints the bootstrap reminder. Run this at the START of a session.
#
# Usage: .ai/scripts/new_session.sh <agent-name>
#   e.g. .ai/scripts/new_session.sh claude-code
#        .ai/scripts/new_session.sh gemini-cli
set -euo pipefail

AGENT="${1:-}"
if [[ -z "$AGENT" ]]; then
  echo "Usage: $0 <agent-name>   (e.g. claude-code, gemini-cli, codex, cursor)" >&2
  exit 1
fi

# Slugify: lowercase, spaces/underscores -> hyphens
AGENT_SLUG="$(echo "$AGENT" | tr '[:upper:]' '[:lower:]' | tr ' _' '-')"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(dirname "$SCRIPT_DIR")"
SESSIONS_DIR="$AI_DIR/sessions"
TEMPLATE="$AI_DIR/templates/session.md"

TIMESTAMP="$(date +%Y-%m-%d-%H%M)"
DATE_HUMAN="$(date +%Y-%m-%d)"
TIME_HUMAN="$(date +%H:%M)"
SESSION_FILE="$SESSIONS_DIR/${TIMESTAMP}-${AGENT_SLUG}.md"

if [[ -e "$SESSION_FILE" ]]; then
  echo "A session file already exists for this minute: $SESSION_FILE" >&2
  exit 1
fi

sed \
  -e "s/YYYY-MM-DD HH:MM/${DATE_HUMAN} ${TIME_HUMAN}/" \
  -e "s/<agent name>/${AGENT}/" \
  "$TEMPLATE" > "$SESSION_FILE"

echo "Created: ${SESSION_FILE#"$(cd "$AI_DIR/.." && pwd)/"}"
echo
echo "Before writing any code, run through .ai/BOOTSTRAP.md:"
echo "  1. Read PROJECT.md, STATE.md, TASKS.md, ARCHITECTURE.md"
echo "  2. Check FILE_INDEX.md before creating any file"
echo "  3. Summarize your understanding and plan before coding"
echo
echo "At the end of the session, run: .ai/scripts/end_session.sh"
