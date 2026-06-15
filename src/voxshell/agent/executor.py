from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Sequence

from voxshell.agent.safety import SafetyPolicy


@dataclass(frozen=True)
class AgentResult:
    command: list[str]
    dry_run: bool
    returncode: int | None
    stdout: str
    stderr: str
    blocked: bool = False
    reason: str = ""


class AgentExecutor:
    def __init__(
        self,
        agent_cmd: str = "codex",
        dry_run: bool = True,
        timeout_seconds: float = 30.0,
        safety_policy: SafetyPolicy | None = None,
    ) -> None:
        self.agent_cmd = agent_cmd
        self.dry_run = dry_run
        self.timeout_seconds = timeout_seconds
        self.safety_policy = safety_policy or SafetyPolicy()

    def run(self, prompt: str, agent_cmd: str | None = None) -> AgentResult:
        binary = agent_cmd or self.agent_cmd
        command = self._build_command(binary, prompt)
        decision = self.safety_policy.check(prompt, dry_run=self.dry_run)
        if not decision.allowed:
            return AgentResult(
                command=command,
                dry_run=self.dry_run,
                returncode=None,
                stdout="",
                stderr="",
                blocked=True,
                reason=decision.reason,
            )

        if self.dry_run:
            return AgentResult(
                command=command,
                dry_run=True,
                returncode=0,
                stdout=f"DRY RUN: would execute {command!r}",
                stderr="",
                reason=decision.reason,
            )

        try:
            completed = subprocess.run(
                command,
                shell=False,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except FileNotFoundError as exc:
            return AgentResult(
                command=command,
                dry_run=False,
                returncode=None,
                stdout="",
                stderr=str(exc),
                blocked=False,
                reason="Agent executable was not found.",
            )
        except subprocess.TimeoutExpired as exc:
            return AgentResult(
                command=command,
                dry_run=False,
                returncode=None,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                blocked=False,
                reason=f"Agent execution timed out after {self.timeout_seconds} seconds.",
            )

        return AgentResult(
            command=command,
            dry_run=False,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            reason=decision.reason,
        )

    @staticmethod
    def _build_command(binary: str, prompt: str) -> list[str]:
        return [binary, prompt]
