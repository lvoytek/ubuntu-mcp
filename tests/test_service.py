"""Tests for the shared service module."""

from unittest.mock import MagicMock, patch

from ubuntu_mcp.service import (
    get_service,
    list_active_sessions,
    list_providers,
    login,
    reset_service,
)


class TestGetService:
    def test_creates_singleton(self):
        reset_service()
        with patch("ubuntu_mcp.service.QueryService"):
            svc1 = get_service()
            svc2 = get_service()
            assert svc1 is svc2

    def test_returns_same_instance(self):
        reset_service()
        with patch("ubuntu_mcp.service.QueryService"):
            svc1 = get_service()
            svc2 = get_service()
            assert svc1 is svc2


class TestLogin:
    def test_login_success(self):
        mock_svc = MagicMock()
        mock_svc.available_providers.return_value = ("launchpad",)
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = login(provider_name="launchpad")
            mock_svc.login.assert_called_once_with(
                provider_name="launchpad",
                credentials=None,
            )
            assert "Authenticated" in result

    def test_login_with_credentials(self):
        mock_svc = MagicMock()
        mock_svc.available_providers.return_value = ("github",)
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = login(
                provider_name="github",
                username="user",
                token="tok",
            )
            mock_svc.login.assert_called_once()
            assert "Authenticated" in result

    def test_login_failure(self):
        mock_svc = MagicMock()
        mock_svc.login.side_effect = ValueError("Unknown provider 'bad'")
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = login(provider_name="bad")
            assert "Authentication failed" in result


class TestListProviders:
    def test_returns_providers(self):
        mock_svc = MagicMock()
        mock_svc.available_providers.return_value = (
            "github",
            "launchpad",
            "snapcraft",
        )
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = list_providers()
            assert result == [
                "github",
                "launchpad",
                "snapcraft",
            ]


class TestListActiveSessions:
    def test_returns_sessions(self):
        mock_svc = MagicMock()
        mock_svc._registry.active_sessions.return_value = ("launchpad",)
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = list_active_sessions()
            assert result == ["launchpad"]
