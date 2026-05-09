"""
sqlite.py — SQLite-backed authentication operations.

All SQL strings are imported from models.db.querys.
"""
import sqlite3
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash
from config import SQLITE_PATH
from models.db import querys as Q


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class SQLiteAuth:
    """Creates the users table and provides auth helpers."""

    def init_db(self) -> None:
        """Create the usuarios table and indexes if they do not exist."""
        conn = _get_connection()
        cur = conn.cursor()
        try:
            cur.execute(Q.SQL_SQLITE_CREATE_USERS)
            for idx_sql in Q.SQL_SQLITE_CREATE_INDEXES:
                cur.execute(idx_sql)
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        nombre: str,
        rol: str = "alumno",
    ) -> bool:
        """
        Insert a user with a hashed password.
        Returns True if inserted, False if username/email already exists.
        """
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        created_at = datetime.now(timezone.utc).isoformat()
        conn = _get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                Q.SQL_SQLITE_INSERT_USER,
                (username, email, password_hash, nombre, rol, created_at),
            )
            conn.commit()
            return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        finally:
            cur.close()
            conn.close()

    def verify_user(self, username: str, password: str) -> dict | None:
        """
        Verify credentials.  Returns user dict on success, None on failure.
        """
        conn = _get_connection()
        cur = conn.cursor()
        try:
            cur.execute(Q.SQL_SQLITE_GET_USER, (username,))
            row = cur.fetchone()
        finally:
            cur.close()
            conn.close()

        if row is None:
            return None
        if not row["is_active"]:
            return None
        if not check_password_hash(row["password_hash"], password):
            return None
        return {
            "username": row["username"],
            "nombre":   row["nombre"],
            "rol":      row["rol"],
        }
