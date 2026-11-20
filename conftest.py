"""
Pytest configuration file containing shared fixtures for API and UI test suites.
Manages test setup, browser driver lifecycle, and API session handling.
"""

import os
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from config.config import (
    DEFAULT_API_HEADERS,
    BROWSER_NAME,
    HEADLESS_MODE,
    PAGE_LOAD_TIMEOUT
)


def pytest_addoption(parser):
    """Adds custom command-line options for test execution."""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser tests in headed mode (visible UI window)."
    )
    parser.addoption(
        "--browser",
        action="store",
        default=BROWSER_NAME,
        help="Browser to run tests on: chrome or edge."
    )
    parser.addoption(
        "--mock",
        action="store_true",
        default=False,
        help="Run UI tests against built-in local mock server (guarantees fast, offline CI/CD stability)."
    )


@pytest.fixture(scope="session", autouse=True)
def mock_server_daemon(request):
    """
    Session-level fixture that automatically spins up a local mock server
    if the --mock flag is passed to pytest.
    """
    if request.config.getoption("--mock"):
        import threading
        import socketserver
        from mock_server import MockServerHandler
        import config.config as cfg

        # Allow port reuse
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer(("127.0.0.1", 5000), MockServerHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        # Update runtime configuration for both API and UI
        cfg.REQRES_BASE_URL = "http://127.0.0.1:5000/api"
        cfg.DAVE_AI_BASE_URL = "http://127.0.0.1:5000"
        cfg.BOOK_DEMO_URL = f"{cfg.DAVE_AI_BASE_URL}/book-demo/"
        cfg.PLATFORM_URL = f"{cfg.DAVE_AI_BASE_URL}/platform/"

        yield server
        server.shutdown()
    else:
        yield None


# ---------------------------------------------------------------------------
# API Test Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def api_session():
    """
    Setup & Teardown for API testing:
    - Sets up a persistent requests.Session with default headers and timeout.
    - Yields the session to test functions.
    - Tears down by closing the session cleanly.
    """
    session = requests.Session()
    session.headers.update(DEFAULT_API_HEADERS)
    yield session
    session.close()


# ---------------------------------------------------------------------------
# UI Test Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="class")
def driver(request):
    """
    Setup & Teardown for UI testing:
    - Scoped to 'class' to execute the end-to-end user journey within a single
      browser session, significantly reducing latency and external network requests.
    - Configures window dimensions (1920x1080) and headless options.
    - Yields driver to the test class.
    - Quits the driver cleanly in the teardown phase to prevent orphan processes.
    """
    is_headed = request.config.getoption("--headed")
    browser = request.config.getoption("--browser").lower()
    run_headless = False if is_headed else HEADLESS_MODE

    driver_instance = None

    if browser == "edge":
        options = EdgeOptions()
        if run_headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver_instance = webdriver.Edge(options=options)
    else:
        # Default to Chrome
        options = ChromeOptions()
        if run_headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        driver_instance = webdriver.Chrome(options=options)

    driver_instance.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    # Hand control over to the test class
    yield driver_instance

    # Teardown phase: safely quit browser
    try:
        driver_instance.quit()
    except Exception:
        pass
