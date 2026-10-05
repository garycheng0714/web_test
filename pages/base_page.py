from typing import Self

from playwright.sync_api import Page

from components.header import Header

DEFAULT_BASE_URL = "https://automationexercise.com"


class BasePage:
    def __init__(self, page: Page, header: Header, base_url: str = DEFAULT_BASE_URL) -> None:
        self.page = page
        self.base_url = base_url
        self.header = header

    def open(self, path: str = "/") -> Self:
        self.page.goto(f"{self.base_url}{path}")
        return self

    def title(self) -> str:
        return self.page.title()

    def url(self) -> str:
        return self.page.url
