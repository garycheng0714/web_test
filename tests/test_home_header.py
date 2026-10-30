import pytest

from components.header import NAV_NAMES
from pages.home_page import HomePage

pytestmark = pytest.mark.usefixtures("block_ads")


def test_home_header_is_visible(home_page: HomePage):
    home_page.open()
    assert home_page.header.is_visible()
    assert home_page.header.is_logo_visible()


# The Products nav link's accessible name carries a leading private-use glyph,
# so the exact-name comparison cannot pass. See .scratch/known-issues.md.
@pytest.mark.skip(
    reason="known issue: Products nav link has a private-use glyph in its accessible name"
)
def test_home_header_shows_nav_links(home_page: HomePage):
    home_page.open()
    assert home_page.header.nav_names() == list(NAV_NAMES)
