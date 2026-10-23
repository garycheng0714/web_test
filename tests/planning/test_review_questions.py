from web_test.planning.review.questions import (
    STEP_QUALITY_DIMENSIONS,
    expected_checks,
    questions_for_subject,
)
from web_test.planning.review.verification import CheckDimension
from review_helpers import review_case, review_subject


def test_questions_for_subject_matches_expected_checks():
    subject = review_subject(
        [review_case(), review_case(index=2, scenario="Login")]
    )

    assert set(questions_for_subject(subject)) == {
        spec.question_id for spec in expected_checks(subject)
    }


def test_every_step_has_every_check():
    subject = review_subject(
        [review_case(), review_case(index=2, scenario="Login")]
    )
    specs = expected_checks(subject)

    step_specs = [
        spec for spec in specs if spec.dimension is not CheckDimension.AC_ALIGNMENT
    ]
    assert [spec.dimension for spec in step_specs].count(
        CheckDimension.STEP_REASONABLE
    ) == 4
    assert {spec.dimension for spec in step_specs} == set(STEP_QUALITY_DIMENSIONS)
