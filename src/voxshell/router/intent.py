from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RouteKind(str, Enum):
    LOCAL = "local"
    AGENT = "agent"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RouteResult:
    kind: RouteKind
    message: str
    agent_cmd: str | None = None
    prompt: str | None = None
