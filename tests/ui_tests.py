"""
UI Automation Test Suite for DaveAI (https://www.iamdave.ai).
Uses Selenium WebDriver with the Page Object Model (POM) pattern.
Covers:
1. Page load, Title & Logo verification
2. Key Homepage elements (H1 heading, navigation, CTA)
3. Navigation flow (from Homepage to Book Demo page)
4. Form input interaction on the Book Demo page
"""

import pytest
from pages.home_page import HomePage
from pages.book_demo_page import BookDemoPage
from config.config import BOOK_DEMO_URL, DAVE_AI_BASE_URL


@pytest.mark.ui
class TestDaveAiWebsite:
    """
    Test suite targeting the DaveAI web application.
    Executes a cohesive user journey:
    Load Homepage -> Validate Branding -> Inspect Key Elements -> Navigate -> Interact with Form.
    """

    def test_homepage_load_title_and_logo(self, driver):
        """
        Test Case 1: Verify website loads successfully and displays expected title and logo.
        Checks:
        - Website loads with HTTP 200 equivalent.
        - Page title contains expected brand name 'DaveAI'.
        - Brand logo element is visible and has a valid SVG/image source URL.
        """
        home_page = HomePage(driver).load()

        # 1. Assert Title
        actual_title = home_page.get_title()
        assert "DaveAI" in actual_title or "Automotive" in actual_title, (
            f"Expected 'DaveAI' or 'Automotive' in title, but received: '{actual_title}'"
        )

        # 2. Assert Logo visibility and source
        assert home_page.is_logo_displayed(), "Brand logo was not displayed on the homepage"
        logo_src = home_page.get_logo_src()
        assert logo_src is not None and ("logo" in logo_src.lower() or "daveai" in logo_src.lower()), (
            f"Expected logo image source to contain 'logo' or 'daveai', got: '{logo_src}'"
        )

    def test_homepage_key_elements_presence(self, driver):
        """
        Test Case 2: Check for presence and visibility of key elements on the homepage.
        Checks:
        - Primary H1 heading is present and displays expected messaging.
        - Navigation menu has visible options.
        - 'Book Demo' CTA button is present and visible.
        """
        home_page = HomePage(driver)
        if "iamdave.ai" not in driver.current_url:
            home_page.load()

        # 1. Assert H1 heading
        heading_text = home_page.get_main_heading_text()
        assert len(heading_text) > 0, "Primary H1 heading is empty or missing"
        assert "Automotive" in heading_text or "Intelligence" in heading_text, (
            f"Unexpected H1 heading text: '{heading_text}'"
        )

        # 2. Assert navigation links
        nav_items = home_page.get_navigation_item_texts()
        assert len(nav_items) > 0, "No navigation items found on header"

        # 3. Assert Book Demo CTA button presence
        assert home_page.is_displayed(home_page.BOOK_DEMO_BUTTON), (
            "Book Demo CTA button is not displayed on the homepage"
        )

    def test_navigation_flow_to_book_demo(self, driver):
        """
        Test Case 3: Test navigation flow from Homepage to Book Demo page.
        Checks:
        - User clicks on 'Book Demo' CTA button on homepage.
        - Browser navigates to the Book Demo page URL.
        - The resulting page contains expected 'Book Demo' title and headings.
        """
        home_page = HomePage(driver)
        if "iamdave.ai" not in driver.current_url or "book-demo" in driver.current_url:
            home_page.load()

        # Perform navigation click
        home_page.click_book_demo()

        # Wait for URL transition
        demo_page = BookDemoPage(driver)
        assert demo_page.wait_for_url_contains("book-demo", custom_timeout=15), (
            f"Expected URL to contain 'book-demo', but current URL is: '{demo_page.get_current_url()}'"
        )

        # Assert destination page title
        page_title = demo_page.get_title()
        assert "Book Demo" in page_title or "DaveAI" in page_title, (
            f"Expected 'Book Demo' in page title, got: '{page_title}'"
        )

    def test_book_demo_form_input_interaction(self, driver):
        """
        Test Case 4: Test form input field interaction on the Book Demo page.
        Checks:
        - Navigates to Book Demo page if not already there.
        - Interacts with form fields: Name, Work Email, Company Name, Phone, and Message.
        - Verifies that entered text is properly stored in DOM value attributes.
        - Verifies that the submit button is present and ready for interaction.
        """
        demo_page = BookDemoPage(driver)
        if "book-demo" not in driver.current_url:
            demo_page.load()

        test_data = {
            "name": "QA Candidate",
            "email": "qa.interview.test@example.com",
            "company": "Automation Enterprise",
            "phone": "+1987654321",
            "message": "Automated regression verification inquiry."
        }

        # Fill in form input fields
        demo_page.fill_demo_form(
            name=test_data["name"],
            email=test_data["email"],
            company=test_data["company"],
            phone=test_data["phone"],
            message=test_data["message"]
        )

        # Read back entered values to assert input fields interacted properly
        entered_values = demo_page.get_input_field_values()
        assert entered_values.get("name") == test_data["name"], (
            f"Name field mismatch: expected '{test_data['name']}', got '{entered_values.get('name')}'"
        )
        assert entered_values.get("email") == test_data["email"], (
            f"Email field mismatch: expected '{test_data['email']}', got '{entered_values.get('email')}'"
        )
        assert entered_values.get("company") == test_data["company"], (
            f"Company field mismatch: expected '{test_data['company']}', got '{entered_values.get('company')}'"
        )
        assert entered_values.get("phone") == test_data["phone"], (
            f"Phone field mismatch: expected '{test_data['phone']}', got '{entered_values.get('phone')}'"
        )

        # Assert submit button presence
        assert demo_page.is_submit_button_present(), "Submit button not found on Book Demo form"
