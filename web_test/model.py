import os

DEFAULT_MODEL = "google:gemini-2.5-flash-lite"


def resolve_model() -> str:
    return os.environ.get("WEB_TEST_MODEL", DEFAULT_MODEL)
