# 006 CLI Agent Executor

## Purpose

Specify safe subprocess execution for optional local CLI agents.

## Requirements

- Default to dry-run.
- Log and return the command that would be executed.
- In non-dry-run mode, execute only the configured binary with the prompt as an argument.
- Accept the routed agent command from the router when the CLI selects a fixed target agent.
- Never use `shell=True`.
- Use timeouts and capture stdout/stderr.
- Return structured execution results.

## Non-goals

- No interactive terminal control.
- No streaming CLI session management.
- No automatic installation of Codex, Claude, or other agents.

## Interfaces

- `AgentExecutor.run(prompt: str, agent_cmd: str | None = None) -> AgentResult`
- `AgentResult(command, dry_run, returncode, stdout, stderr, blocked, reason)`

## Acceptance criteria

- Dry-run never invokes subprocess.
- Non-dry-run uses a list of arguments.
- Blocked prompts return structured blocked results.
- Timeouts return structured errors.

## Test cases

- Dry-run returns `command=["codex", "..."]`.
- Fixed target agent routing can produce dry-run commands such as `command=["claude", "..."]`.
- Blocked destructive prompt is not executed.
- Allowed prompt passes policy.

## Open questions

- Should non-dry-run require an interactive approval prompt?
- Should stdout and stderr be capped in memory?
