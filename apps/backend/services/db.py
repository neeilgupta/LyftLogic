# apps/backend/services/db.py
from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import os

SESSION_EXPIRY_DAYS = int(os.getenv("SESSION_EXPIRY_DAYS", "7"))
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "15"))

# .../apps/backend/services/db.py -> data/gymgpt.db
DB_DIR = (Path(__file__).resolve().parent / ".." / ".." / "data").resolve()
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "gymgpt.db"

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # light concurrency safety + durability for dev
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reps INTEGER NOT NULL,
                weight_kg REAL NOT NULL,
                rir INTEGER NOT NULL,
                focus TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_name_time ON logs(name, timestamp);"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS plans(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT NOT NULL,
                input_json TEXT NOT NULL,
                output_json TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_plans_created_at ON plans(created_at);"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS plan_versions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                input_json TEXT NOT NULL,
                output_json TEXT NOT NULL,
                diff_json TEXT, 
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(plan_id) REFERENCES plans(id) ON DELETE CASCADE,
                UNIQUE(plan_id, version)
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_plan_versions_plan_id ON plan_versions(plan_id);"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions(
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
                expires_at TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS login_codes(
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                email      TEXT NOT NULL,
                code_hash  TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
                expires_at TEXT NOT NULL,
                used       INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_login_codes_email ON login_codes(email);"
        )
    migrate_add_diff_json()
    migrate_add_plan_owner()
    migrate_session_expiry()
    migrate_database_hardening()

def migrate_add_diff_json() -> None:
    """
    One-time safe migration to add diff_json to plan_versions
    """
    with _conn() as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(plan_versions);")]
        if "diff_json" not in cols:
            conn.execute("ALTER TABLE plan_versions ADD COLUMN diff_json TEXT;")


def migrate_add_plan_owner() -> None:
    """
    One-time safe migration to add owner_id to plans
    """
    with _conn() as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(plans);")]
        if "owner_id" not in cols:
            conn.execute("ALTER TABLE plans ADD COLUMN owner_id INTEGER NULL;")


def migrate_session_expiry() -> None:
    """Backfill NULL expires_at with created_at + SESSION_EXPIRY_DAYS, delete already-expired."""
    with _conn() as conn:
        # Backfill any sessions that have NULL expires_at
        conn.execute(
            """
            UPDATE sessions
            SET expires_at = strftime('%%Y-%%m-%%dT%%H:%%M:%%SZ',
                                     created_at, '+%d days')
            WHERE expires_at IS NULL
            """ % SESSION_EXPIRY_DAYS
        )
        # Purge sessions that are already expired
        conn.execute(
            """
            DELETE FROM sessions
            WHERE expires_at IS NOT NULL
              AND expires_at <= strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
            """
        )


def migrate_database_hardening() -> None:
    """Add missing indexes and enforce NOT NULL on sessions.expires_at."""
    with _conn() as conn:
        # Index for "My Plans" queries (WHERE owner_id = ?)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_plans_owner_id ON plans(owner_id);"
        )
        # Index for session lookups by user
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);"
        )

        # Enforce NOT NULL on sessions.expires_at:
        # After migrate_session_expiry(), no NULL rows should exist.
        # SQLite requires table rebuild to add NOT NULL constraint.
        cols = {r["name"]: r["notnull"] for r in conn.execute("PRAGMA table_info(sessions);")}
        if cols.get("expires_at") == 0:
            # Verify no NULLs remain before rebuilding
            null_count = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE expires_at IS NULL"
            ).fetchone()[0]
            if null_count == 0:
                conn.execute(
                    """
                    CREATE TABLE sessions_new(
                        token TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
                        expires_at TEXT NOT NULL
                    );
                    """
                )
                conn.execute(
                    "INSERT INTO sessions_new SELECT * FROM sessions;"
                )
                conn.execute("DROP TABLE sessions;")
                conn.execute("ALTER TABLE sessions_new RENAME TO sessions;")
                # Recreate index after table rebuild
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);"
                )


def add_log(
    name: str,
    reps: int,
    weight_kg: float,
    rir: int,
    focus: Optional[str] = None,
) -> Dict:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO logs(name, reps, weight_kg, rir, focus) VALUES (?,?,?,?,?)",
            (name, reps, weight_kg, rir, focus),
        )
        log_id = cur.lastrowid
        row = conn.execute(
            "SELECT id, name, reps, weight_kg, rir, focus, timestamp FROM logs WHERE id = ?",
            (log_id,),
        ).fetchone()
        return dict(row)

def get_logs(focus: Optional[str] = None) -> List[Dict]:
    with _conn() as conn:
        if focus:
            cur = conn.execute(
                """
                SELECT id, name, reps, weight_kg, rir, focus, timestamp
                FROM logs
                WHERE focus = ?
                ORDER BY id DESC
                """,
                (focus,),
            )
        else:
            cur = conn.execute(
                """
                SELECT id, name, reps, weight_kg, rir, focus, timestamp
                FROM logs
                ORDER BY id DESC
                """
            )
        return [dict(r) for r in cur.fetchall()]

def get_recent_sets_map(days: int = 14) -> Dict[str, List[Dict]]:
    """
    Returns: { exercise_name: [ {reps, weight_kg, rir, timestamp}, ... ] }
    Only entries within last `days`.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    out: Dict[str, List[Dict]] = {}
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT name, reps, weight_kg, rir, timestamp
            FROM logs
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            """,
            (since,),
        )
        for r in cur.fetchall():
            d = dict(r)
            out.setdefault(d["name"], []).append(
                {
                    "reps": d["reps"],
                    "weight_kg": d["weight_kg"],
                    "rir": d["rir"],
                    "timestamp": d["timestamp"],
                }
            )
    return out

def get_latest_by_exercise(limit_per_exercise: int = 3) -> Dict[str, List[Dict]]:
    """
    Top-N latest sets for each exercise (useful if you don't want a date window).
    """
    with _conn() as conn:
        # SQLite doesn't have DISTINCT ON; emulate via window function in newer versions
        # fallback: simple group in Python
        cur = conn.execute(
            """
            SELECT name, reps, weight_kg, rir, timestamp
            FROM logs
            ORDER BY name ASC, timestamp DESC
            """
        )
        tmp: Dict[str, List[Dict]] = {}
        for r in cur.fetchall():
            d = dict(r)
            bucket = tmp.setdefault(d["name"], [])
            if len(bucket) < limit_per_exercise:
                bucket.append(
                    {
                        "reps": d["reps"],
                        "weight_kg": d["weight_kg"],
                        "rir": d["rir"],
                        "timestamp": d["timestamp"],
                    }
                )
        return tmp
    
def add_plan(
    title: str,
    input_json: str,
    output_json: str,
    owner_id: Optional[int] = None,
) -> Dict:
    with _conn() as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(plans);")]
        if "owner_id" in cols:
            cur = conn.execute(
                "INSERT INTO plans(title, input_json, output_json, owner_id) VALUES (?,?,?,?)",
                (title, input_json, output_json, owner_id),
            )
            select_cols = "id, created_at, title, input_json, output_json, owner_id"
        else:
            cur = conn.execute(
                "INSERT INTO plans(title, input_json, output_json) VALUES (?,?,?)",
                (title, input_json, output_json),
            )
            select_cols = "id, created_at, title, input_json, output_json"
        conn.commit()
        plan_id = cur.lastrowid

        # ✅ create v1 plan version
        conn.execute(
            "INSERT INTO plan_versions(plan_id, version, input_json, output_json) VALUES (?,?,?,?)",
            (plan_id, 1, input_json, output_json),
        )

        row = conn.execute(
            f"SELECT {select_cols} FROM plans WHERE id = ?",
            (plan_id,),
        ).fetchone()
        return dict(row)


def list_plans(
    limit: int = 20,
    offset: int = 0,
    owner_id: Optional[int] = None,
) -> List[Dict]:
    with _conn() as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(plans);")]
        has_owner = "owner_id" in cols
        if owner_id is not None:
            if not has_owner:
                return []
            cur = conn.execute(
                """
                SELECT id, created_at, title, owner_id
                FROM plans
                WHERE owner_id = ?
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (owner_id, limit, offset),
            )
        else:
            select_cols = "id, created_at, title"
            if has_owner:
                select_cols += ", owner_id"
            cur = conn.execute(
                f"""
                SELECT {select_cols}
                FROM plans
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
        return [dict(r) for r in cur.fetchall()]

def get_plan(plan_id: int) -> Optional[Dict]:
    with _conn() as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(plans);")]
        select_cols = "id, created_at, title, input_json, output_json"
        if "owner_id" in cols:
            select_cols += ", owner_id"
        row = conn.execute(
            f"""
            SELECT {select_cols}
            FROM plans
            WHERE id = ?
            """,
            (plan_id,),
        ).fetchone()
        return dict(row) if row else None


def create_plan_version(plan_id: int, version: int, input_obj: Dict[str, Any], output_obj: Dict[str, Any],  diff: Optional[Dict[str, Any]] = None,) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO plan_versions (plan_id, version, input_json, output_json, diff_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (plan_id, version, json.dumps(input_obj), json.dumps(output_obj), json.dumps(diff) if diff is not None else None),
        )
        conn.commit()

def get_latest_plan_version(plan_id: int) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT plan_id, version, input_json, output_json, diff_json, created_at
            FROM plan_versions
            WHERE plan_id = ?
            ORDER BY version DESC
            LIMIT 1
            """,
            (plan_id,),
        ).fetchone()
        if not row:
            return None

        d = dict(row)
        d["input"] = json.loads(d.pop("input_json"))
        d["output"] = json.loads(d.pop("output_json"))
        d["diff"] = json.loads(d["diff_json"]) if d.get("diff_json") else None
        d.pop("diff_json", None)
        return d


def list_plan_versions(plan_id: int) -> List[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT plan_id, version, input_json, output_json, diff_json, created_at
            FROM plan_versions
            WHERE plan_id = ?
            ORDER BY version DESC
            """,
            (plan_id,),
        )

        out = []
        for row in cur.fetchall():
            d = dict(row)
            d["input"] = json.loads(d.pop("input_json"))
            d["output"] = json.loads(d.pop("output_json"))
            d["diff"] = json.loads(d["diff_json"]) if d.get("diff_json") else None
            d.pop("diff_json", None)
            out.append(d)

        return out

def get_plan_version(plan_id: int, version: int) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT plan_id, version, input_json, output_json, diff_json, created_at
            FROM plan_versions
            WHERE plan_id = ? AND version = ?
            LIMIT 1
            """,
            (plan_id, version),
        ).fetchone()

        if not row:
            return None

        d = dict(row)
        d["input"] = json.loads(d.pop("input_json"))
        d["output"] = json.loads(d.pop("output_json"))
        d["diff"] = json.loads(d["diff_json"]) if d.get("diff_json") else None
        d.pop("diff_json", None)
        return d


def get_or_create_user(email: str) -> Dict[str, Any]:
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(email) VALUES (?)",
            (email,),
        )
        row = conn.execute(
            "SELECT id, email FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row)


def create_session(user_id: int) -> str:
    token = uuid4().hex
    expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    with _conn() as conn:
        conn.execute(
            "INSERT INTO sessions(token, user_id, expires_at) VALUES (?,?,?)",
            (token, user_id, expires_at),
        )
    return token


def get_user_by_session(token: str) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.email, s.expires_at
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
        if not row:
            return None

        expires_at = row["expires_at"]
        if not expires_at:
            # Session without expiry is invalid — delete and reject
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None

        expires_dt = datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        if expires_dt <= datetime.now(timezone.utc):
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None

        return {"id": row["id"], "email": row["email"]}


def delete_session(token: str) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def create_login_code(email: str, code_hash: str) -> None:
    expires_at = (
        datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    with _conn() as conn:
        conn.execute(
            "INSERT INTO login_codes(email, code_hash, expires_at) VALUES (?,?,?)",
            (email, code_hash, expires_at),
        )


def verify_login_code(email: str, code_hash: str) -> bool:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT id FROM login_codes
            WHERE email     = ?
              AND code_hash = ?
              AND used      = 0
              AND expires_at > strftime('%Y-%m-%dT%H:%M:%SZ','now')
            ORDER BY id DESC
            LIMIT 1
            """,
            (email, code_hash),
        ).fetchone()
        if not row:
            return False
        conn.execute(
            "UPDATE login_codes SET used = 1 WHERE id = ?",
            (row["id"],),
        )
        return True


def purge_expired_login_codes() -> None:
    with _conn() as conn:
        conn.execute(
            """
            DELETE FROM login_codes
            WHERE expires_at <= strftime('%Y-%m-%dT%H:%M:%SZ','now')
               OR used = 1
            """
        )
