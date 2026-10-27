import time

import pytest

from pages.login_page import LoginPage


@pytest.mark.case("register-login-smoke", 1)
def test_signup_opens_account_information(login_page: LoginPage) -> None:
    login_page.open().expect_loaded()

    email = f"ocqa.{int(time.time())}@test.com"
    login_page.signup_name().fill("OC QA")
    login_page.signup_email().fill(email)

    login_page.click_signup()
