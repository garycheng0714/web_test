from web_test.planning.cases_writer import CaseWriter, escape_cell
from web_test.planning.schema import Case
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub, PullRequest
from web_test.publishing.publish import BASE_BRANCH, BOT_EMAIL, BOT_NAME

TEST_CASE_DIR = "test-case"


def plan_pr_body(prd_name: str, entries: list[tuple[str, Case]]) -> str:
    lines = [
        f"Adds {len(entries)} test cases from `{prd_name}`.",
        "",
        "| Case | Scenario | Requirements |",
        "| --- | --- | --- |",
    ]
    lines += [
        f"| `{case_id}` | {escape_cell(case.module_feature)}: {escape_cell(case.test_scenario)} "
        f"| {escape_cell(', '.join(case.requirement_ids))} |"
        for case_id, case in entries
    ]
    return "\n".join(lines) + "\n"


class PlanPublisher:
    """Branches from origin/main, writes the case files, commits them, and opens the Gate PR."""

    def __init__(self, *, git: Git, pr: GitHub, writer: CaseWriter) -> None:
        self.git = git
        self.pr = pr
        self.writer = writer

    def publish(self, *, branch: str, message: str, prd_name: str, cases: list[Case]) -> list[str]:
        # Branch from a freshly fetched main before writing, so the ids reflect origin/main and the
        # new (untracked) files never collide with its checkout.
        self.git.set_identity(BOT_NAME, BOT_EMAIL)
        self.git.fetch()
        self.git.create_branch(branch, base=f"origin/{BASE_BRANCH}")

        names = self.writer.write(cases)
        files = [f"{TEST_CASE_DIR}/{name}" for name in names]
        entries = [(name.removesuffix(".md"), case) for name, case in zip(names, cases, strict=True)]

        self.git.add(files)
        self.git.commit(message)
        self.git.push(branch)
        self.pr.open_pull_request(
            PullRequest(
                base=BASE_BRANCH,
                head=branch,
                title=message,
                body=plan_pr_body(prd_name, entries),
            )
        )
        return files
