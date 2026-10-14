from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class ContactUsPage(BasePage):
    __test__ = False

    @property
    def path(self) -> str:
        return "/contact_us"

    def _form(self) -> Locator:
        return self.page.locator("#contact-us-form")

    def get_in_touch_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Get In Touch", exact=True)

    def name_field(self) -> Locator:
        return self._form().get_by_role("textbox", name="Name")

    def email_field(self) -> Locator:
        return self._form().get_by_role("textbox", name="Email")

    def subject_field(self) -> Locator:
        return self._form().get_by_role("textbox", name="Subject")

    def message_field(self) -> Locator:
        return self._form().get_by_role("textbox", name="Your Message Here")

    def upload_file(self, file_path: str) -> Self:
        self.page.locator("input[name='upload_file']").set_input_files(file_path)
        return self

    def submit_button(self) -> Locator:
        return self.page.get_by_role("button", name="Submit")

    def submit(self) -> Self:
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.submit_button().click()
        return self

    def success_message(self) -> Locator:
        return self.page.locator(".status.alert.alert-success")

    def expect_loaded(self) -> Self:
        self.page.wait_for_load_state("networkidle")
        super().expect_loaded()
        expect(self.get_in_touch_heading()).to_be_visible()
        return self
