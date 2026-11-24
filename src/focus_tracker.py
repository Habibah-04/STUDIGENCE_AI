"""Automatic website-open focus tracking for Streamlit.

A short heartbeat keeps an authenticated browser session active. When the
browser closes or disconnects, a server-side sweeper closes the session at its
last heartbeat, avoiding counting time while the site is closed.
"""
from __future__ import annotations

import threading
import time
import uuid
from src.db import conn

STALE_AFTER_SECONDS = 20
_SWEEPER_STARTED = False
_SWEEPER_LOCK = threading.Lock()


def init_tracker_db():
    with conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS focus_activity_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                started_at REAL NOT NULL,
                last_heartbeat REAL NOT NULL,
                ended_at REAL,
                duration_seconds INTEGER DEFAULT 0
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_focus_activity_user ON focus_activity_sessions(user_id, ended_at)")
        c.commit()


def _close_row(c, session_id: str, end_at: float):
    row = c.execute(
        "SELECT started_at, last_heartbeat FROM focus_activity_sessions WHERE id=? AND ended_at IS NULL",
        (session_id,),
    ).fetchone()
    if row:
        # Count only up to the last successful browser heartbeat.
        stop_at = min(float(end_at), float(row["last_heartbeat"]))
        seconds = max(0, int(stop_at - float(row["started_at"])))
        c.execute(
            "UPDATE focus_activity_sessions SET ended_at=?, duration_seconds=? WHERE id=? AND ended_at IS NULL",
            (stop_at, seconds, session_id),
        )


def start_session(uid: int, session_id: str):
    init_tracker_db()
    now = time.time()
    with conn() as c:
        # One active focus session per account, so multiple tabs don't double-count.
        old = c.execute(
            "SELECT id FROM focus_activity_sessions WHERE user_id=? AND ended_at IS NULL",
            (uid,),
        ).fetchall()
        for row in old:
            _close_row(c, row["id"], now)
        c.execute(
            "INSERT OR REPLACE INTO focus_activity_sessions(id,user_id,started_at,last_heartbeat,ended_at,duration_seconds) VALUES(?,?,?,?,NULL,0)",
            (session_id, uid, now, now),
        )
        c.commit()
    start_sweeper()


def heartbeat(uid: int, session_id: str):
    init_tracker_db()
    now = time.time()
    with conn() as c:
        c.execute(
            "UPDATE focus_activity_sessions SET last_heartbeat=? WHERE id=? AND user_id=? AND ended_at IS NULL",
            (now, session_id, uid),
        )
        c.commit()


def end_session(uid: int, session_id: str):
    init_tracker_db()
    with conn() as c:
        _close_row(c, session_id, time.time())
        c.commit()


def sweep_stale_sessions():
    init_tracker_db()
    now = time.time()
    with conn() as c:
        stale = c.execute(
            "SELECT id FROM focus_activity_sessions WHERE ended_at IS NULL AND last_heartbeat < ?",
            (now - STALE_AFTER_SECONDS,),
        ).fetchall()
        for row in stale:
            _close_row(c, row["id"], now)
        c.commit()


def _sweeper_loop():
    while True:
        try:
            sweep_stale_sessions()
        except Exception:
            # A transient SQLite lock should not kill the background worker.
            pass
        time.sleep(5)


def start_sweeper():
    global _SWEEPER_STARTED
    with _SWEEPER_LOCK:
        if not _SWEEPER_STARTED:
            thread = threading.Thread(target=_sweeper_loop, name="focus-session-sweeper", daemon=True)
            thread.start()
            _SWEEPER_STARTED = True


def new_session_id() -> str:
    return uuid.uuid4().hex
