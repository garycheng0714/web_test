from typing import Self

from pydantic import BaseModel, model_validator

from web_test.planning.verify.resolution import ResolutionKind


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
                raise ValueError(
                    "ready verification input is missing its verdict data"
                )
        elif any(field is not None for field in fields):
            raise ValueError("early verification input has verdict data")
        return self
