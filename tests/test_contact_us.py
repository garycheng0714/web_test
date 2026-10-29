from playwright.sync_api import expect

from pages.contact_us_page import ContactUsPage
from pages.home_page import HomePage


def test_contact_us_form(
    home_page: HomePage, contact_us_page: ContactUsPage, tmp_path
) -> None:
    home_page.open().expect_loaded()

    home_page.click_nav_link("Contact us")
    contact_us_page.expect_loaded()

    contact_us_page.name_field().fill("Test User")
    contact_us_page.email_field().fill("testuser@example.com")
    contact_us_page.subject_field().fill("Test Subject")
    contact_us_page.message_field().fill("This is a test message.")

    upload_file = tmp_path / "contact_attachment.txt"
    upload_file.write_text("test file content")
    contact_us_page.upload_file(str(upload_file))

    contact_us_page.submit()

    expect(contact_us_page.success_message()).to_have_text(
        "Success! Your details have been submitted successfully."
    )

    home_page.click_nav_link("Home")
    home_page.expect_loaded()
