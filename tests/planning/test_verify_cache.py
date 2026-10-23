from pathlib import Path

import pytest

from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify.cache import CachedVerdict, VerdictCache
from web_test.planning.verify.run import run
from web_test.publishing.github import CheckPayload
from verify_helpers import (
    approval,
    empty_system_one,
    never_called,
    one_answer,
    passing_system_one,
    ready_input,
    sink,
)


def test_run_uses_a_cached_verdict(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CachedVerdict(
            status=VerificationStatus.PASS,
            payload=CheckPayload(
                head_sha="old",
                conclusion="success",
                title="Test Case verification: PASS",
                summary="cached summary",
                external_id=verification_input.cache_key,
            ),
        ).model_dump_json(),
        encoding="utf-8",
    )
    payloads, publish = sink()

    result = run(
        verification_input,
        head_sha="new",
        publish=publish,
        system_one=never_called,
        cache=cache,
    )
    payload = result.payload

    assert payload.summary == "cached summary"
    assert payload.head_sha == "new"
    assert payload.external_id == verification_input.cache_key
    assert result.saved is False
    assert result.status is VerificationStatus.PASS
    assert payloads == [payload]


def test_run_keeps_the_cached_status(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CachedVerdict(
            status=VerificationStatus.NEEDS_REVIEW,
            payload=CheckPayload(
                head_sha="old",
                conclusion="action_required",
                title="Test Case verification: NEEDS_REVIEW",
                summary="cached summary",
                external_id=verification_input.cache_key,
            ),
        ).model_dump_json(),
        encoding="utf-8",
    )
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="new",
        publish=publish,
        system_one=never_called,
        cache=cache,
    )

    assert result.status is VerificationStatus.NEEDS_REVIEW
    assert result.payload.conclusion == "action_required"


def test_run_saves_a_new_verdict(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=passing_system_one,
        cache=cache,
    )
    payload = result.payload

    assert result.saved is True
    assert cache.load(verification_input.cache_key) == CachedVerdict(
        status=VerificationStatus.PASS, payload=payload
    )
    assert payload.external_id == verification_input.cache_key


def test_run_does_not_cache_blocked(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=empty_system_one,
        cache=cache,
    )
    payload = result.payload

    assert payload.title == "Test Case verification: BLOCKED"
    assert result.saved is False
    assert not cache.path.exists()


def test_run_does_not_cache_an_adjudicated_success(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=one_answer(0.6),
        cache=cache,
        approval=approval(),
    )
    cached = cache.load(verification_input.cache_key)

    assert result.overridden is True
    assert result.payload.conclusion == "success"
    assert result.saved is True
    assert cached is not None
    assert cached.status is VerificationStatus.NEEDS_REVIEW
    assert "Human adjudication" not in cached.payload.summary


def test_run_ignores_a_cache_for_another_key(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CachedVerdict(
            status=VerificationStatus.FAIL,
            payload=CheckPayload(
                head_sha="old",
                conclusion="failure",
                title="Test Case verification: FAIL",
                summary="stale",
                external_id="another-key",
            ),
        ).model_dump_json(),
        encoding="utf-8",
    )
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=passing_system_one,
        cache=cache,
    )
    payload = result.payload

    assert payload.title == "Test Case verification: PASS"
    assert result.saved is True


def test_run_ignores_an_old_cache_format(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CheckPayload(
            head_sha="old",
            conclusion="success",
            title="Test Case verification: PASS",
            summary="old format",
            external_id=verification_input.cache_key,
        ).model_dump_json(),
        encoding="utf-8",
    )
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=passing_system_one,
        cache=cache,
    )

    assert result.payload.summary != "old format"
    assert result.saved is True


def test_run_ignores_a_corrupt_cache(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text("{not json", encoding="utf-8")
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=passing_system_one,
        cache=cache,
    )
    payload = result.payload

    assert payload.title == "Test Case verification: PASS"
    assert result.saved is True


def test_cached_verdict_rejects_blocked() -> None:
    with pytest.raises(ValueError, match="BLOCKED"):
        CachedVerdict(
            status=VerificationStatus.BLOCKED,
            payload=CheckPayload(
                head_sha="sha",
                conclusion="failure",
                title="Test Case verification: BLOCKED",
                summary="blocked",
                external_id="key",
            ),
        )
