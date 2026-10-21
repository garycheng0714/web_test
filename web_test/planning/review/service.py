from collections.abc import Callable

from web_test.planning.review.jev import ReviewRequest, SystemOne, typesafe_system_one
from web_test.planning.review.questions import question_set_version, questions_for_subject
from web_test.planning.review.record import DEFAULT_BANDS, build_blocked_record, build_record
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import Bands, VerificationRecord
from web_test.planning.schema import DesignOutput

# A seam over the whole review: takes the PRD, design, and rendered artifact.
Reviewer = Callable[[str, DesignOutput, str], VerificationRecord]


def _subject_from_design(prd_text: str, design: DesignOutput) -> ReviewSubject:
    return ReviewSubject(
        prd=prd_text,
        cases=[
            ReviewCase(
                index=case_index,
                requirement_ids=case.requirement_ids,
                module_feature=case.module_feature,
                test_scenario=case.test_scenario,
                preconditions=case.preconditions,
                steps=[
                    ReviewStep(
                        index=step_index,
                        action=step.action,
                        expected_result=step.expected_result,
                    )
                    for step_index, step in enumerate(case.steps, start=1)
                ],
            )
            for case_index, case in enumerate(design.cases, start=1)
        ],
    )


def run_review_on(
    subject: ReviewSubject,
    test_case_text: str = "",
    *,
    system_one: SystemOne = typesafe_system_one,
    bands: Bands = DEFAULT_BANDS,
) -> VerificationRecord:
    """Judge an existing review subject and always return a record, blocked or not."""
    try:
        questions = questions_for_subject(subject)
        request = ReviewRequest(subject=subject, questions=questions)
        version = question_set_version(questions)
    except Exception as error:  # noqa: BLE001 - a malformed subject must not fail the plan
        return build_blocked_record(
            subject,
            test_case_text=test_case_text,
            question_set_version="",
            bands=bands,
            reason=f"request build failed: {error}",
        )

    return _review_request(request, test_case_text, version, system_one=system_one, bands=bands)


def _review_request(
    request: ReviewRequest,
    test_case_text: str,
    version: str,
    *,
    system_one: SystemOne,
    bands: Bands,
) -> VerificationRecord:
    try:
        answers = system_one(request)
    except Exception as error:  # noqa: BLE001 - the record must carry the blocked reason
        return build_blocked_record(
            request.subject,
            test_case_text=test_case_text,
            question_set_version=version,
            bands=bands,
            reason=f"Jev call failed: {error}",
        )

    if not answers:
        return build_blocked_record(
            request.subject,
            test_case_text=test_case_text,
            question_set_version=version,
            bands=bands,
            reason="Jev returned no answers",
        )

    return build_record(
        request.subject,
        answers,
        test_case_text=test_case_text,
        question_set_version=version,
        bands=bands,
    )


def run_review(
    prd_text: str,
    design: DesignOutput,
    test_case_text: str = "",
    *,
    system_one: SystemOne = typesafe_system_one,
    bands: Bands = DEFAULT_BANDS,
) -> VerificationRecord:
    """Ask Jev about a design and return the verification record, or a blocked record when it
    cannot answer."""
    return run_review_on(
        _subject_from_design(prd_text, design),
        test_case_text,
        system_one=system_one,
        bands=bands,
    )
