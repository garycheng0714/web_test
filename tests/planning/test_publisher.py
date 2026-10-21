from unittest.mock import MagicMock, call

from web_test.planning.publisher import PlanPublisher, plan_pr_body
from web_test.planning.schema import Case

BRANCH = "plan/prd-register-20261014T120000Z"
MESSAGE = "Add test cases from prd-register.md"


def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [{"action": "Go", "expected_result": "Page shown"}],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        **overrides,
    }
    return Case.model_validate(data)


def test_plan_publisher_branches_writes_commits_and_opens_a_pr():
    git, pr = MagicMock(), MagicMock()
    writer = MagicMock()
    writer.write.return_value = "prd-register.md"
    cases = [_case(), _case(test_scenario="Login")]

    files = PlanPublisher(git=git, pr=pr, writer=writer).publish(
        branch=BRANCH, message=MESSAGE, prd_stem="prd-register", cases=cases, open_questions=["Q?"]
    )

    assert files == ["test-case/prd-register.md"]
    writer.write.assert_called_once_with("prd-register", cases, ["Q?"], content=None)
    assert git.method_calls == [
        call.set_identity(
            "web-test-qa-flow[bot]", "344404446+web-test-qa-flow[bot]@users.noreply.github.com"
        ),
        call.fetch(),
        call.create_branch(BRANCH, base="origin/main"),
        call.add(["test-case/prd-register.md"]),
        call.commit(MESSAGE),
        call.push(BRANCH),
    ]
    assert pr.open_pull_request.call_count == 1
    opened = pr.open_pull_request.call_args.args[0]
    assert (opened.base, opened.head, opened.title) == ("main", BRANCH, MESSAGE)
    assert "FR-ACC-01" in opened.body
    assert "Q?" in opened.body


def test_plan_pr_body_escapes_pipes():
    body = plan_pr_body("prd-register", [_case(module_feature="A | B")])

    assert "A \\| B" in body


def test_plan_pr_body_includes_the_review():
    body = plan_pr_body("prd-register", [_case()], review="## Jev review (advisory)")

    assert "\n---\n\n## Jev review (advisory)" in body


def test_plan_publisher_puts_the_review_in_the_pr_body():
    git, pr = MagicMock(), MagicMock()
    writer = MagicMock()
    writer.write.return_value = "prd-register.md"

    PlanPublisher(git=git, pr=pr, writer=writer).publish(
        branch=BRANCH, message=MESSAGE, prd_stem="prd-register", cases=[_case()], review="## Jev review"
    )

    opened = pr.open_pull_request.call_args.args[0]
    assert "## Jev review" in opened.body


def test_plan_publisher_writes_supplied_content_verbatim():
    git, pr = MagicMock(), MagicMock()
    writer = MagicMock()
    writer.write.return_value = "prd-register.md"

    PlanPublisher(git=git, pr=pr, writer=writer).publish(
        branch=BRANCH,
        message=MESSAGE,
        prd_stem="prd-register",
        cases=[_case()],
        content="# rendered\n",
    )

    assert writer.write.call_args.args[0] == "prd-register"
    assert writer.write.call_args.kwargs["content"] == "# rendered\n"
