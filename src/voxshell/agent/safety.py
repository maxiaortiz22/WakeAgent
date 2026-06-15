from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str


class SafetyPolicy:
    destructive_patterns = (
        r"\brm\s+-rf\b",
        r"\bdel\s+/s\b",
        r"\bformat\b",
        r"\bshutdown\b",
        r"\breboot\b",
        r"\bmkfs\b",
    )
    secret_patterns = (
        r"(^|\s)\.env(\s|$)",
        r"\bid_rsa\b",
        r"\bid_ed25519\b",
        r"\.ssh[/\\]",
        r"aws[/\\]credentials",
        r"gcloud[/\\]",
        r"kube[/\\]config",
    )

    def check(self, prompt: str, dry_run: bool = True) -> SafetyDecision:
        lowered = prompt.lower()
        for pattern in self.destructive_patterns:
            if re.search(pattern, lowered):
                return SafetyDecision(False, f"Blocked destructive pattern: {pattern}")
        for pattern in self.secret_patterns:
            if re.search(pattern, lowered):
                return SafetyDecision(False, f"Blocked obvious secret access pattern: {pattern}")
        if dry_run:
            return SafetyDecision(True, "Allowed in dry-run mode.")
        return SafetyDecision(True, "Allowed for explicit non-dry-run execution.")
