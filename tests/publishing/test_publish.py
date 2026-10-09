from datetime import date

from web_test.publishing.publish import allowed_paths, branch_name, publish


class RecordingGit:
    def __init__(self, paths: list[str] | None = None) -> None:
        self.paths = paths or []
        self.calls: list[tuple] = []

    def changed_paths(self) -> list[str]:
        return list(self.paths)

    def set_identity(self, name: str, email: str) -> None:
        self.calls.append(("set_identity", name, email))

    def create_branch(self, branch: str) -> None:
        self.calls.append(("create_branch", branch))

    def add(self, paths: list[str]) -> None:
        self.calls.append(("add", list(paths)))

    def commit(self, message: str) -> None:
        self.calls.append(("commit", message))

    def push(self, branch: str) -> None:
        self.calls.append(("push", branch))


class RecordingGitHub:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def open_pull_request(self, *, base: str, head: str, title: str, body: str) -> None:
        self.calls.append({"base": base, "head": head, "title": title, "body": body})


class StubSuite:
    def __init__(self, *, green: bool) -> None:
        self.green = green

    def is_green(self) -> bool:
        return self.green


def _publish(git: RecordingGit, pr: RecordingGitHub, suite: StubSuite) -> str | None:
    return publish(
        case_ids=["TC-1", "TC-2"],
        body="## Summary\n\nbody",
        git=git,
        pr=pr,
        suite=suite,
        today=date(2026, 10, 9),
    )


def test_red_suite_publishes_nothing() -> None:
    git = RecordingGit(paths=["tests/a.py"])
    pr = RecordingGitHub()

    assert _publish(git, pr, StubSuite(green=False)) is None
    assert git.calls == []
    assert pr.calls == []


def test_no_changes_publishes_nothing() -> None:
    git = RecordingGit(paths=[])
    pr = RecordingGitHub()

    assert _publish(git, pr, StubSuite(green=True)) is None
    assert git.calls == []
    assert pr.calls == []


def test_publishes_on_green() -> None:
    git = RecordingGit(paths=["tests/a.py", "README.md", "pages/p.py"])
    pr = RecordingGitHub()

    branch = _publish(git, pr, StubSuite(green=True))

    assert branch == "automation/automationexercise-2026-10-09"
    assert git.calls == [
        (
            "set_identity",
            "github-actions[bot]",
            "41898282+github-actions[bot]@users.noreply.github.com",
        ),
        ("create_branch", branch),
        ("add", ["tests/a.py", "pages/p.py"]),
        ("commit", "Add automated tests for TC-1, TC-2"),
        ("push", branch),
    ]
    assert pr.calls == [
        {
            "base": "main",
            "head": branch,
            "title": "Add automated tests for TC-1, TC-2",
            "body": "## Summary\n\nbody",
        }
    ]


def test_branch_name_uses_feature_and_date() -> None:
    assert branch_name("feature-x", date(2026, 1, 2)) == "automation/feature-x-2026-01-02"


def test_allowed_paths_keeps_only_guard_permitted() -> None:
    paths = ["tests/a.py", "web_test/x.py", "README.md", "pages/p.py", "tests/n.txt"]

    assert allowed_paths(paths) == ["tests/a.py", "pages/p.py"]
