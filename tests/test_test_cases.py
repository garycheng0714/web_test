from pages.home_page import HomePage
from pages.test_cases_page import TestCasesPage


def test_navigate_to_test_cases_from_header(home_page: HomePage, test_cases_page: TestCasesPage) -> None:
    home_page.open()
    home_page.expect_loaded()

    home_page.header.nav_link("Test Cases").click()

    test_cases_page.expect_loaded()
