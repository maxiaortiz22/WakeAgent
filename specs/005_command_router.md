# 005 Command Router

## Purpose

Specify how transcripts become local actions, agent requests, or safe fallback responses.

## Requirements

- Route transcripts containing `status` to a local status response.
- Route transcripts containing `help` to local help text.
- Route transcripts containing `ask codex` or `codex` to agent execution.
- Route transcripts containing `ask claude` or `claude` to agent execution.
- Support a fixed target agent mode, selected outside the transcript, where any non-local transcript routes to the configured agent.
- Return a safe fallback for unrecognized commands.

## Non-goals

- No LLM-based intent detection.
- No command memory.
- No direct OS actions.

## Interfaces

- `CommandRouter(target_agent: "auto" | "codex" | "claude")`
- `CommandRouter.route(transcript: str) -> RouteResult`
- `RouteResult(kind, message, agent_cmd, prompt)`
- `RouteKind.LOCAL`, `RouteKind.AGENT`, `RouteKind.UNKNOWN`

## Acceptance criteria

- Router behavior is deterministic.
- Router never executes commands itself.
- Agent prompts are cleaned of obvious trigger phrases.
- Local commands such as `status`, `estado`, `help`, and `ayuda` remain local even when a fixed target agent is configured.
- In fixed target agent mode, the transcript does not need to include `codex` or `claude`.

## Test cases

- `status` returns local route.
- `help` returns local route.
- `ask codex to explain this repo` returns agent route for `codex`.
- Fixed `target_agent="claude"` with transcript `explain this repo` routes to `claude`.
- Fixed target agent mode keeps `estado` local.
- Unknown command returns safe fallback.

## Open questions

- Should routing be configurable with a YAML rules file?
- Should agent command aliases be user-defined?
