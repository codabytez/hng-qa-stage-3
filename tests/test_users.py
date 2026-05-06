import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


class TestUsers:
    """Tests for user-related endpoints."""

    def test_get_onboard_status_returns_boolean(self, base_url, registered_user_headers):
        """Positive: Onboard status data.status must be a boolean."""
        response = requests.get(
            f"{base_url}/auth/onboard-status",
            headers=registered_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"]["status"], bool)

    def test_update_onboard_status_with_valid_token(self, base_url, registered_user_headers):
        """Positive: Update onboard status with valid token."""
        response = requests.put(
            f"{base_url}/auth/onboard-status",
            headers=registered_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"

    def test_update_onboard_status_without_token(self, base_url):
        """Negative: Update onboard status without auth token."""
        response = requests.put(f"{base_url}/auth/onboard-status")
        assert response.status_code == 401

    def test_magic_link_request_with_valid_email(self, base_url, registered_user):
        """Positive: Request magic link with a registered email."""
        response = requests.post(
            f"{base_url}/auth/magick-link",
            json={"email": registered_user["email"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert isinstance(data.get("message"), str)

    def test_magic_link_request_with_invalid_email_format(self, base_url):
        """Edge case: Magic link with invalid email format."""
        response = requests.post(
            f"{base_url}/auth/magick-link",
            json={"email": "notanemail"},
        )
        assert response.status_code in (400, 422)

    def test_magic_link_request_with_missing_email(self, base_url):
        """Negative: Magic link request without email field."""
        response = requests.post(
            f"{base_url}/auth/magick-link",
            json={},
        )
        assert response.status_code in (400, 422)

    def test_magic_link_verify_with_invalid_token(self, base_url):
        """Negative: Verify magic link with invalid token."""
        response = requests.post(
            f"{base_url}/auth/magick-link/verify",
            json={"token": "fake-magic-token-99999"},
        )
        assert response.status_code in (400, 401)
        data = response.json()
        assert isinstance(data.get("message"), str)

    def test_magic_link_verify_with_missing_token(self, base_url):
        """Negative: Verify magic link without token field."""
        response = requests.post(
            f"{base_url}/auth/magick-link/verify",
            json={},
        )
        assert response.status_code in (400, 422)

    def test_email_verification_request_with_registered_email(self, base_url, registered_user):
        """Positive: Request email verification with registered email."""
        response = requests.post(
            f"{base_url}/auth/email-request",
            json={"email": registered_user["email"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"

    def test_email_verification_request_with_missing_email(self, base_url):
        """Negative: Email verification request without email field."""
        response = requests.post(
            f"{base_url}/auth/email-request",
            json={},
        )
        assert response.status_code in (400, 422)