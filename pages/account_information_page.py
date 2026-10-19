from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class AccountInformationPage(BasePage):
    @property
    def path(self) -> str:
        return "/signup"

    def heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Enter Account Information")

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        expect(self.heading()).to_be_visible()
        return self
