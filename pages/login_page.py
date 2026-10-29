from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    @property
    def path(self) -> str:
        return "/login"

    def _signup_form(self) -> Locator:
        return self.page.locator(".signup-form")

    def signup_name_field(self) -> Locator:
        return self._signup_form().get_by_placeholder("Name")

    def signup_email_field(self) -> Locator:
        return self._signup_form().get_by_placeholder("Email Address")

    def signup_button(self) -> Locator:
        return self._signup_form().get_by_role("button", name="Signup")

    def enter_signup_name(self, name: str) -> Self:
        self.signup_name_field().fill(name)
        return self

    def enter_signup_email(self, email: str) -> Self:
        self.signup_email_field().fill(email)
        return self

    def click_signup(self) -> Self:
        self.signup_button().click()
        self.page.wait_for_load_state("networkidle")
        return self

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        expect(
            self._signup_form().get_by_role("heading", name="New User Signup!")
        ).to_be_visible()
        return self
