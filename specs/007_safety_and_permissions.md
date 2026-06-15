# 007 Safety And Permissions

## Purpose

Specify basic safety policy for the MVP CLI-agent bridge.

## Requirements

- Block prompts with destructive patterns such as `rm -rf`, `del /s`, `format`, `shutdown`, `reboot`, and `mkfs`.
- Block obvious secret-file access such as `.env`, SSH keys, and common cloud credential paths.
- Require explicit non-dry-run configuration before execution.
- Keep policy tests independent from the executor.

## Non-goals

- No complete sandbox.
- No formal security guarantee.
- No OS-level permission isolation.
- No prompt injection defense beyond simple static checks.

## Interfaces

- `SafetyPolicy.check(prompt: str, dry_run: bool) -> SafetyDecision`
- `SafetyDecision(allowed, reason)`

## Acceptance criteria

- Destructive prompts are blocked.
- Secret-file prompts are blocked.
- Benign prompts are allowed.
- Dry-run remains the default execution mode.

## Test cases

- `rm -rf /` is blocked.
- `open .env` is blocked.
- `explain this repo` is allowed.
- Executor refuses blocked prompts before subprocess execution.

## Open questions

- Which patterns create too many false positives?
- Should policy be user-configurable?
