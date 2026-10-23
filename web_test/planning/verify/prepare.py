from collections.abc import Iterable
from pathlib import Path

from web_test.planning.verify.input import PreparedVerification
from web_test.planning.verify.key import InvalidTestCase, cache_key
from web_test.planning.verify.resolution import ResolutionKind, resolve


def prepare(
    changed_paths: Iterable[str], *, workspace: Path
) -> PreparedVerification:
    """Resolve the changed paths to the verification input."""
    resolution = resolve(changed_paths, workspace=workspace)
    if resolution.kind is not ResolutionKind.READY:
        return PreparedVerification(
            kind=resolution.kind,
            files=list(resolution.files),
            detail=resolution.detail,
        )

    texts = resolution.texts
    if texts is None:
        raise ValueError("ready resolution is missing its texts")
    try:
        key = cache_key(texts.test_case_text, texts.prd_text)
    except InvalidTestCase as error:
        return PreparedVerification(kind=ResolutionKind.INVALID, detail=str(error))
    return PreparedVerification(
        kind=ResolutionKind.READY,
        test_case_text=texts.test_case_text,
        prd_text=texts.prd_text,
        cache_key=key,
    )
