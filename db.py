import sqlite3
from datetime import datetime

DB_PATH = "human_performance.db"


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            participant_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            consented INTEGER NOT NULL,
            notes TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            participant_id TEXT NOT NULL,
            condition_name TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            task_number INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            prompt TEXT NOT NULL,
            expected_answer TEXT NOT NULL,
            selected_answer TEXT NOT NULL,
            correct INTEGER NOT NULL,
            response_time REAL NOT NULL,
            cognitive_load INTEGER NOT NULL,
            distraction_present INTEGER NOT NULL,
            switch_trial INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS interaction_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            participant_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            target TEXT NOT NULL,
            page TEXT NOT NULL,
            task_number INTEGER,
            value TEXT,
            elapsed_ms REAL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS accessibility_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT NOT NULL,
            session_id TEXT,
            keyboard_navigation INTEGER NOT NULL,
            readable_labels INTEGER NOT NULL,
            clear_feedback INTEGER NOT NULL,
            low_distraction INTEGER NOT NULL,
            adequate_time INTEGER NOT NULL,
            notes TEXT,
            score REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def execute(query, params=()):
    conn = connect()
    conn.execute(query, params)
    conn.commit()
    conn.close()


def query_df(query, params=()):
    import pandas as pd
    conn = connect()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def now_iso():
    return datetime.now().isoformat(timespec="seconds")
