from typesafe_sdk import Noul, NoulCriteria

QUESTIONS = {
    "steps_in_order": Noul(
        instructions=(
            "The subject's `case` is a test case, `test` is a generated Playwright Python test, and "
            "`support` is the page-object/component code the test uses. Does the test execute the "
            "case's actions in the same order, with no action replaced by a different action? Treat "
            "a page-object method call as the action its body performs."
        ),
        criteria=NoulCriteria(
            true=(
                "Every case action appears in order, directly or through a page-object method that "
                "performs it; no action is replaced by a different one."
            ),
            false=(
                "An action is missing, reordered, or replaced by a different action (for example, "
                "clicking Login instead of Signup)."
            ),
        ),
    ),
    "expected_results_asserted": Noul(
        instructions=(
            "Does the test assert every expected result in the case? An assertion on a page-unique "
            "heading, a visible field, or an entered value counts; the test does not need to assert "
            "the URL if it asserts the page-unique heading. A URL-only assertion does not cover a "
            "visible block, field, value, or page heading."
        ),
        criteria=NoulCriteria(
            true=(
                "Every expected result has at least one assertion that would fail if that result "
                "were absent; page-unique headings count."
            ),
            false=(
                "At least one expected result is missing or covered only by a weaker assertion (for "
                "example, only the URL)."
            ),
        ),
    ),
    "no_invented_behavior": Noul(
        instructions=(
            "Does the test avoid a different user flow or unrelated assertions? A weaker assertion "
            "is not invented behavior; setup/cleanup is allowed. Flag only actions or assertions the "
            "case does not describe (for example, logging in instead of signing up)."
        ),
        criteria=NoulCriteria(
            true=(
                "The test follows the case's flow plus necessary setup/cleanup; no different flow "
                "or unrelated assertion."
            ),
            false="The test follows a different flow or asserts something unrelated to the case.",
        ),
    ),
    "preconditions_setup": Noul(
        instructions=(
            "Does the test perform the setup actions the case needs: is it on /login and does it use "
            "a fresh test email? It does not need to prove the email is unregistered; a timestamped "
            "email counts as fresh. The guest state is implied by using the login page before "
            "signing in."
        ),
        criteria=NoulCriteria(
            true=(
                "The test navigates to /login and uses a fresh/timestamped email; setup is visible "
                "in the test or a page-object call."
            ),
            false=(
                "The test assumes an existing session, reuses a fixed email, or does not navigate "
                "to the login page."
            ),
        ),
    ),
}
