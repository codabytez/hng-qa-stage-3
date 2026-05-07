# Zedu API Automation — HNG QA Stage 3

![CI](https://github.com/codabytez/hng-qa-stage-3/actions/workflows/ci.yml/badge.svg)

Structured API automation project testing the Zedu platform backend using Python and Pytest

## Project Overview

This project contains 48 automated test cases covering authentication, user management, and organisation endpoints of the Zedu API. Tests are organized by endpoint group, fully independent, idempotent, and use dynamically generated test data.

## CI Pipeline

This project uses GitHub Actions for continuous integration.

The pipeline triggers on every push and pull request and:

1. Sets up Python 3.11
2. Installs all dependencies from requirements.txt
3. Creates the .env file from GitHub Secrets
4. Runs the full test suite with pytest
5. Uploads JUnit XML results as an artifact
6. Fails the build if any test fails

Environment variables used: `BASE_URL`, `TEST_EMAIL`, `TEST_PASSWORD` — stored as GitHub repository secrets.

## Prerequisites

- Python 3.11+
- pip

## Setup Instructions

### 1. Clone the repository

    git clone https://github.com/codabytez/hng-qa-stage-3.git
    cd hng-qa-stage-3

### 2. Create and activate virtual environment

    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Set up environment variables

Copy the example env file and fill in your credentials:

    cp .env.example .env

Your `.env` file should contain:

    BASE_URL=https://api.zedu.chat/api/v1
    TEST_EMAIL=your_email@example.com
    TEST_PASSWORD=your_password

## Running the Tests

Run the full test suite:

    pytest tests/ -v

Run a specific test file:

    pytest tests/test_auth.py -v

Run with HTML report:

    pytest tests/ -v --html=report.html

Run with JUnit XML report:

    pytest tests/ -v --junitxml=report.xml

## Test File Coverage

| File                          | Description                                                                                                                                    |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/test_auth.py`          | 30 tests covering registration, login, logout, password reset, and onboard status. Includes positive, negative, edge case, and security tests. |
| `tests/test_organisations.py` | 8 tests covering organisation creation and retrieval. Includes auth protection, missing fields, and invalid UUID edge cases.                   |
| `tests/test_users.py`         | 10 tests covering onboard status, magic link flow, and email verification.                                                                     |

## Authentication Handling

All authentication tokens are obtained dynamically at runtime via `utils/auth.py`. The `get_auth_token()` function logs in and extracts the Bearer token programmatically. No tokens are hardcoded anywhere in the codebase. Shared fixtures in `conftest.py` handle token reuse across tests.

## Test Data Strategy

- Unique emails and usernames are generated per test using `uuid.uuid4()`
- Each test that needs a user creates a fresh one via the `registered_user` fixture
- Tests are fully idempotent — safe to run multiple times without state conflicts

## Key Findings During Testing

Several API behaviors differed from the Swagger documentation:

- Duplicate email registration returns 200 instead of 400
- Missing username field does not return 422 as documented
- Missing X-Platform header on logout does not return 400 as documented
- Non-existent organisation ID returns 200 instead of 404
- phone_number field in registration triggers an unexpected 400

These are documented in test comments with references to the spec.

## Dependencies

See `requirements.txt` for pinned versions.
