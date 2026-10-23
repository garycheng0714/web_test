from web_test.planning.review.parser import parse_test_case
from review_helpers import make_case, render_case


def _document() -> str:
    case = make_case(
        requirement_ids=["FR-1"],
        preconditions=["The signup page is open"],
        steps=[
            {"action": "Go | home", "expected_result": "Page shown"},
            {"action": "Submit", "expected_result": "Done"},
        ],
        notes="Covers FR-1.",
    )
    return render_case(
        case,
        id="register",
        title="Register",
        open_questions=["What is the password policy?"],
    )


def test_parse_test_case_round_trips_cases_and_steps():
    subject = parse_test_case(_document(), "# PRD")

    assert subject.prd == "# PRD"
    assert len(subject.cases) == 1
    assert subject.cases[0].index == 1
    assert subject.cases[0].requirement_ids == ["FR-1"]
    assert subject.cases[0].module_feature == "Account"
    assert subject.cases[0].test_scenario == "Register"
    assert [step.action for step in subject.cases[0].steps] == ["Go | home", "Submit"]
    assert [step.expected_result for step in subject.cases[0].steps] == [
        "Page shown",
        "Done",
    ]


def test_editing_a_step_changes_the_parsed_subject():
    subject = parse_test_case(_document().replace("Submit", "Click Submit"), "# PRD")

    assert subject.cases[0].steps[1].action == "Click Submit"
