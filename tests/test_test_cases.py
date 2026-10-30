import pytest

from pages.home_page import HomePage
from pages.test_cases_page import TestCasesPage

pytestmark = pytest.mark.usefixtures("block_ads")


def test_navigate_to_test_cases_from_header(
    home_page: HomePage, test_cases_page: TestCasesPage
) -> None:
    (home_page.open().expect_loaded().click_nav_link("Test Cases"))

    test_cases_page.expect_loaded()
