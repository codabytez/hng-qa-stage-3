import os
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


def get_auth_token(email: Optional[str] = None, password: Optional[str] = None) -> str:
    """
    Login with provided or default credentials and return the access token.
    Raises an exception if login fails.
    """
    email = email or TEST_EMAIL
    password = password or TEST_PASSWORD

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200, (
        f"Login failed with status {response.status_code}: {response.text}"
    )

    data = response.json()
    token = data.get("data", {}).get("access_token")

    assert token, "No access_token in login response"
    return token


def get_auth_headers(email: Optional[str] = None, password: Optional[str] = None) -> dict:
    """
    Return Authorization headers for authenticated requests.
    """
    token = get_auth_token(email, password)
    return {"Authorization": f"Bearer {token}"}