from dataclasses import dataclass
from pathlib import Path

from web_test.publishing.github import CheckPayload


@dataclass(frozen=True)
class VerdictCache:
    """The verdict file restored from the workflow cache."""

    directory: Path

    @property
    def path(self) -> Path:
        return self.directory / "verdict.json"

    # shortcut: a corrupt cache entry is a miss, but the Actions cache key is immutable;
    # delete the entry if it keeps reappearing.
    def load(self, key: str) -> CheckPayload | None:
        try:
            payload = CheckPayload.model_validate_json(
                self.path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            return None
        return payload if payload.external_id == key else None

    def save(self, payload: CheckPayload) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path.write_text(payload.model_dump_json() + "\n", encoding="utf-8")
