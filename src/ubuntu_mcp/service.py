"""Shared QueryService lifecycle management for MCP servers."""

from ubq import QueryService
from ubq.models import ProviderCredentials

_service: QueryService | None = None


def get_service() -> QueryService:
    """Return the singleton QueryService, creating it on first call."""
    global _service  # noqa: PLW0603
    if _service is None:
        _service = QueryService()
    return _service


def reset_service() -> None:
    """Reset the singleton for testing."""
    global _service  # noqa: PLW0603
    _service = None


def login(
    provider_name: str,
    username: str | None = None,
    token: str | None = None,
) -> str:
    """Authenticate with a provider and cache the session.

    Returns a confirmation message with active session info.
    """
    svc = get_service()
    credentials = None
    if username is not None or token is not None:
        credentials = ProviderCredentials(username=username, token=token)

    try:
        svc.login(provider_name=provider_name, credentials=credentials)
    except ValueError as exc:
        return f"Authentication failed: {exc}"

    sessions = ", ".join(svc.available_providers())
    return f"Authenticated with '{provider_name}'. Active sessions: {sessions}"


def list_providers() -> list[str]:
    """Return all available provider names."""
    return list(get_service().available_providers())


def list_active_sessions() -> list[str]:
    """Return names of providers with active sessions."""
    return list(get_service()._registry.active_sessions())
