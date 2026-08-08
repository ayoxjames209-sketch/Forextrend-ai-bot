"""
Lightweight SQLite persistence layer. No ORM — kept simple and dependency-free
so the bot has no external database service to provision for v1.
"""
import sqlite3
import time
from contextlib import contextmanager

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    first_name  TEXT,
    joined_at   INTEGER
);

CREATE TABLE IF NOT EXISTS favorites (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    pair        TEXT NOT NULL,
    UNIQUE(user_id, pair)
);

CREATE TABLE IF NOT EXISTS alerts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    pair          TEXT NOT NULL,
    target_price  REAL NOT NULL,
    direction     TEXT NOT NULL,  -- 'above' or 'below'
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    INTEGER
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# ---------- Users ----------

def upsert_user(user_id: int, username: str, first_name: str):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO users (user_id, username, first_name, joined_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   username=excluded.username,
                   first_name=excluded.first_name""",
            (user_id, username, first_name, int(time.time())),
        )


def get_user(user_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_all_user_ids():
    with get_conn() as conn:
        rows = conn.execute("SELECT user_id FROM users").fetchall()
        return [r["user_id"] for r in rows]


def get_user_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]


# ---------- Favorites ----------

def add_favorite(user_id: int, pair: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO favorites (user_id, pair) VALUES (?, ?)",
            (user_id, pair),
        )


def remove_favorite(user_id: int, pair: str):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM favorites WHERE user_id = ? AND pair = ?",
            (user_id, pair),
        )


def get_favorites(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT pair FROM favorites WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()
        return [r["pair"] for r in rows]


# ---------- Alerts ----------

def add_alert(user_id: int, pair: str, target_price: float, direction: str):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO alerts (user_id, pair, target_price, direction, active, created_at)
               VALUES (?, ?, ?, ?, 1, ?)""",
            (user_id, pair, target_price, direction, int(time.time())),
        )


def get_user_alerts(user_id: int, active_only: bool = True):
    with get_conn() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE user_id = ? AND active = 1 ORDER BY id",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE user_id = ? ORDER BY id", (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]


def get_all_active_alerts():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM alerts WHERE active = 1").fetchall()
        return [dict(r) for r in rows]


def deactivate_alert(alert_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE alerts SET active = 0 WHERE id = ?", (alert_id,))


def delete_alert(alert_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM alerts WHERE id = ? AND user_id = ?", (alert_id, user_id)
        )
