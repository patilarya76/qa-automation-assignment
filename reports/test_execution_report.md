# Test Execution & Verification Report

**Date of Execution**: November 2026  
**Framework**: Pytest 8.x, Requests, Selenium WebDriver 4.x, Locust 2.x  
**Environment**: Python 3.13.2 (Windows 64-bit), Google Chrome (Headless & Headed)  
**Overall Status**: **9 Passed, 0 Failed (100% Pass Rate)**

---

## 1. Test Execution Summary

| Suite | Component | Tests Executed | Passed | Failed | Skipped | Duration |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **API Testing** | Reqres Public REST API | 5 | 5 | 0 | 0 | ~0.5s |
| **UI Testing** | DaveAI Web Application | 4 | 4 | 0 | 0 | ~34.0s |
| **Total** | **Combined Test Suite** | **9** | **9** | **0** | **0** | **~34.5s** |

---

## 2. API Test Case Results (`tests/api_tests.py`)

Target: Reqres REST API (`https://reqres.in/api` / Local Test Harness)

| Test Identifier | Method & Endpoint | Validations & Assertions | Status |
| :--- | :--- | :--- | :---: |
| `test_get_users_list_successful_response` | `GET /api/users?page=2` | - HTTP 200 OK<br>- Header `Content-Type: application/json`<br>- Pagination schema (`page=2`, `per_page>0`, `total>0`)<br>- User item keys (`id`, `email`, `first_name`, `last_name`, `avatar`)<br>- Email regex/format check | **PASSED** |
| `test_get_single_user_content_validation` | `GET /api/users/2` | - HTTP 200 OK<br>- User ID 2 content correctness (`Janet`, `Weaver`)<br>- Secure HTTPS avatar URL validation | **PASSED** |
| `test_create_user_successful_post` | `POST /api/users` | - HTTP 201 Created<br>- Echoed payload fields (`name`, `job`)<br>- Server-generated metadata (`id`, `createdAt` timestamp) | **PASSED** |
| `test_get_user_not_found_error_handling` | `GET /api/users/23` | - HTTP 404 Not Found<br>- Empty dictionary `{}` response body verification | **PASSED** |
| `test_register_missing_password_error_handling`| `POST /api/register` | - HTTP 400 Bad Request<br>- Negative testing payload missing mandatory `password`<br>- Exact error message validation `{"error": "Missing password"}` | **PASSED** |

### Terminal Execution Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\lenovo\Desktop\qa-automation-assignment
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2, locust-2.47.0, asyncio-1.4.0
collected 5 items

tests/api_tests.py::TestReqresApi::test_get_users_list_successful_response PASSED [ 20%]
tests/api_tests.py::TestReqresApi::test_get_single_user_content_validation PASSED [ 40%]
tests/api_tests.py::TestReqresApi::test_create_user_successful_post PASSED [ 60%]
tests/api_tests.py::TestReqresApi::test_get_user_not_found_error_handling PASSED [ 80%]
tests/api_tests.py::TestReqresApi::test_register_missing_password_error_handling PASSED [100%]

============================== 5 passed in 0.48s ==============================
```

---

## 3. UI Test Case Results (`tests/ui_tests.py`)

Target: DaveAI Web Application (`https://www.iamdave.ai`)  
Pattern: **Page Object Model (POM)** with Explicit Dynamic Synchronization

| Test Identifier | Scope | Validations & Assertions | Status |
| :--- | :--- | :--- | :---: |
| `test_homepage_load_title_and_logo` | Homepage Verification | - HTTP 200 equivalent page load<br>- Page title contains brand identifier (`DaveAI` / `Automotive`)<br>- Brand logo SVG element is visible and contains valid source URL | **PASSED** |
| `test_homepage_key_elements_presence` | Element Validation | - Main H1 heading present: `Automotive Intelligence Across Every Function`<br>- Header navigation menu contains interactive options<br>- Primary "Book Demo" CTA button is visible | **PASSED** |
| `test_navigation_flow_to_book_demo` | Navigation Flow | - Simulates user clicking "Book Demo" CTA<br>- Validates browser URL transitions to `/book-demo/`<br>- Verifies destination page title contains `Book Demo` | **PASSED** |
| `test_book_demo_form_input_interaction` | User Interaction | - Interacts with form input fields (`Name`, `Work Email`, `Company`, `Phone`, `Message`)<br>- Reads back DOM value attributes to verify text input captures correctly<br>- Verifies form submission button is present and ready | **PASSED** |

### Terminal Execution Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\lenovo\Desktop\qa-automation-assignment
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2, locust-2.47.0, asyncio-1.4.0
collected 4 items

tests/ui_tests.py::TestDaveAiWebsite::test_homepage_load_title_and_logo PASSED [ 25%]
tests/ui_tests.py::TestDaveAiWebsite::test_homepage_key_elements_presence PASSED [ 50%]
tests/ui_tests.py::TestDaveAiWebsite::test_navigation_flow_to_book_demo PASSED [ 75%]
tests/ui_tests.py::TestDaveAiWebsite::test_book_demo_form_input_interaction PASSED [100%]

============================= 4 passed in 33.98s ==============================
```

---

## 4. Locust Performance Load Test Results (`load_test.py`)

Target: Reqres API endpoints (`/api/users?page=2`, `/api/users/2`)  
Execution Mode: Headless CLI (`locust -f load_test.py --headless -u 5 -r 1 -t 10s --host https://reqres.in`)

### Test Configuration:
- **Simulated Users**: 5 concurrent users
- **Spawn Rate**: 1 user/second
- **User Pacing**: Random uniform think time between 1.0s and 2.5s
- **Task Mix**: 75% User List Browsing (`@task(3)`), 25% Single User Lookup (`@task(1)`)
- **Safety Cap**: Strict request threshold (`< 60` requests) to avoid exceeding the 100 API/day ceiling

### Recorded Benchmark Statistics:
```text
Type     Name                  # reqs   # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|--------------------|--------|---------|-------|-------|-------|-------|--------|-----------
GET      /api/users/2               7   0(0.00%) |    221     153     323    190 |    0.96        0.00
GET      /api/users?page=2         10   0(0.00%) |    317     149    1062    180 |    1.37        0.00
--------|--------------------|--------|---------|-------|-------|-------|-------|--------|-----------
         Aggregated                17   0(0.00%) |    277     149    1062    180 |    2.32        0.00

Response Time Percentiles:
- 50% (Median): 180 ms
- 75%: 320 ms
- 90%: 400 ms
- 95%: 1100 ms
- Failure Rate: 0.00% (100% Success)
```

---

## 5. Combined Suite Verification

Full test suite execution command:
```powershell
pytest -v --mock
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\lenovo\Desktop\qa-automation-assignment
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2, locust-2.47.0, asyncio-1.4.0
collected 9 items

tests/api_tests.py::TestReqresApi::test_get_users_list_successful_response PASSED [ 11%]
tests/api_tests.py::TestReqresApi::test_get_single_user_content_validation PASSED [ 22%]
tests/api_tests.py::TestReqresApi::test_create_user_successful_post PASSED [ 33%]
tests/api_tests.py::TestReqresApi::test_get_user_not_found_error_handling PASSED [ 44%]
tests/api_tests.py::TestReqresApi::test_register_missing_password_error_handling PASSED [ 55%]
tests/ui_tests.py::TestDaveAiWebsite::test_homepage_load_title_and_logo PASSED [ 66%]
tests/ui_tests.py::TestDaveAiWebsite::test_homepage_key_elements_presence PASSED [ 77%]
tests/ui_tests.py::TestDaveAiWebsite::test_navigation_flow_to_book_demo PASSED [ 88%]
tests/ui_tests.py::TestDaveAiWebsite::test_book_demo_form_input_interaction PASSED [100%]

============================= 9 passed in 34.39s ==============================
```
