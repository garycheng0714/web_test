import pytest
from playwright.sync_api import Page

from components.header import Header


@pytest.fixture
def header(page: Page) -> Header:
    return Header(page)
