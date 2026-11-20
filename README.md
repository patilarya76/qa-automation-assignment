# QA Automation Engineering Assignment: API, UI & Performance Testing

An enterprise-grade test automation framework developed in Python for both API (REST) and Web UI testing, accompanied by a performance load-testing suite.

---

## Table of Contents
1. [Project Overview & Objectives](#project-overview--objectives)
2. [Architectural Design Choices](#architectural-design-choices)
3. [Project Directory Structure](#project-directory-structure)
4. [Prerequisites & Installation](#prerequisites--installation)
5. [Test Execution Guide](#test-execution-guide)
   - [Running API Tests](#1-running-api-tests)
   - [Running Web UI Tests](#2-running-web-ui-tests)
   - [Running the Full Test Suite](#3-running-the-complete-test-suite)
   - [Running Locust Performance Load Tests](#4-running-locust-load-testing-bonus)
6. [Locust Load Test Plan & Results](#locust-load-test-plan--recorded-results)
7. [Interview Preparation Guide & Technical Explanations](#interview-preparation-guide--technical-explanations)

---

## Project Overview & Objectives

This repository satisfies all requirements for the QA Automation Engineer Assessment:

- **Part 1: API Testing**
  - **Target**: Public REST API [Reqres](https://reqres.in)
  - **Framework**: `pytest` and `requests`
  - **Coverage**: 5 comprehensive test cases covering `GET`, `POST`, status codes (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`), JSON schema validation, response headers, and error message validation.
  - **Bonus**: Locust performance load testing script with request-rate capping safely under the 100 daily API call threshold.

- **Part 2: Web UI Testing**
  - **Target**: DaveAI Automotive Intelligence Platform (`https://www.iamdave.ai`)
  - **Framework**: `pytest` and `Selenium WebDriver`
  - **Architecture**: **Page Object Model (POM)** with decoupled locator repositories and explicit dynamic synchronization (`WebDriverWait`).
  - **Coverage**: 4 end-to-end user scenarios covering page load, title & brand logo verification, key element presence (H1, navigation, CTA), navigation transition, and input field interactions with form readiness checks.

---

## Architectural Design Choices

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Test Runner** | `pytest 8.x` | Industry-standard test framework offering powerful fixtures, parameterization, strict markers, and detailed assertion introspection without boilerplate code. |
| **API Client** | `requests` | High-performance, clean HTTP library. Utilizing session-scoped `requests.Session` enables connection pooling, persistent default headers, and deterministic teardown. |
| **UI Automation** | `Selenium WebDriver 4.x` | Cross-browser compatibility (Chrome and Edge), native OS level browser controls, and support for headless execution in CI/CD pipelines. |
| **Design Pattern** | **Page Object Model (POM)** | Decouples test specifications from UI locator selectors and DOM interaction logic. Changes to the UI require updates in only one Page Object class rather than multiple tests. |
| **Synchronization** | **Explicit Dynamic Waits** | Uses `WebDriverWait` with `expected_conditions` (e.g. `visibility_of_element_located`, `element_to_be_clickable`). Eliminates brittle, non-deterministic `time.sleep()` calls while preventing flakiness. |
| **Load Testing** | `Locust 2.x` | Python-native, highly scalable user simulation with realistic wait times (`between(1.0, 2.5)`), event listeners for metric collection, and safety request throttling. |
| **Environment Switch** | `config/config.py` + Mock Staging | Provides dynamic environment configuration via environment variables and includes a built-in mock server (`--mock`) to guarantee 100% test reliability even when third-party servers throttle external traffic. |

---

## Project Directory Structure

```text
qa-automation-assignment/
├── config/
│   ├── __init__.py
│   └── config.py               # Global settings, base URLs, timeouts, headers
├── pages/
│   ├── __init__.py
│   ├── base_page.py            # Base Page encapsulating explicit WebDriverWait methods
│   ├── home_page.py            # Page Object for DaveAI Homepage (selectors & actions)
│   └── book_demo_page.py       # Page Object for DaveAI Book Demo Page & Forms
├── tests/
│   ├── __init__.py
│   ├── api_tests.py            # 5 automated REST API test cases for Reqres
│   └── ui_tests.py             # 4 automated UI test cases for DaveAI using POM
├── mock_site/                  # Local staging mock fixtures for CI/CD offline resilience
│   ├── index.html              # DaveAI Homepage fixture
│   └── book-demo.html          # DaveAI Book Demo page fixture
├── conftest.py                 # Pytest shared fixtures (api_session, driver lifecycle, mock daemon)
├── load_test.py                # Locust performance load test script with safety cap
├── mock_server.py              # Lightweight local HTTP server for offline/isolated execution
├── pytest.ini                  # Pytest configuration, custom markers, and discovery rules
├── requirements.txt            # Project dependencies
└── README.md                   # Complete framework documentation & interview guide
```

---

## Prerequisites & Installation

### 1. Requirements
- Python **3.10+** (Tested on Python 3.13)
- Google Chrome browser (or Microsoft Edge) installed

### 2. Setup Virtual Environment & Install Dependencies
Open PowerShell or your preferred terminal in the project directory:

```powershell
# 1. Create a virtual environment (recommended)
python -m venv venv

# 2. Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# 3. Upgrade pip and install all required packages
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Test Execution Guide

### 1. Running API Tests
Execute only the API test suite targeting the Reqres endpoints:

```powershell
pytest tests/api_tests.py -v
```

*Or run using the custom pytest marker:*
```powershell
pytest -m api -v
```

#### Test Cases Included:
1. `test_get_users_list_successful_response`: Validates `GET /api/users?page=2`, HTTP status `200 OK`, JSON pagination headers, and user object schema (`id`, `email`, `first_name`, `last_name`, `avatar`).
2. `test_get_single_user_content_validation`: Validates `GET /api/users/2` content correctness (`Janet Weaver`, HTTPS avatar).
3. `test_create_user_successful_post`: Validates `POST /api/users` creation, HTTP status `201 Created`, echoed body parameters, and generated `id` & `createdAt` timestamp.
4. `test_get_user_not_found_error_handling`: Validates negative test case `GET /api/users/23`, asserting `404 Not Found` and empty payload response.
5. `test_register_missing_password_error_handling`: Validates error handling for `POST /api/register` with missing required parameter, asserting `400 Bad Request` and exact error message `{"error": "Missing password"}`.

---

### 2. Running Web UI Tests

#### A. Running against Live Website (`https://www.iamdave.ai`):
```powershell
pytest tests/ui_tests.py -v
```

#### B. Running in Headed Mode (Watch Chrome Browser UI):
```powershell
pytest tests/ui_tests.py -v --headed
```

#### C. Running with Microsoft Edge:
```powershell
pytest tests/ui_tests.py -v --browser edge
```

#### D. Running in Mock Staging Mode (Guaranteed Fast & Offline CI/CD):
*Third-party marketing sites frequently enforce rate-limiting or experience latency during repeated automated runs. Passing `--mock` automatically starts a local mock server and executes the identical UI test suite in ~30 seconds:*
```powershell
pytest tests/ui_tests.py -v --mock
```

#### Test Cases Included:
1. `test_homepage_load_title_and_logo`: Verifies page title contains `DaveAI` / `Automotive` and the brand SVG logo is visible on the page with a valid source URL.
2. `test_homepage_key_elements_presence`: Asserts presence and visibility of the main H1 headline (`Automotive Intelligence Across Every Function`), top navigation menu links, and the primary "Book Demo" CTA.
3. `test_navigation_flow_to_book_demo`: Simulates clicking the homepage "Book Demo" CTA button and verifies smooth URL navigation to `/book-demo/` with expected destination page title.
4. `test_book_demo_form_input_interaction`: Navigates to `/book-demo/`, enters realistic candidate test data into form fields (Name, Work Email, Company, Phone Number, and Message), verifies that DOM input values accurately stored the text, and asserts that the submission button is present and ready for interaction.

---

### 3. Running the Complete Test Suite
Run all 9 tests (5 API + 4 UI) with a single command:

```powershell
pytest -v --mock
```

---

### 4. Running Locust Load Testing (Bonus)

The load testing script (`load_test.py`) simulates realistic user traffic against the Reqres API with an automated safety cap (`MAX_REQUEST_CAP = 60`) to respect the public API daily usage limit (< 100 requests).

#### Option 1: Headless CLI Mode (Simulating 5 Concurrent Users for 10 Seconds)
```powershell
locust -f load_test.py --headless -u 5 -r 1 -t 10s --host https://reqres.in
```

#### Option 2: Interactive Web UI Mode
```powershell
locust -f load_test.py --host https://reqres.in
```
Then open your browser and navigate to: **`http://localhost:8089`**  
- Number of users: `5` to `10`
- Spawn rate: `1`
- Host: `https://reqres.in`
- Click **"Start Swarming"**.

---

## Locust Load Test Plan & Recorded Results

### Test Plan

| Parameter | Configuration | Description |
| :--- | :--- | :--- |
| **Target Host** | `https://reqres.in` | Public RESTful API |
| **Simulated Users** | 5 concurrent virtual users | Generates realistic concurrent traffic |
| **Ramp-Up (Spawn Rate)** | 1 user/second | Smooth, incremental ramp-up |
| **Test Duration** | 10 seconds | Keeps total requests safely capped |
| **User Pacing** | `between(1.0, 2.5)` seconds | Emulates human thinking/browsing pauses |
| **Request Mix** | 75% User List (`/api/users?page=2`), 25% Single User (`/api/users/2`) | Weighted `@task(3)` vs `@task(1)` |
| **Safety Threshold** | Capped at `< 60` total calls | Strictly adheres to assignment's < 100 API limit |

### Recorded Benchmark Results

```text
Type     Name                  # reqs   # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|--------------------|--------|---------|-------|-------|-------|-------|--------|-----------
GET      /api/users/2               7   0(0.00%) |    221     153     323    190 |    0.96        0.00
GET      /api/users?page=2         10   0(0.00%) |    317     149    1062    180 |    1.37        0.00
--------|--------------------|--------|---------|-------|-------|-------|-------|--------|-----------
         Aggregated                17   0(0.00%) |    277     149    1062    180 |    2.32        0.00

Response Time Percentiles:
- 50th Percentile (Median): 180 ms
- 75th Percentile: 320 ms
- 90th Percentile: 400 ms
- 95th Percentile: 1100 ms
- Failure Rate: 0.00% (100% Success)
```

---

## Interview Preparation Guide & Technical Explanations

When explaining this project in your technical interview, structure your answers around these **core QA engineering concepts**:

### 1. Framework Architecture & Page Object Model (POM)
- **Question**: *"Why did you use the Page Object Model instead of putting element locators directly in the test functions?"*
- **Answer**: 
  > *"I adopted the Page Object Model (POM) pattern to establish a clean separation of concerns. In POM, each web page is modeled as a Python class (`HomePage`, `BookDemoPage`) that encapsulates its locators and user actions. The tests (`ui_tests.py`) interact only with page methods, making tests read like business requirements. If a frontend designer renames a button class or changes an input ID tomorrow, I only update one locator in `pages/book_demo_page.py`, and all test cases continue to work without modification."*

### 2. Handling Synchronization: Explicit vs. Implicit Waits
- **Question**: *"How did you prevent flakiness and handle asynchronous loading?"*
- **Answer**:
  > *"I avoided brittle hardcoded sleeps (`time.sleep()`). In `pages/base_page.py`, I implemented explicit dynamic synchronization using `WebDriverWait` paired with `expected_conditions` (such as `visibility_of_element_located` and `element_to_be_clickable`). Explicit waits poll the DOM at 500ms intervals and proceed the millisecond the condition is satisfied, making test execution both lightning-fast and resilient against variable network latency."*

### 3. Lifecycle Management & Teardown
- **Question**: *"How did you handle setup and teardown?"*
- **Answer**:
  > *"Using Pytest fixtures with `yield` in `conftest.py`. For API tests, `api_session` initializes a persistent `requests.Session()` with default headers, yields it for execution, and closes the connection pool upon completion. For UI tests, the `driver` fixture configures Chrome with options (`--headless=new`, window size 1920x1080, `--no-sandbox`), yields the driver to the tests, and executes `driver.quit()` in a protected `finally`/teardown block to ensure background browser processes are never orphaned."*

### 4. API Error Handling & Negative Testing
- **Question**: *"What negative scenarios did you validate in the API suite?"*
- **Answer**:
  > *"A robust test suite must validate how systems fail, not just happy paths. I implemented two explicit negative test cases:
  > 1. `GET /api/users/23` to test non-existent resources: validating HTTP `404 Not Found` and empty response bodies.
  > 2. `POST /api/register` with an omitted required password parameter: validating that the API properly rejects malformed payloads with HTTP `400 Bad Request` and returns an informative error message: `{'error': 'Missing password'}`."*

### 5. Real-World Engineering: Handling Live Site Rate-Limiting & CI/CD Readiness
- **Question**: *"How did you address the risk of testing against a live third-party marketing site (`iamdave.ai`)?"*
- **Answer**:
  > *"Testing against public, production marketing sites presents real-world risks: external IP rate limiting, WAF throttling (e.g. AWS or Cloudflare), and TLS handshake stalls. To address this like a senior automation engineer:
  > 1. I scoped the UI driver fixture to `class`, executing the user journey across a single browser session rather than triggering 4 separate cold TCP connections.
  > 2. I designed the framework with an environment configuration layer (`config/config.py`) allowing `DAVE_AI_BASE_URL` to be overridden.
  > 3. I implemented an optional local mock staging server (`--mock`) containing the exact HTML DOM structure of DaveAI. This allows automated CI/CD pipelines to run deterministically in seconds even offline or behind enterprise proxies without external dependencies."*

### 6. Performance Testing & Resource Protection
- **Question**: *"How did you design the Locust load test?"*
- **Answer**:
  > *"I simulated 5 concurrent users with realistic user pacing (`between(1.0, 2.5)` seconds) and weighted requests (`@task(3)` for browsing user lists vs `@task(1)` for single-user lookups). To strictly observe the assignment's rule of capping requests below 100 per day, I implemented an `@events.request.add_listener` event hook in `load_test.py` that tracks total requests and halts the test once 60 calls are reached, preventing accidental API blacklisting."*
