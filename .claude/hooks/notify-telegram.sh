#!/usr/bin/env bash
# Post Claude Code lifecycle events to Telegram.
#
# The two ways to run Navox agents need two notifiers. The SDK
# (sdk/navox/notify.py) hooks into the orchestrator's step boundaries. The
# plugin has no orchestrator process — Claude Code runs the agents itself —
# so it hooks into Claude Code's lifecycle events instead. This is that half.
#
# Wire it up in .claude/settings.json:
#
#   "hooks": {
#     "Notification": [{"hooks": [{"type": "command",
#       "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-telegram.sh needs-you"}]}],
#     "Stop": [{"hooks": [{"type": "command",
#       "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-telegram.sh done"}]}]
#   }
#
# Set NAVOX_TELEGRAM_BOT_TOKEN and NAVOX_TELEGRAM_CHAT_ID in the environment
# or in a .env at the project root. See docs/notifications.md.
#
# Rule, same as the SDK notifier: never fail loudly. A dead webhook or a
# missing token must not interrupt a session. Always exits 0.

set -uo pipefail

payload=$(cat 2>/dev/null || echo '{}')

# Hooks inherit Claude Code's environment, which may not have .env loaded.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ -f "$root/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$root/.env" 2>/dev/null || true
  set +a
fi

[ -n "${NAVOX_TELEGRAM_BOT_TOKEN:-}" ] || exit 0
[ -n "${NAVOX_TELEGRAM_CHAT_ID:-}" ] || exit 0

event="${1:-event}"
project="$(basename "$root")"

# Pull a useful line out of the hook payload without requiring jq.
detail=$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit()
for k in ("message", "last_assistant_message", "stop_reason", "prompt"):
    v = d.get(k)
    if isinstance(v, str) and v.strip():
        print(v.strip()[:600]); break
' 2>/dev/null)

case "$event" in
  needs-you) text="🚨 Agents need you — ${project}" ;;
  done)      text="✅ Agent turn complete — ${project}" ;;
  *)         text="Navox agents — ${project}" ;;
esac
[ -n "$detail" ] && text="${text}"$'\n\n'"${detail}"

curl -s -m 10 -o /dev/null \
  "https://api.telegram.org/bot${NAVOX_TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${NAVOX_TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${text}" \
  -d "disable_notification=$([ "$event" = needs-you ] && echo false || echo true)" || true

exit 0
