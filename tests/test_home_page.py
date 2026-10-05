from components.header import NAV_NAMES
from pages.home_page import HomePage


def test_home_page_loads(home_page: HomePage):
    home_page.open()
    assert home_page.title() == "Automation Exercise"
    assert home_page.url().startswith("https://automationexercise.com")
    assert home_page.header.is_logo_visible()


def test_home_page_shows_nav_links(home_page: HomePage):
    home_page.open()
    for name in NAV_NAMES:
        assert home_page.nav_link(name).is_visible()
