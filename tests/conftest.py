import re

import pytest
from playwright.sync_api import BrowserContext, Page

from components.header import Header
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.test_cases_page import TestCasesPage

AD_URL_PATTERN = re.compile(
    r"googlesyndication\.com|doubleclick\.net|googleadservices\.com|"
    r"googletagservices\.com|adtrafficquality\.google"
)


@pytest.fixture
def block_ads(context: BrowserContext) -> None:
    context.route(AD_URL_PATTERN, lambda route: route.abort())


@pytest.fixture
def header(page: Page) -> Header:
    return Header(page)


@pytest.fixture
def home_page(page: Page, header: Header) -> HomePage:
    return HomePage(page, header)


@pytest.fixture
def test_cases_page(page: Page, header: Header) -> TestCasesPage:
    return TestCasesPage(page, header)


@pytest.fixture
def login_page(page: Page, header: Header) -> LoginPage:
    return LoginPage(page, header)


@pytest.fixture
def signup_page(page: Page, header: Header) -> SignupPage:
    return SignupPage(page, header)

