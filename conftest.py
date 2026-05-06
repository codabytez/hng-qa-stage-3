import os
import uuid
import pytest
import requests
from dotenv import load_dotenv
from utils.auth import get_auth_token, get_auth_headers

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token():
    """Session-scoped token — logs in once and reuses across all tests."""
    return get_auth_token()


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Session-scoped auth headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def unique_email():
    """Generate a unique email for each test that needs registration."""
    return f"qa_test_{uuid.uuid4().hex[:8]}@zedutest.com"


@pytest.fixture
def unique_username():
    """Generate a unique username for each test."""
    return f"qauser_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def registered_user(base_url, unique_email, unique_username):
    """
    Register a fresh user and return their credentials.
    Each test that uses this gets a brand new user.
    """
    payload = {
        "email": unique_email,
        "username": unique_username,
        "password": "TestPass@123",
        "first_name": "QA",
        "last_name": "Tester",
    }
    response = requests.post(f"{base_url}/auth/register", json=payload)
    assert response.status_code == 201, (
        f"Test setup failed — could not register user: {response.text}"
    )
    return {
        "email": unique_email,
        "username": unique_username,
        "password": "TestPass@123",
    }


@pytest.fixture
def registered_user_token(base_url, registered_user):
    """Register a fresh user and return their auth token."""
    return get_auth_token(
        email=registered_user["email"],
        password=registered_user["password"],
    )


@pytest.fixture
def registered_user_headers(registered_user_token):
    """Return auth headers for a freshly registered user."""
    return {"Authorization": f"Bearer {registered_user_token}"}