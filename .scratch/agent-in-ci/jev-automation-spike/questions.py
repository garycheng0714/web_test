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
            "Does the test assert every expected result in the case? The subject's `test` shows the "
            "assertions and `support` shows the page-object queries. An expected result is covered "
            "only if the test would fail when that result is absent; a URL-only or trivially true "
            "assertion does not cover a visible block, field, value, or page heading."
        ),
        criteria=NoulCriteria(
            true=(
                "Every expected result has an assertion that would fail if the result were absent."
            ),
            false=(
                "At least one expected result is missing or replaced by a weaker assertion (for "
                "example, only the URL)."
            ),
        ),
    ),
    "no_invented_behavior": Noul(
        instructions=(
            "Does the test avoid actions or assertions the case does not describe? Setup needed to "
            "reach the case is allowed; a different flow (for example, logging in instead of signing "
            "up) or unrelated assertions is not."
        ),
        criteria=NoulCriteria(
            true="Only the case's behavior plus necessary setup/cleanup appears.",
            false="The test invents behavior or asserts something the case does not describe.",
        ),
    ),
    "preconditions_setup": Noul(
        instructions=(
            "Does the test establish the case's preconditions? The preconditions are listed in the "
            "case: a guest, the browser on /login, and an email that has never been registered. A "
            "page-object `open()` on the login page and a timestamped email count as setup."
        ),
        criteria=NoulCriteria(
            true=(
                "Each precondition is met by a fixture, a setup step, or the page-object action the "
                "test calls."
            ),
            false=(
                "A precondition is assumed or missing (for example, a reused email or no login-page "
                "navigation)."
            ),
        ),
    ),
}
