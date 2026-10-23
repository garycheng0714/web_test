from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pydantic import BaseModel, model_validator

from web_test.planning.review.verification import VerificationStatus
from web_test.publishing.github import CheckPayload


class CachedVerdict(BaseModel):
    """The original verdict stored for a cache key."""

    status: VerificationStatus
    payload: CheckPayload

    @model_validator(mode="after")
    def _reject_blocked(self) -> Self:
        if self.status is VerificationStatus.BLOCKED:
            raise ValueError("BLOCKED verdicts are not cached")
        return self


@dataclass(frozen=True)
class VerdictCache:
    """The verdict file restored from the workflow cache."""

    directory: Path

    @property
    def path(self) -> Path:
        return self.directory / "verdict.json"

    # shortcut: a corrupt or old-format cache entry is a miss, but the Actions cache key is
    # immutable; delete the entry if it keeps reappearing.
    def load(self, key: str) -> CachedVerdict | None:
        try:
            cached = CachedVerdict.model_validate_json(
                self.path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            return None
        return cached if cached.payload.external_id == key else None

    def save(self, status: VerificationStatus, payload: CheckPayload) -> None:
        cached = CachedVerdict(status=status, payload=payload)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path.write_text(cached.model_dump_json() + "\n", encoding="utf-8")
