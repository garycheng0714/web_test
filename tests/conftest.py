import pytest
from playwright.sync_api import Page

from components.header import Header
from pages.home_page import HomePage


@pytest.fixture
def header(page: Page) -> Header:
    return Header(page)


@pytest.fixture
def home_page(page: Page, header: Header) -> HomePage:
    return HomePage(page, header)
