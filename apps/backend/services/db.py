# apps/backend/services/db.py
from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta, timezone

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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(plan_id) REFERENCES plans(id) ON DELETE CASCADE,
                UNIQUE(plan_id, version)
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_plan_versions_plan_id ON plan_versions(plan_id);"
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
    
def add_plan(title: str, input_json: str, output_json: str) -> Dict:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO plans(title, input_json, output_json) VALUES (?,?,?)",
            (title, input_json, output_json),
        )
        conn.commit()
        plan_id = cur.lastrowid

        # ✅ create v1 plan version
        conn.execute(
            "INSERT INTO plan_versions(plan_id, version, input_json, output_json) VALUES (?,?,?,?)",
            (plan_id, 1, input_json, output_json),
        )

        row = conn.execute(
            "SELECT id, created_at, title, input_json, output_json FROM plans WHERE id = ?",
            (plan_id,),
        ).fetchone()
        return dict(row)


def list_plans(limit: int = 20, offset: int = 0) -> List[Dict]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, created_at, title
            FROM plans
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]

def get_plan(plan_id: int) -> Optional[Dict]:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT id, created_at, title, input_json, output_json
            FROM plans
            WHERE id = ?
            """,
            (plan_id,),
        ).fetchone()
        return dict(row) if row else None


def create_plan_version(plan_id: int, version: int, input_obj: Dict[str, Any], output_obj: Dict[str, Any]) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO plan_versions (plan_id, version, input_json, output_json)
            VALUES (?, ?, ?, ?)
            """,
            (plan_id, version, json.dumps(input_obj), json.dumps(output_obj)),
        )
        conn.commit()

def get_latest_plan_version(plan_id: int) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT plan_id, version, input_json, output_json, created_at
            FROM plan_versions
            WHERE plan_id = ?
            ORDER BY version DESC
            LIMIT 1
            """,
            (plan_id,),
        ).fetchone()
        if not row:
            return None
        # sqlite Row supports dict(row)
        d = dict(row)
        d["input"] = json.loads(d.pop("input_json"))
        d["output"] = json.loads(d.pop("output_json"))
        return d

def list_plan_versions(plan_id: int) -> List[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT plan_id, version, input_json, output_json, created_at
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
            out.append(d)
        return out
