from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage

class ContactUsPage(BasePage):
    @property
    def path(self) -> str:
        return "/contact_us"

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        self.page.wait_for_load_state("networkidle")
        expect(self.page.get_by_role("heading", name="GET IN TOUCH")).to_be_visible()
        return self

    def fill_form(self, name: str, email: str, subject: str, message: str) -> Self:
        self.page.get_by_placeholder("Name").fill(name)
        self.page.get_by_placeholder("Email", exact=True).fill(email)
        self.page.get_by_placeholder("Subject").fill(subject)
        self.page.get_by_placeholder("Your Message Here").fill(message)
        return self

    def upload_file(self, file_path: str) -> Self:
        self.page.locator("input[name='upload_file']").set_input_files(file_path)
        return self

    def submit_form(self) -> Self:
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_role("button", name="Submit").click()
        return self

    def success_message(self) -> Locator:
        return self.page.locator(".status.alert.alert-success")

    def click_home_button(self) -> None:
        self.page.locator("#contact-page").get_by_role("link", name="Home").click()
