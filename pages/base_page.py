"""
Base Page module implementing core interactions with Selenium WebDriver.
Encapsulates explicit waits (WebDriverWait) and provides reusable, reliable methods
to avoid flakiness and hardcoded sleep calls.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import UI_EXPLICIT_WAIT


class BasePage:
    """Base class that all Page Objects inherit from."""

    def __init__(self, driver: WebDriver, timeout: int = UI_EXPLICIT_WAIT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        """Navigates to the specified URL if not already on it, minimizing redundant reloads."""
        # Normalize trailing slashes for comparison
        current = (self.driver.current_url or "").rstrip("/")
        target = url.rstrip("/")
        if current != target:
            self.driver.get(url)

    def get_title(self) -> str:
        """Returns the current page title."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Returns the current page URL."""
        return self.driver.current_url

    def find_visible(self, locator: tuple) -> WebElement:
        """Waits for an element to be visible on the page and returns it."""
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException as exc:
            raise TimeoutException(
                f"Element with locator {locator} was not visible within {self.timeout}s"
            ) from exc

    def find_present(self, locator: tuple) -> WebElement:
        """Waits for an element to be present in the DOM and returns it."""
        try:
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException as exc:
            raise TimeoutException(
                f"Element with locator {locator} was not found in DOM within {self.timeout}s"
            ) from exc

    def find_all(self, locator: tuple) -> list[WebElement]:
        """Finds all elements matching the locator after waiting for presence."""
        self.find_present(locator)
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple) -> None:
        """Waits for an element to be clickable and performs click."""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            self.scroll_into_view_element(element)
            element.click()
        except TimeoutException as exc:
            raise TimeoutException(
                f"Element with locator {locator} was not clickable within {self.timeout}s"
            ) from exc

    def type_text(self, locator: tuple, text: str, clear_existing: bool = True) -> None:
        """Waits for an element to be visible, optionally clears it, and types text."""
        element = self.find_visible(locator)
        self.scroll_into_view_element(element)
        if clear_existing:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        """Returns text of an element once visible."""
        return self.find_visible(locator).text.strip()

    def get_attribute_value(self, locator: tuple, attribute: str) -> str:
        """Returns value of a specific attribute of an element."""
        return self.find_present(locator).get_attribute(attribute)

    def is_displayed(self, locator: tuple, custom_timeout: int = 5) -> bool:
        """Checks if an element is visible within a custom short timeout."""
        try:
            WebDriverWait(self.driver, custom_timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def scroll_into_view_element(self, element: WebElement) -> None:
        """Executes JavaScript to smoothly scroll element into the center of viewport."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        except Exception:
            pass

    def wait_for_url_contains(self, partial_url: str, custom_timeout: int = None) -> bool:
        """Waits until the URL contains the expected substring."""
        timeout = custom_timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(EC.url_contains(partial_url))
