"""Single source of truth for the database connection.

Set VIKEEATS_DB_URL to point somewhere else -- a hosted Postgres instance, or
another SQLite file. Otherwise the default resolves next to the repo root
rather than the working directory, so it no longer matters which folder Flask
is launched from.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(_REPO_ROOT, "vikeeats.db")

DB_URL = os.getenv("VIKEEATS_DB_URL", f"sqlite:///{DEFAULT_DB_PATH}")

_engine = None


def _build_engine(url):
    if url.startswith("sqlite"):
        # NullPool connects per use instead of holding the file open between
        # requests. A lingering handle is what stops Windows releasing the file.
        return create_engine(url, poolclass=NullPool)
    # A hosted Postgres suspends idle compute, so a pooled connection can be
    # dead by the time it is reused; pre_ping discards those transparently.
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=2)


def get_engine():
    """The process-wide engine. Built on first use so set_db_url() can precede it."""
    global _engine
    if _engine is None:
        _engine = _build_engine(DB_URL)
    return _engine


def set_db_url(url):
    """Repoint at another database, disposing the old engine. Used by tests."""
    global DB_URL, _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
    DB_URL = url


def sqlite_path():
    """Filesystem path behind a SQLite URL, or None for a server URL."""
    prefix = "sqlite:///"
    return DB_URL[len(prefix):] if DB_URL.startswith(prefix) else None


def database_exists():
    """Whether the database is there to be queried.

    For SQLite that is a file check. For a server URL there is nothing to stat,
    so assume it exists and let connection errors surface on their own.
    """
    path = sqlite_path()
    return True if path is None else os.path.exists(path)
