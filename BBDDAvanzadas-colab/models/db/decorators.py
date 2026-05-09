"""
decorators.py — Connection helpers for PostgreSQL (psycopg2).

`with_cursor`      — opens a connection+cursor, commits on success,
                     rolls back on exception, always closes.
`with_transaction` — same but passes both conn and cursor so the
                     wrapped function can perform manual savepoints.
"""
import functools
import psycopg2
from config import PG_HOST, PG_DB, PG_USER, PG_PASSWORD, PG_PORT


def _get_connection():
    """Return a new psycopg2 connection using env-var config."""
    return psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        port=PG_PORT,
    )


def with_cursor(fn):
    """
    Decorator that injects a psycopg2 cursor as a keyword argument
    named `cursor`.  Commits on success, rolls back on any exception.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        conn = _get_connection()
        cur = conn.cursor()
        try:
            result = fn(*args, cursor=cur, **kwargs)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    return wrapper


def with_transaction(fn):
    """
    Decorator that injects both `conn` and `cursor` keyword arguments.
    Useful when the caller needs to control savepoints or explicit
    rollback behaviour.  Commits on success, rolls back on any exception.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        conn = _get_connection()
        cur = conn.cursor()
        try:
            result = fn(*args, conn=conn, cursor=cur, **kwargs)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    return wrapper
