"""Run all ubuntu-mcp servers at once on sequential ports."""

import argparse
import asyncio

from mcp.server.transport_security import TransportSecuritySettings

from ubuntu_mcp.bugs.server import mcp as bugs_mcp
from ubuntu_mcp.merge_requests.server import mcp as merge_requests_mcp
from ubuntu_mcp.packages.server import mcp as packages_mcp
from ubuntu_mcp.versions.server import mcp as versions_mcp

SERVERS = [
    ("bugs", bugs_mcp),
    ("packages", packages_mcp),
    ("versions", versions_mcp),
    ("merge-requests", merge_requests_mcp),
]

BASE_PORT = 8000


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all ubuntu-mcp servers")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=BASE_PORT)
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        help="Allowed Host header value (repeatable). Required when behind a reverse proxy.",
    )
    args = parser.parse_args()

    security = None
    if args.allowed_host:
        security = TransportSecuritySettings(
            allowed_hosts=args.allowed_host,
            allowed_origins=args.allowed_host,
        )

    async def run_all() -> None:
        tasks = []
        for i, (name, mcp_instance) in enumerate(SERVERS):
            mcp_instance.settings.host = args.host
            mcp_instance.settings.port = args.port + i
            if security is not None:
                mcp_instance.settings.transport_security = security
            tasks.append(asyncio.create_task(mcp_instance.run_streamable_http_async(), name=name))
        await asyncio.gather(*tasks)

    for i, (name, _) in enumerate(SERVERS):
        print(f"  {name}: http://{args.host}:{args.port + i}/mcp")

    asyncio.run(run_all())


if __name__ == "__main__":
    main()
