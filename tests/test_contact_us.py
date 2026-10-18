import pytest
from pathlib import Path
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.contact_us_page import ContactUsPage


def test_contact_us_form(
    home_page: HomePage,
    contact_us_page: ContactUsPage,
    tmp_path: Path,
) -> None:
    # 2. Navigate to url
    home_page.open()

    # 3. Verify that home page is visible successfully
    home_page.expect_loaded()

    # 4. Click on 'Contact Us' button
    home_page.header.click_nav_link("Contact us")

    # 5. Verify 'GET IN TOUCH' is visible
    contact_us_page.expect_loaded()

    # 6. Enter name, email, subject and message
    contact_us_page.fill_form(
        name="Test User",
        email="testuser@example.com",
        subject="Test Subject",
        message="This is a test message."
    )

    # 7. Upload file
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("dummy content")
    contact_us_page.upload_file(str(test_file))

    # 8. Click 'Submit' button
    # 9. Click OK button (handled within submit_form action)
    contact_us_page.submit_form()

    # 10. Verify success message 'Success! Your details have been submitted successfully.' is visible
    expect(contact_us_page.success_message()).to_have_text(
        "Success! Your details have been submitted successfully."
    )

    # 11. Click 'Home' button and verify that landed to home page successfully
    contact_us_page.click_home_button()

    # 12. Verify that home page is visible successfully
    home_page.expect_loaded()
