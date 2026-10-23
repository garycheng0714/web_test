import time

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.signup_page import SignupPage

pytestmark = pytest.mark.usefixtures("block_ads")


def test_signup_step_one_opens_account_info(
    login_page: LoginPage,
    signup_page: SignupPage,
) -> None:
    timestamp = str(int(time.time()))
    name = "OC QA"
    email = f"ocqa.{timestamp}@test.com"

    login_page.open()
    login_page.expect_loaded()

    expect(login_page.signup_name_input()).to_be_visible()
    expect(login_page.signup_email_input()).to_be_visible()
    expect(login_page.signup_button()).to_be_visible()

    login_page.fill_signup_form(name, email)
    expect(login_page.signup_name_input()).to_have_value(name)
    expect(login_page.signup_email_input()).to_have_value(email)

    login_page.click_signup()

    signup_page.page.wait_for_load_state("networkidle")
    signup_page.expect_loaded()
