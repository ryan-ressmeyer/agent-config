---
name: email-ryan
description: Use when Ryan asks to be emailed or notified by email, or when starting a run expected to take more than two hours.
---

# Email Ryan

Sends Ryan a plain-text email through Resend. The recipient is fixed; this cannot email anyone else, attach files, or send HTML.

## 1. Decide whether an email is warranted

Send an email only in these two cases:

- **Requested:** Ryan asked for one in this session.
- **Long run:** the work is expected to take more than two hours of wall-clock time. No request is needed, but tell Ryan before starting the work that an email will arrive when it finishes, so he knows to expect it.

Everything else is reported in the session, not by email.

**Complete when:** the case is identified as requested or long run, and for a long run the session already contains the sentence telling Ryan to expect the email.

## 2. Send one email per run

Send a single email when the run ends: on completion, or when it fails or blocks in a way that needs Ryan. Collect everything worth saying into that one message. Progress updates, per-step results, and follow-up corrections stay in the session.

Run the bundled script, resolving the path relative to this skill's directory:

```bash
scripts/send-email.sh --subject "Spike sorting finished: 12/12 sessions" <<'EOF'
All 12 sessions sorted in 4h 52m. Session 7 has 3 units flagged for review.

Outputs: /data/sorted/2026-10-08/
Log: /data/sorted/2026-10-08/run.log
EOF
```

The body may instead come from `--body TEXT` or `--body-file PATH`. The script prefixes the subject with `[hostname]`, so do not repeat the machine name.

Write the subject as the outcome, and open the body with the result, then where the outputs are and anything Ryan must do. Leave out secrets and credentials.

**Complete when:** the script exited 0 and printed a Resend message id, and that id is reported in the session.

## If the script fails

The script enforces a limit of three emails per hour per machine. Do not work around any failure by calling Resend another way.

| Exit | Meaning | Action |
|---|---|---|
| 1 | Bad arguments, empty body, or `RESEND_API_KEY` missing | Fix the arguments and rerun. For a missing key, tell Ryan in the session to run `secrets-pull && reload`. |
| 2 | Resend rejected the email or was unreachable | Rerun once. If it fails again, report the error in the session. |
| 3 | Hourly limit reached | Do not retry. Report the content in the session instead. |
