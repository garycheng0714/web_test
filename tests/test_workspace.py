def test_browser_launches(page):
    page.set_content("<title>Example Domain</title>")
    assert page.title() == "Example Domain"
