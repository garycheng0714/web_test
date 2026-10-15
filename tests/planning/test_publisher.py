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
        branch=BRANCH, message=MESSAGE, prd_stem="prd-register", cases=cases
    )

    assert files == ["test-case/prd-register.md"]
    writer.write.assert_called_once_with("prd-register", cases)
    assert git.method_calls == [
        call.set_identity(
            "github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com"
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


def test_plan_pr_body_escapes_pipes():
    body = plan_pr_body("prd-register", [_case(module_feature="A | B")])

    assert "A \\| B" in body
