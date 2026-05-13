"""Shared test fixtures for ubuntu-mcp tests."""

from unittest.mock import MagicMock

import pytest
from ubq.models import (
    BugRecord,
    BugTaskRecord,
    CommentRecord,
    MergeRequestRecord,
    PackageRecord,
    UserRecord,
    VersionRecord,
)


@pytest.fixture
def mock_user():
    return UserRecord(username="testuser", display_name="Test User")


@pytest.fixture
def mock_comment(mock_user):
    return CommentRecord(author=mock_user, content="test comment")


@pytest.fixture
def mock_bug_task(mock_user):
    return BugTaskRecord(
        title="test-task",
        target="ubuntu",
        importance="Medium",
        status="New",
        assignee=mock_user,
    )


@pytest.fixture
def mock_bug_record(mock_user, mock_comment, mock_bug_task):
    return BugRecord(
        provider_name="launchpad",
        id="12345",
        title="Test Bug",
        description="A test bug",
        tags=["tag1"],
        comments=[mock_comment],
        owner=mock_user,
        assignee=mock_user,
        bug_tasks=[mock_bug_task],
    )


@pytest.fixture
def mock_package_record():
    return PackageRecord(
        provider_name="launchpad",
        name="test-package",
        package_url="https://launchpad.net/test-package",
    )


@pytest.fixture
def mock_version_record():
    return VersionRecord(
        provider_name="launchpad",
        version_string="1.0.0",
        package_name="test-package",
        series="noble",
        pocket="Release",
    )


@pytest.fixture
def mock_merge_request_record(mock_user, mock_package_record):
    return MergeRequestRecord(
        provider_name="launchpad",
        id="42",
        title="Test MR",
        description="A test merge request",
        status="Merged",
        source_branch="feature",
        target_branch="main",
        web_url="https://launchpad.net/test-mr",
        author=mock_user,
        assignees=[mock_user],
        package=mock_package_record,
    )


@pytest.fixture
def mock_query_service():
    svc = MagicMock()
    svc.available_providers.return_value = (
        "github",
        "launchpad",
        "snapcraft",
    )
    svc._registry.active_sessions.return_value = ("launchpad",)
    return svc


@pytest.fixture
def bug_service(mock_query_service, mock_bug_record):
    mock_query_service.get_bug.return_value = mock_bug_record
    mock_query_service.search_bugs.return_value = [mock_bug_record]
    mock_query_service.submit_bug.return_value = mock_bug_record
    return mock_query_service


@pytest.fixture
def package_service(mock_query_service, mock_package_record):
    mock_query_service.get_package.return_value = mock_package_record
    return mock_query_service


@pytest.fixture
def version_service(mock_query_service, mock_version_record):
    mock_query_service.get_version.return_value = mock_version_record
    return mock_query_service


@pytest.fixture
def mr_service(mock_query_service, mock_merge_request_record):
    mock_query_service.get_merge_request.return_value = mock_merge_request_record
    mock_query_service.get_merge_requests_from_user.return_value = [  # noqa: E501
        mock_merge_request_record
    ]
    return mock_query_service
