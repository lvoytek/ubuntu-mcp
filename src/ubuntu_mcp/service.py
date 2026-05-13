"""Shared QueryService lifecycle management for MCP servers."""

import sys
from pathlib import Path

from launchpadlib.launchpad import Launchpad  # type: ignore[import-untyped]
from ubq import QueryService
from ubq.models import ProviderCredentials
from ubq.providers.session import ProviderSession

_service: QueryService | None = None
_verbose: bool = False

DEFAULT_CREDENTIAL_FILE = Path(
    "~/.config/ubq/launchpad-credentials"
).expanduser()


def set_verbose(enabled: bool) -> None:
    """Enable or disable verbose logging of ubq API calls."""
    global _verbose  # noqa: PLW0603
    _verbose = enabled


def get_service() -> QueryService:
    """Return the singleton QueryService, creating it on first call."""
    global _service  # noqa: PLW0603
    if _service is None:
        svc = QueryService()
        _service = _VerboseQueryService(svc) if _verbose else svc
    return _service


def reset_service() -> None:
    """Reset the singleton for testing."""
    global _service  # noqa: PLW0603
    _service = None


def login(
    provider_name: str,
    username: str | None = None,
    token: str | None = None,
    credential_file: str | None = None,
) -> str:
    """Authenticate with a provider and cache the session.

    For Launchpad: provide a token directly, a credential file path
    containing the token, or omit all credentials to authenticate
    anonymously.

    Returns a confirmation message with active session info.
    """
    svc = get_service()
    credentials = _resolve_credentials(provider_name, username, token, credential_file)
    if isinstance(credentials, str):
        return credentials

    if credentials is None and provider_name.lower() == "launchpad":
        try:
            _login_launchpad_anonymous(svc)
        except Exception as exc:
            return f"Authentication failed: {exc}"
    else:
        try:
            svc.login(provider_name=provider_name, credentials=credentials)
        except ValueError as exc:
            return f"Authentication failed: {exc}"

    sessions = ", ".join(svc.available_providers())
    return f"Authenticated with '{provider_name}'. Active sessions: {sessions}"


def _resolve_credentials(
    provider_name: str,
    username: str | None,
    token: str | None,
    credential_file: str | None,
) -> ProviderCredentials | None | str:
    """Resolve credentials from the given parameters.

    Returns ProviderCredentials if credentials were found, None if no
    credentials were provided (anonymous auth), or a str error message
    if a credential file was specified but does not exist.
    """
    if token is not None or username is not None:
        return ProviderCredentials(username=username, token=token)

    if credential_file is not None:
        cred_path = Path(credential_file).expanduser()
        if not cred_path.is_file():
            return f"Authentication failed: credential file not found: {cred_path}"
        return ProviderCredentials(token=cred_path.read_text().strip())

    if provider_name.lower() == "launchpad" and DEFAULT_CREDENTIAL_FILE.is_file():
        return ProviderCredentials(
            token=DEFAULT_CREDENTIAL_FILE.read_text().strip()
        )

    return None


def _login_launchpad_anonymous(svc: QueryService) -> None:
    """Create an anonymous Launchpad session and inject it into the registry.

    This bypasses LaunchpadProvider.authenticate(), which would call
    Launchpad.login_with() and block on keyring/desktop OAuth in
    headless environments.
    """
    lp = Launchpad.login_anonymously(
        consumer_name="ubq",
        service_root="production",
        version="devel",
    )

    registry = svc._registry
    providers = registry._get_providers("launchpad")

    for provider in providers:
        provider.set_session_object(lp)

    session = ProviderSession(
        provider_name="launchpad",
        session_object=lp,
    )
    for provider in providers:
        session = session.with_provider(provider)

    registry._sessions["launchpad"] = session


def list_providers() -> list[str]:
    """Return all available provider names."""
    return list(get_service().available_providers())


def list_active_sessions() -> list[str]:
    """Return names of providers with active sessions."""
    return list(get_service()._registry.active_sessions())


class _VerboseQueryService:
    """Wrapper that logs all ubq API calls before delegating to the real service."""

    def __init__(self, service: QueryService) -> None:
        self._service = service

    def _log(self, method_name: str, **kwargs) -> None:
        args_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        print(f"ubq API call: {method_name}({args_str})", file=sys.stderr)

    def login(self, **kwargs):
        self._log("login", **kwargs)
        return self._service.login(**kwargs)

    def available_providers(self):
        self._log("available_providers")
        return self._service.available_providers()

    def get_bug(self, **kwargs):
        self._log("get_bug", **kwargs)
        return self._service.get_bug(**kwargs)

    def search_bugs(self, **kwargs):
        self._log("search_bugs", **kwargs)
        return self._service.search_bugs(**kwargs)

    def submit_bug(self, **kwargs):
        self._log("submit_bug", **kwargs)
        return self._service.submit_bug(**kwargs)

    def get_package(self, **kwargs):
        self._log("get_package", **kwargs)
        return self._service.get_package(**kwargs)

    def get_version(self, **kwargs):
        self._log("get_version", **kwargs)
        return self._service.get_version(**kwargs)

    def get_merge_request(self, **kwargs):
        self._log("get_merge_request", **kwargs)
        return self._service.get_merge_request(**kwargs)

    def get_merge_requests_from_user(self, **kwargs):
        self._log("get_merge_requests_from_user", **kwargs)
        return self._service.get_merge_requests_from_user(**kwargs)

    @property
    def _registry(self):
        return self._service._registry
