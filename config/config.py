"""
Global configuration constants and test settings.
Centralizing these values ensures easy environment switching and maintenance.
"""

import os

# --- API Configuration (Reqres) ---
REQRES_BASE_URL = os.getenv("REQRES_BASE_URL", "https://reqres.in/api")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
DEFAULT_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (QA-Automation-Framework)",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# --- UI Configuration (DaveAI) ---
DAVE_AI_BASE_URL = os.getenv("DAVE_AI_BASE_URL", "https://www.iamdave.ai")
BOOK_DEMO_URL = f"{DAVE_AI_BASE_URL}/book-demo/"
PLATFORM_URL = f"{DAVE_AI_BASE_URL}/platform/"

# Browser execution settings
BROWSER_NAME = os.getenv("BROWSER", "chrome").lower()
HEADLESS_MODE = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
UI_IMPLICIT_WAIT = int(os.getenv("UI_IMPLICIT_WAIT", "0"))  # Favor explicit waits
UI_EXPLICIT_WAIT = int(os.getenv("UI_EXPLICIT_WAIT", "10"))
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))
