"""
Locust Performance & Load Testing Script for Reqres API.
Designed according to assignment requirements:
- Targets Reqres public API (GET /api/users endpoints)
- Simulates 5 to 10 concurrent users
- Enforces a strict maximum cap (<100 requests) to protect public API rate limits
- Includes both headless execution and interactive Web UI mode

Usage Examples:
1. Headless CLI mode (recommended for CI/automated runs):
   locust -f load_test.py --headless -u 5 -r 1 -t 15s --host https://reqres.in

2. Interactive Web UI mode:
   locust -f load_test.py --host https://reqres.in
   Then navigate to http://localhost:8089 in your browser.
"""

import logging
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, LocalRunner

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LocustLoadTest")

# Safety cap to strictly avoid exceeding the 100 API call daily budget
MAX_REQUEST_CAP = 60
request_counter = 0


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Event listener triggered on each HTTP request to enforce the strict request cap."""
    global request_counter
    request_counter += 1
    if request_counter >= MAX_REQUEST_CAP:
        logger.warning(
            f"Safety limit of {MAX_REQUEST_CAP} API requests reached! Signaling Locust to stop."
        )
        runner = events.request._runner_instance if hasattr(events.request, "_runner_instance") else None
        # Handled gracefully via stop runner check


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    """Store environment runner instance for safety shutdown."""
    events.request._runner_instance = environment.runner


class ReqresUser(HttpUser):
    """
    Simulates a concurrent user querying Reqres API endpoints.
    User waits between 1.0 and 2.5 seconds between requests (realistic user pacing).
    """

    wait_time = between(1.0, 2.5)

    def on_start(self):
        """User initialization lifecycle hook."""
        self.client.headers.update({
            "User-Agent": "Locust-QA-LoadTest/1.0",
            "Accept": "application/json"
        })

    @task(3)
    def get_users_list(self):
        """
        Simulate browsing the user list (Page 2).
        Weighted 3x frequency compared to single user lookup.
        """
        global request_counter
        if request_counter >= MAX_REQUEST_CAP:
            self.environment.runner.quit()
            return

        with self.client.get(
            "/api/users?page=2",
            name="/api/users?page=2",
            catch_response=True,
            timeout=10
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data and len(data["data"]) > 0:
                        response.success()
                    else:
                        response.failure("Response missing 'data' list")
                except Exception as err:
                    response.failure(f"JSON decoding error: {err}")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def get_single_user(self):
        """Simulate fetching details for a specific user (User ID 2)."""
        global request_counter
        if request_counter >= MAX_REQUEST_CAP:
            self.environment.runner.quit()
            return

        with self.client.get(
            "/api/users/2",
            name="/api/users/2",
            catch_response=True,
            timeout=10
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
