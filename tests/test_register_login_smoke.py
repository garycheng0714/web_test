import time

from pages.account_information_page import AccountInformationPage
from pages.login_page import LoginPage


def test_new_user_signup_opens_account_information_page(
    login_page: LoginPage,
    account_information_page: AccountInformationPage,
) -> None:
    login_page.open()
    login_page.page.wait_for_load_state("networkidle")
    login_page.expect_loaded()

    email = f"ocqa.{time.time_ns()}@test.com"
    (
        login_page.enter_signup_name("OC QA")
        .enter_signup_email(email)
        .click_signup()
    )

    account_information_page.expect_loaded()
