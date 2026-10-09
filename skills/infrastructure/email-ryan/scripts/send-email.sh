#!/usr/bin/env bash
# Email Ryan through the Resend API. Requires curl and jq.
#
# Usage: send-email.sh --subject SUBJECT [--body TEXT | --body-file PATH | <stdin>]
#
# Prints the Resend message id on success. Exit status: 0 sent, 1 usage or
# missing key, 2 Resend rejected or was unreachable, 3 hourly limit reached.
set -euo pipefail

# The recipient is fixed: this script exists to reach Ryan, not to send mail.
TO="ryan.ressmeyer@gmail.com"
# Resend's shared sender; it delivers only to the account owner's address.
FROM="agent <onboarding@resend.dev>"
API_URL="https://api.resend.com/emails"
# Per-machine cap, so a looping agent cannot flood the inbox.
MAX_PER_HOUR=3
WINDOW_SECONDS=3600

die() {
  printf 'send-email: %s\n' "$2" >&2
  exit "$1"
}

SUBJECT=""
BODY=""
BODY_FILE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --subject) SUBJECT="${2-}"; shift 2 || true ;;
    --body) BODY="${2-}"; shift 2 || true ;;
    --body-file) BODY_FILE="${2-}"; shift 2 || true ;;
    *) die 1 "unknown argument: $1 (usage: --subject SUBJECT [--body TEXT | --body-file PATH | <stdin>])" ;;
  esac
done
[ -n "$SUBJECT" ] || die 1 "--subject is required"

# Resolve body: --body > --body-file > stdin.
if [ -n "$BODY" ]; then
  :
elif [ -n "$BODY_FILE" ]; then
  [ -r "$BODY_FILE" ] || die 1 "cannot read --body-file: $BODY_FILE"
  BODY="$(cat "$BODY_FILE")"
elif [ ! -t 0 ]; then
  BODY="$(cat)"
fi
[ -n "$BODY" ] || die 1 "empty body: pass --body, --body-file, or text on stdin"

# Sessions started before the key was distributed, and non-interactive shells,
# do not have it in the environment; read it from the shell-secrets file.
KEY="${RESEND_API_KEY:-}"
if [ -z "$KEY" ] && [ -r "$HOME/.zshrc.local" ]; then
  KEY="$(sed -n "s/^export RESEND_API_KEY=[\"']\{0,1\}\([^\"']*\)[\"']\{0,1\}\$/\1/p" "$HOME/.zshrc.local" | tail -n 1)"
fi
[ -n "$KEY" ] || die 1 "RESEND_API_KEY is not set and not in ~/.zshrc.local; ask Ryan to run 'secrets-pull && reload' on this machine"

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/email-ryan"
SENT_LOG="$STATE_DIR/sent.log"
mkdir -p "$STATE_DIR"
now="$(date +%s)"
recent="$(awk -v cutoff="$((now - WINDOW_SECONDS))" '$1 > cutoff' "$SENT_LOG" 2>/dev/null || true)"
count="$(printf '%s' "$recent" | grep -c . || true)"
[ "$count" -lt "$MAX_PER_HOUR" ] ||
  die 3 "hourly limit reached ($MAX_PER_HOUR emails per hour from this machine); not sent. Do not retry: tell Ryan in the session instead"

payload="$(mktemp)"
trap 'rm -f "$payload"' EXIT
jq -n --arg from "$FROM" --arg to "$TO" --arg subject "[$(hostname -s)] $SUBJECT" --arg text "$BODY" \
  '{from: $from, to: [$to], subject: $subject, text: $text}' >"$payload"

# The key goes in on stdin so it never appears in the process list.
response="$(printf 'Authorization: Bearer %s\n' "$KEY" |
  curl -sS --max-time 30 -w '\n%{http_code}' -X POST "$API_URL" \
    -H @- -H 'Content-Type: application/json' -d "@$payload")" ||
  die 2 "could not reach Resend; not sent"

status="${response##*$'\n'}"
reply="${response%$'\n'*}"
case "$status" in
  2??) ;;
  *) die 2 "Resend rejected the email (HTTP $status): $(jq -r '.message // .' <<<"$reply" 2>/dev/null || printf '%s' "$reply")" ;;
esac

printf '%s\n%s\n' "$recent" "$now" | grep . >"$SENT_LOG"
jq -r '.id' <<<"$reply"
