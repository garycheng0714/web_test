from pathlib import Path

from web_test.planning.verify.cache import VerdictCache
from web_test.planning.verify.run import run
from web_test.publishing.github import CheckPayload
from verify_helpers import (
    empty_system_one,
    never_called,
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
        CheckPayload(
            head_sha="old",
            conclusion="success",
            title="Test Case verification: PASS",
            summary="cached summary",
            external_id=verification_input.cache_key,
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
    assert payloads == [payload]

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
    assert cache.load(verification_input.cache_key) == payload
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

def test_run_ignores_a_cache_for_another_key(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CheckPayload(
            head_sha="old",
            conclusion="failure",
            title="Test Case verification: FAIL",
            summary="stale",
            external_id="another-key",
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
