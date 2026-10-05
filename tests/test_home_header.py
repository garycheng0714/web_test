from playwright.sync_api import Page

from components.header import Header

BASE_URL = "https://automationexercise.com/"
NAV_LINKS = [
    "Home",
    "Products",
    "Cart",
    "Signup / Login",
    "Test Cases",
    "API Testing",
    "Video Tutorials",
    "Contact us",
]


def test_home_header_is_visible(page: Page, header: Header):
    page.goto(BASE_URL)
    assert header.is_visible()
    assert header.is_logo_visible()


def test_home_header_shows_nav_links(page: Page, header: Header):
    page.goto(BASE_URL)
    assert header.nav_names() == NAV_LINKS
