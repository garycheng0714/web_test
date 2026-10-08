from abc import ABC, abstractmethod
from typing import Self

from playwright.sync_api import Page, expect

from components.header import Header

DEFAULT_BASE_URL = "https://automationexercise.com"


class BasePage(ABC):
    @property
    @abstractmethod
    def path(self) -> str: ...

    def __init__(self, page: Page, header: Header, base_url: str = DEFAULT_BASE_URL) -> None:
        self.page = page
        self.base_url = base_url
        self.header = header

    def open(self, path: str | None = None) -> Self:
        self.page.goto(f"{self.base_url}{self.path if path is None else path}")
        return self

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}{self.path}")
