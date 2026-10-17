import unittest
from unittest.mock import Mock, call, patch

from app.services.google_oauth import build_authorization_url, fetch_google_user


class GoogleOAuthServiceTests(unittest.TestCase):
    @patch("app.services.google_oauth.requests.get")
    @patch("app.services.google_oauth.requests.post")
    def test_authorization_url_and_userinfo_exchange(self, post, get):
        token_response = Mock()
        token_response.json.return_value = {"access_token": "access-token"}
        post.return_value = token_response
        user_response = Mock()
        user_response.json.return_value = {
            "sub": "google-subject",
            "email": "user@example.com",
            "email_verified": True,
        }
        get.return_value = user_response

        url = build_authorization_url("client-id", "https://example.com/auth/callback", "csrf-state")
        self.assertIn("accounts.google.com/o/oauth2/v2/auth", url)
        self.assertIn("state=csrf-state", url)

        user = fetch_google_user(
            "auth-code", "client-id", "client-secret", "https://example.com/auth/callback"
        )
        self.assertEqual(user["sub"], "google-subject")
        self.assertEqual(post.call_args, call(
            "https://oauth2.googleapis.com/token",
            data={
                "code": "auth-code",
                "client_id": "client-id",
                "client_secret": "client-secret",
                "redirect_uri": "https://example.com/auth/callback",
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
            timeout=20,
        ))
        self.assertEqual(get.call_args.kwargs["headers"]["Authorization"], "Bearer access-token")

    @patch("app.services.google_oauth.requests.get")
    @patch("app.services.google_oauth.requests.post")
    def test_rejects_unverified_google_email(self, post, get):
        token_response = Mock()
        token_response.json.return_value = {"access_token": "access-token"}
        post.return_value = token_response
        user_response = Mock()
        user_response.json.return_value = {
            "sub": "google-subject",
            "email": "user@example.com",
            "email_verified": False,
        }
        get.return_value = user_response

        with self.assertRaises(ValueError):
            fetch_google_user("auth-code", "client-id", "secret", "https://example.com/callback")


if __name__ == "__main__":
    unittest.main()
