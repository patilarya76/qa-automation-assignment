"""
Page Object representing the DaveAI Book Demo Page (https://www.iamdave.ai/book-demo/).
Encapsulates form input fields, interactions, and assertions.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import BOOK_DEMO_URL


class BookDemoPage(BasePage):
    """Encapsulates elements and actions on the Book Demo page."""

    # --- Selectors ---
    HEADING = (By.CSS_SELECTOR, "h1, h2")
    NAME_INPUT = (By.CSS_SELECTOR, "input[placeholder*='Name'], input[name*='name']")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email'], input[placeholder*='Email']")
    COMPANY_INPUT = (By.CSS_SELECTOR, "input[placeholder*='Company']")
    PHONE_INPUT = (By.CSS_SELECTOR, "input[type='tel'], input[placeholder*='Phone']")
    MESSAGE_INPUT = (By.CSS_SELECTOR, "textarea[placeholder*='help'], textarea[name*='message']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], .elementor-button, form input[type='submit']")

    def __init__(self, driver):
        super().__init__(driver)

    def load(self) -> "BookDemoPage":
        """Directly navigates to the Book Demo page."""
        import config.config as cfg
        self.open(cfg.BOOK_DEMO_URL)
        return self

    def fill_demo_form(
        self,
        name: str,
        email: str,
        company: str,
        phone: str,
        message: str = ""
    ) -> None:
        """Fills out the contact demo request form."""
        if self.is_displayed(self.NAME_INPUT):
            self.type_text(self.NAME_INPUT, name)
        if self.is_displayed(self.EMAIL_INPUT):
            self.type_text(self.EMAIL_INPUT, email)
        if self.is_displayed(self.COMPANY_INPUT):
            self.type_text(self.COMPANY_INPUT, company)
        if self.is_displayed(self.PHONE_INPUT):
            self.type_text(self.PHONE_INPUT, phone)
        if message and self.is_displayed(self.MESSAGE_INPUT):
            self.type_text(self.MESSAGE_INPUT, message)

    def get_input_field_values(self) -> dict[str, str]:
        """Reads back values entered into the form fields to verify user interactions."""
        values = {}
        if self.is_displayed(self.NAME_INPUT):
            values["name"] = self.get_attribute_value(self.NAME_INPUT, "value")
        if self.is_displayed(self.EMAIL_INPUT):
            values["email"] = self.get_attribute_value(self.EMAIL_INPUT, "value")
        if self.is_displayed(self.COMPANY_INPUT):
            values["company"] = self.get_attribute_value(self.COMPANY_INPUT, "value")
        if self.is_displayed(self.PHONE_INPUT):
            values["phone"] = self.get_attribute_value(self.PHONE_INPUT, "value")
        return values

    def is_submit_button_present(self) -> bool:
        """Checks if the form submission CTA button is present in the DOM."""
        buttons = self.driver.find_elements(*self.SUBMIT_BUTTON)
        return len(buttons) > 0
