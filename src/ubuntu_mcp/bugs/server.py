"""MCP server for Ubuntu bug data via ubq."""

from datetime import datetime

from mcp.server.fastmcp import FastMCP
from ubq.models import BugSearchRecord, BugSubmissionRecord, UserRecord

from ubuntu_mcp.cli import run_server
from ubuntu_mcp.service import (
    get_service,
    list_active_sessions,
    list_providers,
    login,
)

mcp = FastMCP("ubuntu-mcp-bugs")


@mcp.tool()
def login_provider(
    provider_name: str,
    username: str | None = None,
    token: str | None = None,
) -> str:
    """Authenticate with a bug data provider (e.g. 'launchpad', 'github').

    For providers supporting keyring auth (like Launchpad), username
    and token can be omitted to use system-stored credentials.
    """
    return login(
        provider_name=provider_name,
        username=username,
        token=token,
    )


@mcp.tool()
def list_bug_providers() -> list[str]:
    """List all available bug data provider names."""
    return list_providers()


@mcp.tool()
def get_bug(
    bug_id: str,
    provider_name: str,
    metadata_only: bool = False,
) -> dict | None:
    """Fetch a bug by ID from the given provider.

    Set metadata_only to True to skip fetching comments and tasks.
    """
    svc = get_service()
    try:
        record = svc.get_bug(
            bug_id=bug_id,
            provider_name=provider_name,
            metadata_only=metadata_only,
        )
    except ValueError as exc:
        return {"error": str(exc)}

    if record is None:
        return None

    return _bug_record_to_dict(record)


@mcp.tool()
def search_bugs(  # noqa: PLR0913
    provider_name: str,
    title: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
    importance: str | None = None,
    owner: str | None = None,
    assignee: str | None = None,
    milestone: str | None = None,
    created_since: str | None = None,
    created_before: str | None = None,
    modified_since: str | None = None,
) -> list[dict]:
    """Search for bugs matching criteria on the given provider.

    Date arguments should be ISO 8601 format (e.g. '2025-01-01').
    """
    svc = get_service()

    owner_record = UserRecord(username=owner) if owner else None
    assignee_record = UserRecord(username=assignee) if assignee else None

    query = BugSearchRecord(
        provider_name=provider_name,
        title=title,
        tags=tags or [],
        status=status,
        importance=importance,
        owner=owner_record,
        assignee=assignee_record,
        milestone=milestone,
        created_since=_parse_datetime(created_since),
        created_before=_parse_datetime(created_before),
        modified_since=_parse_datetime(modified_since),
    )

    try:
        results = svc.search_bugs(query=query, provider_name=provider_name)
    except ValueError as exc:
        return [{"error": str(exc)}]

    return [_bug_record_to_dict(r) for r in results]


@mcp.tool()
def submit_bug(  # noqa: PLR0913
    title: str,
    provider_name: str,
    package_names: list[str] | None = None,
    description: str | None = None,
    importance: str | None = None,
    status: str | None = None,
    tags: list[str] | None = None,
    assignee: str | None = None,
    private: bool = False,
    milestone: str | None = None,
) -> dict | None:
    """Submit a new bug to the given provider.

    Returns the created bug record, or None on failure.
    """
    svc = get_service()

    assignee_record = UserRecord(username=assignee) if assignee else None

    submission = BugSubmissionRecord(
        provider_name=provider_name,
        title=title,
        package_names=package_names or [],
        description=description,
        importance=importance,
        status=status,
        tags=tags or [],
        assignee=assignee_record,
        private=private,
        milestone=milestone,
    )

    try:
        record = svc.submit_bug(submission=submission, provider_name=provider_name)
    except ValueError as exc:
        return {"error": str(exc)}

    if record is None:
        return None

    return _bug_record_to_dict(record)


@mcp.resource("ubq://bugs/providers")
def bugs_providers_resource() -> str:
    """Available bug data providers."""
    return "\n".join(list_providers())


@mcp.resource("ubq://bugs/sessions")
def bugs_sessions_resource() -> str:
    """Active bug data provider sessions."""
    sessions = list_active_sessions()
    return "\n".join(sessions) if sessions else "No active sessions"


def _bug_record_to_dict(record) -> dict:
    return {
        "provider_name": record.provider_name,
        "id": record.id,
        "title": record.title,
        "description": record.description,
        "tags": record.tags,
        "created_at": _fmt_dt(record.created_at),
        "updated_at": _fmt_dt(record.updated_at),
        "last_message_at": _fmt_dt(record.last_message_at),
        "owner": _user_to_dict(record.owner),
        "assignee": _user_to_dict(record.assignee),
        "bug_tasks": [_task_to_dict(t) for t in record.bug_tasks],
        "comments": [_comment_to_dict(c) for c in record.comments],
    }


def _task_to_dict(task) -> dict:
    return {
        "title": task.title,
        "target": task.target,
        "importance": task.importance,
        "status": task.status,
        "milestone": task.milestone,
        "owner": _user_to_dict(task.owner),
        "assignee": _user_to_dict(task.assignee),
    }


def _comment_to_dict(comment) -> dict:
    return {
        "author": _user_to_dict(comment.author),
        "content": comment.content,
        "created_at": _fmt_dt(comment.created_at),
        "edited_at": _fmt_dt(comment.edited_at),
    }


def _user_to_dict(user) -> dict | None:
    if user is None:
        return None
    return {
        "username": user.username,
        "display_name": user.display_name,
        "profile_url": user.profile_url,
    }


def _fmt_dt(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def main():
    run_server(mcp)


if __name__ == "__main__":
    main()
