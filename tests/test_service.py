"""Tests for the shared service module."""

from pathlib import Path
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

    def test_login_with_credential_file(self, tmp_path):
        cred_file = tmp_path / "creds"
        cred_file.write_text("my-token-value")
        mock_svc = MagicMock()
        mock_svc.available_providers.return_value = ("launchpad",)
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = login(
                provider_name="launchpad",
                credential_file=str(cred_file),
            )
            call_kwargs = mock_svc.login.call_args
            assert call_kwargs.kwargs["credentials"].token == "my-token-value"
            assert "Authenticated" in result

    def test_login_with_missing_credential_file(self):
        mock_svc = MagicMock()
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ):
            result = login(
                provider_name="launchpad",
                credential_file="/nonexistent/path/creds",
            )
            assert "credential file not found" in result
            mock_svc.login.assert_not_called()

    def test_login_launchpad_default_credential_file(self):
        mock_svc = MagicMock()
        mock_svc.available_providers.return_value = ("launchpad",)
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ), patch.object(Path, "is_file", return_value=True), patch.object(
            Path, "read_text", return_value="default-token\n"
        ):
            login(provider_name="launchpad")
            call_kwargs = mock_svc.login.call_args
            assert call_kwargs.kwargs["credentials"].token == "default-token"

    def test_login_launchpad_no_credentials_anonymous(self):
        mock_svc = MagicMock()
        mock_svc.available_providers.return_value = ("launchpad",)
        mock_lp = MagicMock()
        mock_providers = [MagicMock()]
        mock_svc._registry._get_providers.return_value = mock_providers
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ), patch.object(Path, "is_file", return_value=False), patch(
            "ubuntu_mcp.service.Launchpad"
        ) as mock_launchpad_cls:
            mock_launchpad_cls.login_anonymously.return_value = mock_lp
            result = login(provider_name="launchpad")
            mock_launchpad_cls.login_anonymously.assert_called_once_with(
                consumer_name="ubq",
                service_root="production",
                version="devel",
            )
            mock_svc.login.assert_not_called()
            assert "Authenticated" in result

    def test_login_launchpad_anonymous_failure(self):
        mock_svc = MagicMock()
        with patch(
            "ubuntu_mcp.service.get_service",
            return_value=mock_svc,
        ), patch.object(Path, "is_file", return_value=False), patch(
            "ubuntu_mcp.service.Launchpad"
        ) as mock_launchpad_cls:
            mock_launchpad_cls.login_anonymously.side_effect = RuntimeError(
                "network error"
            )
            result = login(provider_name="launchpad")
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
