"""Async SQLite request logger implementing the shared requests table contract."""

from pathlib import Path
from typing import Any


class RequestLogger:
    """Persists every /ask request (hit, miss, or error) to SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        """Initialize the logger with the target SQLite database path."""
        self.db_path = Path(db_path)

    async def init_db(self) -> None:
        """Create parent directories and initialize the requests table from schema.sql."""
        # TODO (Task 0.8): Execute schema.sql using aiosqlite and store connection/pool.
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def log_request(self, record: dict[str, Any]) -> None:
        """Insert a single request row into the requests table.

        Args:
            record: Dictionary matching the columns in src/logging/schema.sql.
        """
        # TODO (Task 0.8): Insert row asynchronously using aiosqlite.
        raise NotImplementedError("Request logging will be implemented in Task 0.8.")

    async def close(self) -> None:
        """Close any open database connections cleanly on app shutdown."""
        # TODO (Task 0.8): Close open aiosqlite connection if persistent.
        return None

