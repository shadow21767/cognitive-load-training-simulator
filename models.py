from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import database_url


class Base(DeclarativeBase):
    pass


class Participant(Base):
    __tablename__ = "participants"

    participant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    consented: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Trial(Base):
    __tablename__ = "trials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    participant_id: Mapped[str] = mapped_column(String(64), index=True)
    study_id: Mapped[str] = mapped_column(String(128), index=True)
    condition_name: Mapped[str] = mapped_column(String(64), index=True)
    difficulty: Mapped[int] = mapped_column(Integer)
    task_number: Mapped[int] = mapped_column(Integer)
    task_type: Mapped[str] = mapped_column(String(64), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    expected_answer: Mapped[str] = mapped_column(Text)
    selected_answer: Mapped[str] = mapped_column(Text)
    correct: Mapped[bool] = mapped_column(Boolean)
    response_time: Mapped[float] = mapped_column(Float)
    cognitive_load: Mapped[int] = mapped_column(Integer)
    distraction_present: Mapped[bool] = mapped_column(Boolean)
    switch_trial: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InteractionEvent(Base):
    __tablename__ = "interaction_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    participant_id: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    target: Mapped[str] = mapped_column(String(128))
    page: Mapped[str] = mapped_column(String(128))
    task_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    elapsed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    x_norm: Mapped[float | None] = mapped_column(Float, nullable=True)
    y_norm: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AccessibilityAudit(Base):
    __tablename__ = "accessibility_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    participant_id: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    keyboard_navigation: Mapped[bool] = mapped_column(Boolean)
    readable_labels: Mapped[bool] = mapped_column(Boolean)
    clear_feedback: Mapped[bool] = mapped_column(Boolean)
    low_distraction: Mapped[bool] = mapped_column(Boolean)
    adequate_time: Mapped[bool] = mapped_column(Boolean)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GazeSample(Base):
    __tablename__ = "gaze_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    participant_id: Mapped[str] = mapped_column(String(64), index=True)
    timestamp_ms: Mapped[float] = mapped_column(Float)
    x_norm: Mapped[float] = mapped_column(Float)
    y_norm: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


engine = create_engine(database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
