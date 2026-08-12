from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models import init_db
from repository import add_event, events_df, participants_df, trials_df

app = FastAPI(
    title="Human Performance Simulation Research API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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
    x_norm: Optional[float] = Field(default=None, ge=0, le=1)
    y_norm: Optional[float] = Field(default=None, ge=0, le=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/participants")
def participants():
    return participants_df().to_dict(orient="records")


@app.get("/sessions")
def sessions():
    return trials_df().to_dict(orient="records")


@app.get("/events")
def events():
    return events_df().to_dict(orient="records")


@app.post("/events")
def create_event(event: EventIn):
    add_event(**event.model_dump())
    return {"saved": True}


@app.get("/analytics/summary")
def analytics_summary():
    df = trials_df()
    if df.empty:
        return {"trials": 0, "participants": 0}
    return {
        "trials": int(len(df)),
        "participants": int(df["participant_id"].nunique()),
        "accuracy": float(df["correct"].mean()),
        "avg_response_time": float(df["response_time"].mean()),
        "avg_cognitive_load": float(df["cognitive_load"].mean()),
    }
