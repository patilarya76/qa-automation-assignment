"""
Page Object representing the DaveAI Homepage (https://www.iamdave.ai).
Contains all selectors and user interaction methods for the homepage.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import DAVE_AI_BASE_URL


class HomePage(BasePage):
    """Encapsulates elements and actions available on the DaveAI Homepage."""

    # --- Selectors ---
    LOGO = (By.CSS_SELECTOR, "img[src*='DaveAI_Logo'], header img, .navbar-brand img")
    MAIN_HEADING = (By.TAG_NAME, "h1")
    SUB_HEADINGS = (By.TAG_NAME, "h2")
    NAV_LINKS = (By.CSS_SELECTOR, "nav a, header a, .main-navigation a")
    BOOK_DEMO_BUTTON = (By.CSS_SELECTOR, "a[href*='book-demo']")
    PLATFORM_LINK = (By.CSS_SELECTOR, "a[href*='/platform/']")
    FOOTER = (By.TAG_NAME, "footer")

    def __init__(self, driver):
        super().__init__(driver)

    def load(self) -> "HomePage":
        """Opens the DaveAI homepage."""
        import config.config as cfg
        self.open(cfg.DAVE_AI_BASE_URL)
        return self

    def get_main_heading_text(self) -> str:
        """Retrieves the primary H1 headline of the homepage."""
        return self.get_text(self.MAIN_HEADING)

    def is_logo_displayed(self) -> bool:
        """Verifies if the brand logo is displayed on the page."""
        return self.is_displayed(self.LOGO)

    def get_logo_src(self) -> str:
        """Returns the source URL of the brand logo."""
        return self.get_attribute_value(self.LOGO, "src")

    def click_book_demo(self) -> None:
        """Clicks the Book Demo CTA button."""
        # Find all matching book demo links and click the first visible/interactive one
        buttons = self.driver.find_elements(*self.BOOK_DEMO_BUTTON)
        for btn in buttons:
            if btn.is_displayed():
                self.scroll_into_view_element(btn)
                btn.click()
                return
        # Fallback to standard click if none matched is_displayed check immediately
        self.click(self.BOOK_DEMO_BUTTON)

    def get_navigation_item_texts(self) -> list[str]:
        """Returns a list of visible navigation menu labels."""
        elements = self.driver.find_elements(*self.NAV_LINKS)
        return [el.text.strip() for el in elements if el.text.strip()]
