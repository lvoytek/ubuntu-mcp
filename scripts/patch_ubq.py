"""Patch ubq session.py to add future annotations.

This works around a bug in ubq 0.4.0 where slots=True dataclass
uses TYPE_CHECKING-only imports, causing NameError at class
definition time.
"""

import importlib
from pathlib import Path


def main() -> None:
    spec = importlib.util.find_spec("ubq.providers.session")
    if spec is None or spec.origin is None:
        return

    path = Path(spec.origin)
    content = path.read_text()

    if "from __future__ import annotations" in content:
        return

    path.write_text(
        "from __future__ import annotations\n" + content
    )
    print(f"Patched {path}")


if __name__ == "__main__":
    main()
