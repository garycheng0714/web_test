import re
import time

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage


@pytest.mark.case("register-login-smoke", 1)
def test_signup_opens_account_information(login_page: LoginPage) -> None:
    login_page.open().expect_loaded()
    expect(login_page.signup_block()).to_be_visible()
    expect(login_page.signup_name()).to_be_visible()
    expect(login_page.signup_email()).to_be_visible()
    expect(login_page.signup_button()).to_be_visible()

    email = f"ocqa.{int(time.time())}@test.com"
    login_page.signup_name().fill("OC QA")
    login_page.signup_email().fill(email)
    expect(login_page.signup_name()).to_have_value("OC QA")
    expect(login_page.signup_email()).to_have_value(email)

    login_page.click_signup()
    expect(login_page.page).to_have_url(re.compile(r"automationexercise"))
