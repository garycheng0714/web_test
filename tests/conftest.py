import pytest
from playwright.sync_api import Page

from components.header import Header
from pages.home_page import HomePage
from pages.test_cases_page import TestCasesPage


@pytest.fixture
def header(page: Page) -> Header:
    return Header(page)


@pytest.fixture
def home_page(page: Page, header: Header) -> HomePage:
    return HomePage(page, header)


@pytest.fixture
def test_cases_page(page: Page, header: Header) -> TestCasesPage:
    return TestCasesPage(page, header)

