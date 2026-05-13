# Ubuntu MCP Servers

MCP servers for querying and submitting Ubuntu data via [ubq](https://github.com/canonical/ubq). Each server exposes a focused set of tools and resources for a single data domain — bugs, packages, versions, or merge requests.

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```shell
git clone https://github.com/lvoytek/ubuntu-mcp.git && cd ubuntu-mcp
uv sync
```

This installs the four entry-point commands:

| Command | Server |
|---|---|
| `ubuntu-mcp-bugs` | Bug data |
| `ubuntu-mcp-packages` | Package data |
| `ubuntu-mcp-versions` | Package version data |
| `ubuntu-mcp-merge-requests` | Merge request data |

## Running a server

All servers share the same CLI flags:

```shell
ubuntu-mcp-bugs                                           # streamable-http on 0.0.0.0:8000 (default)
ubuntu-mcp-bugs --transport streamable-http --host 127.0.0.1 --port 9000
ubuntu-mcp-bugs --transport stdio                         # for MCP clients that spawn the process
```

Replace `ubuntu-mcp-bugs` with any of the four commands above.

### Connecting an MCP client

For an HTTP server, add the URL to your client config:

```json
{
  "mcp": {
    "ubuntu-mcp-bugs": {
      "type": "remote",
      "url": "http://127.0.0.1:9000/mcp"
    }
  }
}
```

For stdio, point the client at the entry-point command directly.

## Authentication

Most tools require an authenticated session before they can query data. Call `login_provider` first.

### Launchpad

Launchpad supports three authentication modes:

| Mode | When |
|---|---|
| **Anonymous** | No credentials provided — read-only public access. Best for CI or headless environments. |
| **Credential file** | `credential_file` path points to a file containing a Launchpad OAuth token. |
| **Inline token** | `token` (and optionally `username`) passed directly. |

A default credential file path is also checked automatically: `~/.config/ubq/launchpad-credentials`. If this file exists and no other credentials are provided, its contents are used as the token.

#### Anonymous (no credentials)

```json
{
  "tool": "login_provider",
  "arguments": { "provider_name": "launchpad" }
}
```

#### Credential file

```json
{
  "tool": "login_provider",
  "arguments": {
    "provider_name": "launchpad",
    "credential_file": "/path/to/launchpad-token"
  }
}
```

#### Inline token

```json
{
  "tool": "login_provider",
  "arguments": {
    "provider_name": "launchpad",
    "token": "oauth-token-value"
  }
}
```

### GitHub

GitHub requires a personal access token passed via `token`:

```json
{
  "tool": "login_provider",
  "arguments": {
    "provider_name": "github",
    "token": "ghp_xxxxxxxxxxxx"
  }
}
```

### Snapcraft

Snapcraft requires a token passed via `token`:

```json
{
  "tool": "login_provider",
  "arguments": {
    "provider_name": "snapcraft",
    "token": "snap-token-value"
  }
}
```

## Servers and tools

### Bugs — `ubuntu-mcp-bugs`

| Tool | Description |
|---|---|
| `login_provider` | Authenticate with a bug data provider |
| `list_bug_providers` | List available bug data provider names |
| `get_bug` | Fetch a bug by ID |
| `search_bugs` | Search bugs by criteria |
| `submit_bug` | Submit a new bug |

**Resources:**

- `ubq://bugs/providers` — available bug data providers
- `ubq://bugs/sessions` — active bug data provider sessions

#### `get_bug`

```
bug_id: str          — the bug ID
provider_name: str   — e.g. "launchpad" or "github"
metadata_only: bool  — set True to skip comments and tasks
```

#### `search_bugs`

```
provider_name: str          — e.g. "launchpad" or "github"
title: str | None           — filter by title substring
tags: list[str] | None      — filter by tags
status: str | None          — e.g. "New", "Fix Released"
importance: str | None      — e.g. "Medium", "High"
owner: str | None           — username of the bug owner
assignee: str | None        — username of the assignee
milestone: str | None       — milestone name
created_since: str | None   — ISO 8601 date (e.g. "2025-01-01")
created_before: str | None  — ISO 8601 date
modified_since: str | None  — ISO 8601 date
```

#### `submit_bug`

```
title: str                  — bug title (required)
provider_name: str          — e.g. "launchpad" or "github"
package_names: list[str]    — affected package names
description: str | None     — bug description
importance: str | None      — e.g. "Medium"
status: str | None          — e.g. "New"
tags: list[str] | None      — tags to apply
assignee: str | None        — username to assign
private: bool               — mark the bug private (default False)
milestone: str | None       — target milestone
```

---

### Packages — `ubuntu-mcp-packages`

| Tool | Description |
|---|---|
| `login_provider` | Authenticate with a package data provider |
| `list_package_providers` | List available package data provider names |
| `get_package` | Fetch a package by name |

**Resources:**

- `ubq://packages/providers` — available package data providers
- `ubq://packages/sessions` — active package data provider sessions

#### `get_package`

```
package_name: str    — the source package name
provider_name: str   — e.g. "launchpad" or "snapcraft"
```

---

### Versions — `ubuntu-mcp-versions`

| Tool | Description |
|---|---|
| `login_provider` | Authenticate with a version data provider |
| `list_version_providers` | List available version data provider names |
| `get_version` | Fetch the version of a package in an Ubuntu series |

**Resources:**

- `ubq://versions/providers` — available version data providers
- `ubq://versions/sessions` — active version data provider sessions

#### `get_version`

```
package_name: str    — the source package name
series: str          — Ubuntu codename (e.g. "noble", "jammy")
provider_name: str   — e.g. "launchpad" or "snapcraft"
pocket: str | None   — "Release", "Security", "Updates", "Proposed", or None for default
```

---

### Merge Requests — `ubuntu-mcp-merge-requests`

| Tool | Description |
|---|---|
| `login_provider` | Authenticate with a merge request provider |
| `list_merge_request_providers` | List available merge request provider names |
| `get_merge_request` | Fetch a merge request by ID |
| `get_merge_requests_from_user` | Fetch merge requests assigned to a user |

**Resources:**

- `ubq://merge-requests/providers` — available merge request providers
- `ubq://merge-requests/sessions` — active merge request provider sessions

#### `get_merge_request`

```
merge_request_id: str  — the merge request ID
provider_name: str     — e.g. "launchpad" or "github"
```

#### `get_merge_requests_from_user`

```
user_id: str         — username
provider_name: str    — e.g. "launchpad" or "github"
```

## Available providers

| Provider | Domains |
|---|---|
| `launchpad` | Bugs, packages, versions, merge requests |
| `github` | Bugs, merge requests |
| `snapcraft` | Packages, versions |

## Development

```shell
uv sync                    # install all dependencies
uv run ruff check .         # lint
uv run pytest tests/ -v    # run tests
```

## License

GPL-3.0
