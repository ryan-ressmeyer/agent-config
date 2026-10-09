#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SEND="$ROOT/skills/infrastructure/email-ryan/scripts/send-email.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

# A stand-in curl: records the auth header (stdin) and the JSON payload (the
# `-d @file` argument), then replies with $FAKE_BODY and status $FAKE_STATUS.
mkdir -p "$TMP/bin"
cat >"$TMP/bin/curl" <<'EOF'
#!/usr/bin/env bash
cat >"$FAKE_DIR/header"
printf '%s\n' "$@" >"$FAKE_DIR/args"
while [ $# -gt 0 ]; do
  [ "$1" = "-d" ] && cp "${2#@}" "$FAKE_DIR/payload"
  shift
done
printf '%s\n%s' "$FAKE_BODY" "$FAKE_STATUS"
EOF
chmod +x "$TMP/bin/curl"

# Run the script in a fresh HOME with the stand-in curl. $KEY becomes
# RESEND_API_KEY (unset when empty) and $ZSHRC_LOCAL seeds ~/.zshrc.local.
# Stdout and stderr land in $FAKE_DIR/out and $FAKE_DIR/err.
OK_BODY='{"id":"msg-123"}'
case_n=0
run() {
  case_n=$((case_n + 1))
  export FAKE_DIR="$TMP/case-$case_n"
  mkdir -p "$FAKE_DIR/home"
  [ -z "${ZSHRC_LOCAL:-}" ] || printf '%s\n' "$ZSHRC_LOCAL" >"$FAKE_DIR/home/.zshrc.local"
  HOME="$FAKE_DIR/home" XDG_STATE_HOME="" PATH="$TMP/bin:$PATH" \
    FAKE_BODY="${FAKE_BODY:-$OK_BODY}" FAKE_STATUS="${FAKE_STATUS:-200}" \
    env -u RESEND_API_KEY ${KEY:+"RESEND_API_KEY=$KEY"} \
    "$SEND" "$@" >"$FAKE_DIR/out" 2>"$FAKE_DIR/err"
}

# A normal send posts a JSON payload to Resend with the fixed recipient, a
# host-prefixed subject, and the stdin body intact, then prints the message id.
body=$'line one\nhe said "hi" \\ done'
printf '%s' "$body" >"$TMP/stdin.txt"
KEY=test-key run --subject "Fit finished" <"$TMP/stdin.txt" ||
  fail "normal send exited nonzero: $(cat "$FAKE_DIR/err")"
[[ "$(cat "$FAKE_DIR/out")" == "msg-123" ]] ||
  fail "did not print the message id: $(cat "$FAKE_DIR/out")"
[[ "$(jq -r '.to[0]' "$FAKE_DIR/payload")" == "ryan.ressmeyer@gmail.com" ]] ||
  fail "wrong recipient: $(cat "$FAKE_DIR/payload")"
[[ "$(jq -r '.subject' "$FAKE_DIR/payload")" == "[$(hostname -s)] Fit finished" ]] ||
  fail "subject not host-prefixed: $(cat "$FAKE_DIR/payload")"
[[ "$(jq -r '.text' "$FAKE_DIR/payload")" == "$body" ]] ||
  fail "body not preserved: $(cat "$FAKE_DIR/payload")"
[[ "$(cat "$FAKE_DIR/header")" == "Authorization: Bearer test-key" ]] ||
  fail "auth header wrong"
grep -q 'test-key' "$FAKE_DIR/args" &&
  fail "API key leaked into curl's argument list"
grep -qx 'https://api.resend.com/emails' "$FAKE_DIR/args" ||
  fail "did not post to the Resend emails endpoint"

# --body and --body-file supply the body without stdin.
KEY=test-key run --subject s --body "inline text" </dev/null ||
  fail "--body send failed"
[[ "$(jq -r '.text' "$FAKE_DIR/payload")" == "inline text" ]] ||
  fail "--body not used"
printf 'from a file\n' >"$TMP/body.txt"
KEY=test-key run --subject s --body-file "$TMP/body.txt" </dev/null ||
  fail "--body-file send failed"
[[ "$(jq -r '.text' "$FAKE_DIR/payload")" == "from a file" ]] ||
  fail "--body-file not used"

# With the variable unset, the key is read from ~/.zshrc.local.
ZSHRC_LOCAL='export RESEND_API_KEY=file-key' run --subject s --body b ||
  fail "did not fall back to ~/.zshrc.local: $(cat "$FAKE_DIR/err")"
[[ "$(cat "$FAKE_DIR/header")" == "Authorization: Bearer file-key" ]] ||
  fail "key from ~/.zshrc.local not used"

# No key anywhere: fail before calling the API, and say how to get the key.
if run --subject s --body b; then
  fail "send without a key succeeded"
fi
grep -q 'secrets-pull' "$FAKE_DIR/err" ||
  fail "missing-key error does not mention secrets-pull: $(cat "$FAKE_DIR/err")"
[ ! -e "$FAKE_DIR/args" ] ||
  fail "called the API without a key"

# A missing subject is rejected before calling the API.
if KEY=test-key run --body b; then
  fail "send without a subject succeeded"
fi
grep -q -- '--subject' "$FAKE_DIR/err" ||
  fail "missing-subject error does not name the flag"
[ ! -e "$FAKE_DIR/args" ] ||
  fail "called the API without a subject"

# An API rejection exits nonzero and surfaces Resend's message.
if FAKE_STATUS=403 FAKE_BODY='{"message":"You can only send testing emails to your own email address"}' \
  KEY=test-key run --subject s --body b; then
  fail "API rejection exited zero"
fi
grep -q '403' "$FAKE_DIR/err" && grep -q 'only send testing emails' "$FAKE_DIR/err" ||
  fail "API error not surfaced: $(cat "$FAKE_DIR/err")"

# The hourly cap refuses further sends from the same machine, without calling
# the API, once three have gone out within the hour.
export FAKE_DIR="$TMP/cap"
mkdir -p "$FAKE_DIR/home"
capped() {
  HOME="$FAKE_DIR/home" XDG_STATE_HOME="" PATH="$TMP/bin:$PATH" FAKE_BODY='{"id":"x"}' FAKE_STATUS=200 \
    RESEND_API_KEY=test-key "$SEND" --subject s --body b >"$FAKE_DIR/out" 2>"$FAKE_DIR/err"
}
for i in 1 2 3; do
  capped || fail "send $i within the cap failed: $(cat "$FAKE_DIR/err")"
done
rm -f "$FAKE_DIR/args"
if capped; then
  fail "fourth send within the hour was allowed"
fi
grep -qi 'limit' "$FAKE_DIR/err" ||
  fail "cap refusal does not explain itself: $(cat "$FAKE_DIR/err")"
[ ! -e "$FAKE_DIR/args" ] ||
  fail "called the API past the cap"

# Sends older than an hour no longer count against the cap.
log="$FAKE_DIR/home/.local/state/email-ryan/sent.log"
old=$(($(date +%s) - 3700))
printf '%s\n' "$old" "$old" "$old" >"$log"
capped || fail "send after the window expired was refused: $(cat "$FAKE_DIR/err")"

echo "email-ryan-send: all checks passed"
