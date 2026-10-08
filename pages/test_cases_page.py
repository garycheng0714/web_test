from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class TestCasesPage(BasePage):
    __test__ = False

    @property
    def path(self) -> str:
        return "/test_cases"

    def test_cases_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Test Cases", exact=True)

    def expect_loaded(self) -> None:
        super().expect_loaded()
        expect(self.test_cases_heading()).to_be_visible()
