from typing import Self

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    TITLE = "Automation Exercise"

    @property
    def path(self) -> str:
        return "/"

    def nav_link(self, name: str) -> Locator:
        return self.header.nav_link(name)

    def click_nav_link(self, name: str) -> None:
        self.header.click_nav_link(name)

    def expect_loaded(self) -> Self:
        super().expect_loaded()
        expect(self.page).to_have_title(self.TITLE)
        return self
