"""
API Test Suite for Reqres (https://reqres.in).
Covers:
- Successful status code validation (200 OK, 201 Created)
- Response content & JSON schema validation (keys, data types, specific values)
- Error handling for invalid parameters (400 Bad Request)
- Error handling for non-existent resources (404 Not Found)
- Graceful handling of external public rate limiting (HTTP 429)
"""

import pytest
import config.config as cfg


def _check_rate_limit(response):
    """Gracefully skips test if public Reqres anonymous rate limit (40 reqs/day) is hit."""
    if response.status_code == 429:
        pytest.skip(
            "Reqres public demo rate limit exceeded (HTTP 429). "
            "Use 'pytest --mock' to execute against local test server."
        )


@pytest.mark.api
class TestReqresApi:
    """Test suite targeting Reqres REST API endpoints."""

    def test_get_users_list_successful_response(self, api_session):
        """
        Test Case 1: Validate GET /api/users with pagination.
        Checks:
        - Status code is 200 OK.
        - Response headers contain application/json.
        - Response content has expected pagination keys ('page', 'per_page', 'total', 'data').
        - 'data' is a non-empty list of user objects with valid user schema.
        """
        page_number = 2
        url = f"{cfg.REQRES_BASE_URL}/users?page={page_number}"
        response = api_session.get(url, timeout=cfg.API_TIMEOUT)
        _check_rate_limit(response)

        # 1. Assert HTTP Status Code
        assert response.status_code == 200, (
            f"Expected status code 200 but received {response.status_code}. Response: {response.text}"
        )

        # 2. Assert Content-Type header
        assert "application/json" in response.headers.get("Content-Type", ""), (
            f"Expected application/json header but got {response.headers.get('Content-Type')}"
        )

        # 3. Assert Response Body Structure & Content
        json_body = response.json()
        assert json_body.get("page") == page_number, f"Expected page {page_number}, got {json_body.get('page')}"
        assert "per_page" in json_body and json_body["per_page"] > 0
        assert "total" in json_body and json_body["total"] > 0
        assert isinstance(json_body.get("data"), list), "Field 'data' should be a list"
        assert len(json_body["data"]) > 0, "'data' list should not be empty"

        # 4. Assert Schema of individual user item
        first_user = json_body["data"][0]
        expected_keys = {"id", "email", "first_name", "last_name", "avatar"}
        assert expected_keys.issubset(first_user.keys()), (
            f"User item missing required keys. Expected at least {expected_keys}, got {first_user.keys()}"
        )
        assert isinstance(first_user["id"], int), "User ID should be an integer"
        assert "@" in first_user["email"], f"Invalid email format: {first_user['email']}"

    def test_get_single_user_content_validation(self, api_session):
        """
        Test Case 2: Validate GET /api/users/{id} for specific content correctness.
        Checks:
        - Status code is 200 OK.
        - 'data' object contains accurate user identity for ID 2 (Janet Weaver).
        """
        user_id = 2
        url = f"{cfg.REQRES_BASE_URL}/users/{user_id}"
        response = api_session.get(url, timeout=cfg.API_TIMEOUT)
        _check_rate_limit(response)

        # Assert status code
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

        json_body = response.json()
        assert "data" in json_body, "Response missing top-level 'data' object"

        user_data = json_body["data"]
        # Assert content correctness
        assert user_data.get("id") == user_id, f"Expected user id {user_id}, got {user_data.get('id')}"
        assert user_data.get("email") == "janet.weaver@reqres.in"
        assert user_data.get("first_name") == "Janet"
        assert user_data.get("last_name") == "Weaver"
        assert user_data.get("avatar", "").startswith("https://"), "Avatar URL must use HTTPS"

    def test_create_user_successful_post(self, api_session):
        """
        Test Case 3: Validate POST /api/users creation.
        Checks:
        - Status code is 201 Created.
        - Request payload fields are reflected in the response.
        - Response contains generated 'id' and 'createdAt' timestamp.
        """
        url = f"{cfg.REQRES_BASE_URL}/users"
        payload = {
            "name": "Jane QA Engineer",
            "job": "Lead Test Architect"
        }
        response = api_session.post(url, json=payload, timeout=cfg.API_TIMEOUT)
        _check_rate_limit(response)

        # Assert status code
        assert response.status_code == 201, (
            f"Expected 201 Created but received {response.status_code}. Response: {response.text}"
        )

        json_body = response.json()
        # Assert payload values preserved
        assert json_body.get("name") == payload["name"]
        assert json_body.get("job") == payload["job"]

        # Assert generated server metadata
        assert "id" in json_body, "Server did not return a generated ID for created user"
        assert "createdAt" in json_body, "Server did not return a 'createdAt' timestamp"

    def test_get_user_not_found_error_handling(self, api_session):
        """
        Test Case 4: Validate Error Handling for non-existent resource (GET /api/users/23).
        Checks:
        - Server responds with 404 Not Found.
        - Response data is empty or indicates absence of user.
        """
        invalid_user_id = 23
        url = f"{cfg.REQRES_BASE_URL}/users/{invalid_user_id}"
        response = api_session.get(url, timeout=cfg.API_TIMEOUT)
        _check_rate_limit(response)

        assert response.status_code == 404, (
            f"Expected 404 Not Found for non-existent user, but got {response.status_code}"
        )
        assert response.json() == {}, f"Expected empty body for 404, got {response.text}"

    def test_register_missing_password_error_handling(self, api_session):
        """
        Test Case 5: Validate Error Handling for missing mandatory parameter (POST /api/register).
        Checks:
        - Server rejects request with 400 Bad Request.
        - Error payload clearly communicates reason: 'Missing password'.
        """
        url = f"{cfg.REQRES_BASE_URL}/register"
        incomplete_payload = {
            "email": "sydney@fife"
            # Missing mandatory 'password' parameter
        }
        response = api_session.post(url, json=incomplete_payload, timeout=cfg.API_TIMEOUT)
        _check_rate_limit(response)

        assert response.status_code == 400, (
            f"Expected 400 Bad Request for incomplete payload, but received {response.status_code}"
        )
        json_body = response.json()
        assert "error" in json_body, "Error response missing 'error' key"
        assert json_body["error"] == "Missing password", (
            f"Expected error message 'Missing password', received '{json_body.get('error')}'"
        )
