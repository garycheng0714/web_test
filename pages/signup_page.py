from typing import Self

from playwright.sync_api import expect

from pages.base_page import BasePage


class SignupPage(BasePage):
    @property
    def path(self) -> str:
        return "/signup"

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        expect(
            self.page.get_by_role("heading", name="Enter Account Information")
        ).to_be_visible()
        return self
