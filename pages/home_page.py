from playwright.sync_api import Locator

from pages.base_page import BasePage


class HomePage(BasePage):
    TITLE = "Automation Exercise"

    @property
    def path(self) -> str:
        return "/"

    def nav_link(self, name: str) -> Locator:
        return self.header.nav_link(name)
