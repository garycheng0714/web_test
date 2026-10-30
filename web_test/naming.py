import os
from datetime import UTC, datetime


def run_token(now: datetime | None = None) -> str:
    """A run-scoped token for branch names.

    In CI the GitHub run id (and attempt) makes every run's branch unique; without them a local
    run falls back to a UTC timestamp.
    """
    run_id = os.environ.get("WEB_TEST_RUN_ID")
    if run_id:
        attempt = os.environ.get("WEB_TEST_RUN_ATTEMPT")
        return f"{run_id}-{attempt}" if attempt else run_id
    moment = now or datetime.now(UTC)
    return f"{moment.astimezone(UTC):%Y%m%dT%H%M%SZ}"


def branch_for(kind: str, identifier: str, token: str) -> str:
    """The branch-name shape shared by both stages: `<kind>/<identifier>-<token>`."""
    return f"{kind}/{identifier}-{token}"
