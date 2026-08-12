from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from db import init_db, query_df, execute, now_iso

app = FastAPI(
    title="Human Performance Simulation Research API",
    version="1.0.0",
    description="Optional API layer for multi-user human-factors research sessions.",
)

init_db()


class EventIn(BaseModel):
    session_id: str
    participant_id: str
    event_type: str
    target: str
    page: str
    task_number: Optional[int] = None
    value: Optional[str] = None
    elapsed_ms: Optional[float] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/participants")
def participants():
    df = query_df("""
        SELECT participant_id, created_at, consented, notes
        FROM participants
        ORDER BY created_at DESC
    """)
    return df.to_dict(orient="records")


@app.get("/sessions")
def sessions(limit: int = 100):
    limit = max(1, min(limit, 1000))
    df = query_df(f"""
        SELECT *
        FROM sessions
        ORDER BY created_at DESC
        LIMIT {limit}
    """)
    return df.to_dict(orient="records")


@app.get("/events")
def events(limit: int = 200):
    limit = max(1, min(limit, 2000))
    df = query_df(f"""
        SELECT *
        FROM interaction_events
        ORDER BY created_at DESC
        LIMIT {limit}
    """)
    return df.to_dict(orient="records")


@app.post("/events")
def create_event(event: EventIn):
    execute("""
        INSERT INTO interaction_events (
            session_id, participant_id, event_type, target, page,
            task_number, value, elapsed_ms, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.session_id,
        event.participant_id,
        event.event_type,
        event.target,
        event.page,
        event.task_number,
        event.value,
        event.elapsed_ms,
        now_iso(),
    ))
    return {"saved": True}


@app.get("/analytics/summary")
def analytics_summary():
    df = query_df("SELECT * FROM sessions")
    if df.empty:
        return {
            "trials": 0,
            "participants": 0,
            "accuracy": None,
            "avg_response_time": None,
            "avg_cognitive_load": None,
        }

    return {
        "trials": int(len(df)),
        "participants": int(df["participant_id"].nunique()),
        "accuracy": float(df["correct"].mean()),
        "avg_response_time": float(df["response_time"].mean()),
        "avg_cognitive_load": float(df["cognitive_load"].mean()),
    }
