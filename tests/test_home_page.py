import pytest
from playwright.sync_api import expect

from components.header import NAV_NAMES
from pages.home_page import HomePage

pytestmark = [pytest.mark.live, pytest.mark.usefixtures("block_ads")]


def test_home_page_loads(home_page: HomePage) -> None:
    home_page.open()
    home_page.expect_loaded()


def test_home_page_shows_nav_links(home_page: HomePage) -> None:
    home_page.open()
    for name in NAV_NAMES:
        expect(home_page.nav_link(name)).to_be_visible()
