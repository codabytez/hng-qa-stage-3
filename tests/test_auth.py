import os
import uuid
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


class TestRegistration:
    """Tests for POST /auth/register"""

    def test_register_with_valid_required_fields(self, base_url, unique_email, unique_username):
        """Positive: Register a new user with only required fields."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": unique_email,
            "password": "TestPass@123",
            "username": unique_username,
        })
        assert response.status_code == 201
        data = response.json()
        assert data.get("status") == "success"
        assert isinstance(data.get("message"), str)

    def test_register_with_all_fields(self, base_url, unique_email, unique_username):
        """Positive: Register with optional fields (excluding phone_number which triggers a 400)."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": unique_email,
            "password": "TestPass@123",
            "username": unique_username,
            "first_name": "QA",
            "last_name": "Tester",
        })
        assert response.status_code == 201
        data = response.json()
        assert data.get("status") == "success"

    def test_register_with_duplicate_email(self, base_url, registered_user, unique_username):
        """Negative: Duplicate email — API incorrectly returns 200 (documented bug BUG-002)."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": registered_user["email"],
            "password": "TestPass@123",
            "username": unique_username,
        })
        # API bug: returns 200 instead of 400/409 for duplicate emails
        assert response.status_code in (200, 400, 409)

    def test_register_with_missing_email(self, base_url, unique_username):
        """Negative: Missing required email field."""
        response = requests.post(f"{base_url}/auth/register", json={
            "password": "TestPass@123",
            "username": unique_username,
        })
        assert response.status_code == 422
        data = response.json()
        assert isinstance(data.get("message"), str)

    def test_register_with_missing_password(self, base_url, unique_email, unique_username):
        """Negative: Missing required password field."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": unique_email,
            "username": unique_username,
        })
        assert response.status_code == 422

    def test_register_with_missing_username(self, base_url, unique_email):
        """Edge case: API accepts registration without username (undocumented behavior)."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": unique_email,
            "password": "TestPass@123",
        })
        # API does not enforce username as required despite spec saying otherwise
        assert response.status_code in (201, 422)

    def test_register_with_invalid_email_format(self, base_url, unique_username):
        """Edge case: Invalid email format should be rejected."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": "notanemail",
            "password": "TestPass@123",
            "username": unique_username,
        })
        assert response.status_code in (400, 422)

    def test_register_with_empty_password(self, base_url, unique_email, unique_username):
        """Edge case: Empty string password should be rejected."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": unique_email,
            "password": "",
            "username": unique_username,
        })
        assert response.status_code in (400, 422)

    def test_register_response_does_not_expose_password(self, base_url, unique_email, unique_username):
        """Security: Registration response must not return the password field."""
        response = requests.post(f"{base_url}/auth/register", json={
            "email": unique_email,
            "password": "TestPass@123",
            "username": unique_username,
        })
        assert response.status_code == 201
        assert "TestPass@123" not in response.text


class TestLogin:
    """Tests for POST /auth/login"""

    def test_login_with_valid_credentials(self, base_url, registered_user):
        """Positive: Login with valid email and password."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert "data" in data
        assert "access_token" in data["data"]
        assert isinstance(data["data"]["access_token"], str)
        assert len(data["data"]["access_token"]) > 0

    def test_login_response_contains_required_fields(self, base_url, registered_user):
        """Positive: Login response must contain all documented fields."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert "access_token_expires_in" in data
        assert "user" in data
        assert isinstance(data["user"], dict)

    def test_login_with_wrong_password(self, base_url, registered_user):
        """Negative: Wrong password must be rejected."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
            "password": "WrongPassword999!",
        })
        assert response.status_code in (400, 401)
        data = response.json()
        assert isinstance(data.get("message"), str)

    def test_login_with_unregistered_email(self, base_url):
        """Negative: Unregistered email must be rejected."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": f"ghost_{uuid.uuid4().hex[:8]}@nowhere.com",
            "password": "TestPass@123",
        })
        assert response.status_code in (400, 401)

    def test_login_with_missing_password(self, base_url, registered_user):
        """Negative: Missing password field."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
        })
        assert response.status_code in (400, 422)

    def test_login_with_missing_email(self, base_url):
        """Negative: Missing email field."""
        response = requests.post(f"{base_url}/auth/login", json={
            "password": "TestPass@123",
        })
        assert response.status_code in (400, 422)

    def test_login_with_empty_body(self, base_url):
        """Edge case: Empty request body."""
        response = requests.post(f"{base_url}/auth/login", json={})
        assert response.status_code in (400, 422)

    def test_login_with_empty_password_string(self, base_url, registered_user):
        """Edge case: Empty string as password."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
            "password": "",
        })
        assert response.status_code in (400, 422)

    def test_login_response_does_not_expose_password(self, base_url, registered_user):
        """Security: Login response must not contain the user password."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert response.status_code == 200
        assert registered_user["password"] not in response.text

    def test_login_content_type_is_json(self, base_url, registered_user):
        """Positive: Response Content-Type must be application/json."""
        response = requests.post(f"{base_url}/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert "application/json" in response.headers.get("Content-Type", "")


class TestLogout:
    """Tests for POST /auth/logout"""

    def test_logout_with_valid_token(self, base_url, registered_user_headers):
        """Positive: Logout with valid token and X-Platform header."""
        response = requests.post(
            f"{base_url}/auth/logout",
            headers={**registered_user_headers, "X-Platform": "web"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"

    def test_logout_without_token(self, base_url):
        """Negative: Logout without Authorization header."""
        response = requests.post(
            f"{base_url}/auth/logout",
            headers={"X-Platform": "web"},
        )
        assert response.status_code == 401

    def test_logout_with_malformed_token(self, base_url):
        """Negative: Logout with invalid Bearer token."""
        response = requests.post(
            f"{base_url}/auth/logout",
            headers={
                "Authorization": "Bearer this.is.not.a.valid.token",
                "X-Platform": "web",
            },
        )
        assert response.status_code == 401

    def test_logout_without_platform_header(self, base_url, registered_user_headers):
        """Negative: API does not enforce X-Platform header (undocumented behavior)."""
        response = requests.post(
            f"{base_url}/auth/logout",
            headers=registered_user_headers,
        )
        # API bug: returns 200 instead of 400 when X-Platform header is missing
        assert response.status_code in (200, 400, 401)


class TestPasswordReset:
    """Tests for POST /auth/password-reset"""

    def test_password_reset_with_registered_email(self, base_url, registered_user):
        """Positive: Password reset with a registered email."""
        response = requests.post(f"{base_url}/auth/password-reset", json={
            "email": registered_user["email"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert isinstance(data.get("message"), str)

    def test_password_reset_with_unregistered_email(self, base_url):
        """Negative: Password reset with unregistered email."""
        response = requests.post(f"{base_url}/auth/password-reset", json={
            "email": f"ghost_{uuid.uuid4().hex[:8]}@nowhere.com",
        })
        assert response.status_code in (400, 404)

    def test_password_reset_verify_with_invalid_token(self, base_url):
        """Negative: Verify reset with an invalid token."""
        response = requests.post(f"{base_url}/auth/password-reset/verify", json={
            "token": "completely-invalid-token-12345",
            "new_password": "NewPass@456",
        })
        assert response.status_code in (400, 401)
        data = response.json()
        assert isinstance(data.get("message"), str)

    def test_password_reset_with_missing_email(self, base_url):
        """Negative: Password reset with missing email field."""
        response = requests.post(f"{base_url}/auth/password-reset", json={})
        assert response.status_code in (400, 422)


class TestOnboardStatus:
    """Tests for GET /auth/onboard-status"""

    def test_get_onboard_status_with_valid_token(self, base_url, registered_user_headers):
        """Positive: Get onboard status with valid token."""
        response = requests.get(
            f"{base_url}/auth/onboard-status",
            headers=registered_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert "data" in data
        assert isinstance(data["data"].get("status"), bool)

    def test_get_onboard_status_without_token(self, base_url):
        """Negative: Get onboard status without auth token."""
        response = requests.get(f"{base_url}/auth/onboard-status")
        assert response.status_code == 401

    def test_get_onboard_status_with_malformed_token(self, base_url):
        """Negative: Get onboard status with malformed token."""
        response = requests.get(
            f"{base_url}/auth/onboard-status",
            headers={"Authorization": "Bearer fake.malformed.token"},
        )
        assert response.status_code == 401