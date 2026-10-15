from web_test.planning.cases_writer import CaseWriter, escape_cell
from web_test.planning.schema import Case
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub, PullRequest
from web_test.publishing.publish import BASE_BRANCH, BOT_EMAIL, BOT_NAME

TEST_CASE_DIR = "test-case"


def plan_pr_body(prd_stem: str, cases: list[Case]) -> str:
    lines = [
        f"Adds {len(cases)} test cases from `{prd_stem}.md`.",
        "",
        "| Case | Scenario | Requirements |",
        "| --- | --- | --- |",
    ]
    lines += [
        f"| {index} | {escape_cell(case.module_feature)}: {escape_cell(case.test_scenario)} "
        f"| {escape_cell(', '.join(case.requirement_ids))} |"
        for index, case in enumerate(cases, start=1)
    ]
    return "\n".join(lines) + "\n"


class PlanPublisher:
    """Branches from origin/main, writes the PRD's case file, commits it, and opens the Gate PR."""

    def __init__(self, *, git: Git, pr: GitHub, writer: CaseWriter) -> None:
        self.git = git
        self.pr = pr
        self.writer = writer

    def publish(self, *, branch: str, message: str, prd_stem: str, cases: list[Case]) -> list[str]:
        # Branch from a freshly fetched main before writing, so the new (untracked) file never
        # collides with origin/main's checkout.
        self.git.set_identity(BOT_NAME, BOT_EMAIL)
        self.git.fetch()
        self.git.create_branch(branch, base=f"origin/{BASE_BRANCH}")

        name = self.writer.write(prd_stem, cases)
        files = [f"{TEST_CASE_DIR}/{name}"]

        self.git.add(files)
        self.git.commit(message)
        self.git.push(branch)
        self.pr.open_pull_request(
            PullRequest(
                base=BASE_BRANCH,
                head=branch,
                title=message,
                body=plan_pr_body(prd_stem, cases),
            )
        )
        return files
