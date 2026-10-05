from components.header import NAV_NAMES
from pages.home_page import HomePage


def test_home_header_is_visible(home_page: HomePage):
    home_page.open()
    assert home_page.header.is_visible()
    assert home_page.header.is_logo_visible()


def test_home_header_shows_nav_links(home_page: HomePage):
    home_page.open()
    assert home_page.header.nav_names() == list(NAV_NAMES)
