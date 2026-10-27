from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    __test__ = False

    @property
    def path(self) -> str:
        return "/login"

    def signup_block(self) -> Locator:
        return self.page.locator(".signup-form")

    def signup_name(self) -> Locator:
        return self.signup_block().get_by_placeholder("Name")

    def signup_email(self) -> Locator:
        return self.signup_block().get_by_placeholder("Email Address")

    def signup_button(self) -> Locator:
        return self.signup_block().get_by_role("button", name="Signup")

    def click_login(self) -> Self:
        self.page.locator(".login-form").get_by_role("button", name="Login").click()
        return self

    def click_signup(self) -> Self:
        self.signup_button().click()
        return self

    def account_information_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Enter Account Information")

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        expect(self.signup_block()).to_be_visible()
        return self
