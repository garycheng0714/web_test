from typing import Self

from pydantic import BaseModel, field_validator, model_validator

from web_test.planning.verify.resolution import ResolutionKind

_REASON_LIMIT = 4000


class PreparedVerification(BaseModel):
    """The verification input file `prepare` writes and `run` reads."""

    kind: ResolutionKind
    files: list[str] = []
    detail: str = ""
    test_case_text: str | None = None
    prd_text: str | None = None
    cache_key: str | None = None

    @model_validator(mode="after")
    def _check_ready_fields(self) -> Self:
        fields = (self.test_case_text, self.prd_text, self.cache_key)
        if self.kind is ResolutionKind.READY:
            if any(field is None for field in fields):
                raise ValueError("ready verification input is missing its verdict data")
        elif any(field is not None for field in fields):
            raise ValueError("early verification input has verdict data")
        return self


class Approval(BaseModel):
    """An approving review that may override a non-final verdict."""

    state: str
    reason: str
    head_sha: str

    @field_validator("reason")
    @classmethod
    def _clean_reason(cls, value: str) -> str:
        text = value.strip()
        return text if len(text) <= _REASON_LIMIT else f"{text[: _REASON_LIMIT - 1]}…"

    @field_validator("head_sha")
    @classmethod
    def _clean_head_sha(cls, value: str) -> str:
        return value.strip()

    def applies_to(self, head_sha: str) -> bool:
        return (
            self.state == "approved"
            and bool(self.reason)
            and bool(self.head_sha)
            and self.head_sha == head_sha
        )
