from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl

from web_test.planning.schema import CaseType, Priority


def _front_matter(text: str) -> dict[str, object]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return yaml.safe_load("\n".join(lines[1:index])) or {}
    return {}


class CaseFile(BaseModel):
    """The machine-readable front-matter of a merged test-case artifact."""

    id: str
    base_url: HttpUrl
    requirement_ids: list[str] = []
    priority: Priority = Priority.MEDIUM
    test_type: CaseType = CaseType.FUNCTIONAL

    @classmethod
    def from_text(cls, text: str) -> "CaseFile":
        return cls.model_validate(_front_matter(text))

    @classmethod
    def from_path(cls, path: str | Path) -> tuple["CaseFile", str]:
        """Validate the artifact path, read it, and return the model with its raw text."""
        artifact = Path(path)
        if (
            artifact.parent.name != "test-case"
            or not artifact.name.startswith("test-case-")
            or artifact.suffix != ".md"
        ):
            raise ValueError(f"{artifact} is not a test-case artifact (expected test-case/<id>.md).")
        text = artifact.read_text(encoding="utf-8")
        return cls.from_text(text), text
