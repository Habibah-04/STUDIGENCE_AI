
import os
import sqlite3
import time
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "focus_timer.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def connection():
    return sqlite3.connect(str(DB_PATH))


def init_focus_db():
    with connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                subject TEXT,
                duration_seconds INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_focus_session(uid, subject, seconds):
    if seconds <= 0:
        return

    with connection() as con:
        con.execute("""
            INSERT INTO focus_sessions
            (user_id, subject, duration_seconds)
            VALUES (?, ?, ?)
        """, (str(uid), subject, int(seconds)))


def focus_total(uid):
    init_focus_db()

    with connection() as con:
        row = con.execute("""
            SELECT COALESCE(SUM(duration_seconds), 0)
            FROM focus_sessions
            WHERE user_id = ?
        """, (str(uid),)).fetchone()

    return int(row[0] or 0) // 60


def render_focus_timer(uid):
    init_focus_db()

    st.subheader("Focus Timer")
    st.caption("Stay focused. Complete sessions. Track your progress.")

    key = f"focus_{uid}"

    if key not in st.session_state:
        st.session_state[key] = {
            "running": False,
            "started_at": None,
            "elapsed": 0,
            "duration": 25 * 60,
            "subject": "General Study",
            "saved": False
        }

    state = st.session_state[key]

    @st.fragment(run_every="1s")
    def timer_display():
        state = st.session_state[key]

        subject = st.text_input(
            "What are you studying?",
            value=state["subject"],
            key=f"{key}_subject",
            disabled=state["running"]
        )
        if not state["running"]:
            state["subject"] = subject

        duration_choice = st.selectbox(
            "Choose focus duration",
            [25, 45, 60],
            index=[25, 45, 60].index(state["duration"] // 60),
            format_func=lambda x: f"{x} minutes",
            key=f"{key}_duration",
            disabled=state["running"]
        )

        if not state["running"]:
            state["duration"] = duration_choice * 60

        elapsed = state["elapsed"]

        if state["running"]:
            elapsed += int(time.time() - state["started_at"])

        remaining = max(0, state["duration"] - elapsed)

        minutes, seconds = divmod(remaining, 60)

        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding:22px;
                background:linear-gradient(135deg,#291B10,#120D09);
                border:1px solid #D99A35;
                border-radius:18px;
                margin:12px 0;">
                <div style="color:#F4B84F;font-weight:800;
                            letter-spacing:2px">FOCUS SESSION</div>
                <div style="font-size:3.3rem;font-weight:800;
                            color:#FFD477;font-family:monospace">
                    {minutes:02d}:{seconds:02d}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        progress = min(1.0, elapsed / state["duration"])
        st.progress(progress)

        if state["running"] and remaining <= 0:
            state["running"] = False
            state["elapsed"] = state["duration"]

            if not state["saved"]:
                save_focus_session(
                    uid, state["subject"], state["duration"]
                )
                state["saved"] = True

            st.success("Focus session completed! Your time was saved.")
            st.balloons()
            return

        left, right = st.columns(2)

        with left:
            if not state["running"]:
                if st.button(
                    "Start / Resume",
                    key=f"{key}_start",
                    use_container_width=True
                ):
                    state["started_at"] = time.time()
                    state["running"] = True
                    state["saved"] = False
                    st.rerun()
            else:
                if st.button(
                    "Pause",
                    key=f"{key}_pause",
                    use_container_width=True
                ):
                    state["elapsed"] += int(
                        time.time() - state["started_at"]
                    )
                    state["running"] = False
                    st.rerun()

        with right:
            if st.button(
                "Reset",
                key=f"{key}_reset",
                use_container_width=True
            ):
                state["running"] = False
                state["started_at"] = None
                state["elapsed"] = 0
                state["saved"] = False
                st.rerun()

    timer_display()

    st.divider()
    total = focus_total(uid)
    hours, minutes = divmod(total, 60)

    st.metric("Total completed focus time", f"{hours}h {minutes}m")
