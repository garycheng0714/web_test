import pytest
from playwright.sync_api import Page

from components.header import Header
from pages.login_page import LoginPage


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page, Header(page))
