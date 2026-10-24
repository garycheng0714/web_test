from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    @property
    def path(self) -> str:
        return "/login"

    def _signup_form(self) -> Locator:
        return self.page.locator(".signup-form")

    def signup_name_input(self) -> Locator:
        return self._signup_form().get_by_placeholder("Name")

    def signup_email_input(self) -> Locator:
        return self._signup_form().get_by_placeholder("Email Address")

    def signup_button(self) -> Locator:
        return self._signup_form().get_by_role("button", name="Signup")

    def fill_signup_form(self, name: str, email: str) -> Self:
        self.signup_name_input().fill(name)
        self.signup_email_input().fill(email)
        return self

    def click_signup(self) -> None:
        self.signup_button().click()

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        expect(self.page.get_by_role("heading", name="Login to your account")).to_be_visible()
        return self
