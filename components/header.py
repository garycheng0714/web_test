from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page) -> None:
        self.page = page

    def is_visible(self) -> bool:
        return self.page.get_by_role("banner").is_visible()

    def is_logo_visible(self) -> bool:
        return (
            self.page.get_by_role("banner")
            .get_by_role("img", name="Website for automation practice")
            .is_visible()
        )

    def nav_names(self) -> list[str]:
        links = self.page.get_by_role("banner").get_by_role("list").get_by_role("link")
        return [name.strip() for name in links.all_inner_texts()]
