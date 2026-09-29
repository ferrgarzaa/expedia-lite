"""Local configuration for secrets (Assignment 2).

The Geoapify key is read from ``backend/.env`` (never committed — see
``.gitignore``) or from the real environment. A tiny parser is used here
so no new dependency is needed.
"""

import os
from pathlib import Path
from typing import Optional

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _load_env_file(path: Path = ENV_PATH) -> None:
    """Copy KEY=VALUE lines from ``path`` into ``os.environ`` (no override)."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file()


def geoapify_api_key() -> Optional[str]:
    """Return the backend-only Geoapify key, or ``None`` if not configured."""
    key = os.environ.get("GEOAPIFY_API_KEY", "").strip()
    return key or None
