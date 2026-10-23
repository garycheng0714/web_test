from pydantic import BaseModel

from web_test.planning.verify.resolution import ResolutionKind


class PreparedVerification(BaseModel):
    """The verification input file `prepare` writes and `run` reads."""

    kind: ResolutionKind
    files: list[str] = []
    detail: str = ""
    test_case_text: str | None = None
    prd_text: str | None = None
    cache_key: str | None = None
