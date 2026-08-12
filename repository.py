from collections.abc import Iterable
import pandas as pd
from sqlalchemy import select

from models import (
    AccessibilityAudit,
    GazeSample,
    InteractionEvent,
    Participant,
    SessionLocal,
    Trial,
)


def add_participant(**kwargs):
    with SessionLocal() as db:
        obj = Participant(**kwargs)
        db.add(obj)
        db.commit()
        return obj


def add_trial(**kwargs):
    with SessionLocal() as db:
        obj = Trial(**kwargs)
        db.add(obj)
        db.commit()
        return obj


def add_event(**kwargs):
    with SessionLocal() as db:
        obj = InteractionEvent(**kwargs)
        db.add(obj)
        db.commit()
        return obj


def add_audit(**kwargs):
    with SessionLocal() as db:
        obj = AccessibilityAudit(**kwargs)
        db.add(obj)
        db.commit()
        return obj


def add_gaze_samples(samples: Iterable[dict]):
    with SessionLocal() as db:
        objects = [GazeSample(**sample) for sample in samples]
        db.add_all(objects)
        db.commit()
        return len(objects)


def table_df(model) -> pd.DataFrame:
    with SessionLocal() as db:
        rows = db.execute(select(model)).scalars().all()
        if not rows:
            return pd.DataFrame()
        records = []
        for row in rows:
            records.append({
                column.name: getattr(row, column.name)
                for column in model.__table__.columns
            })
        return pd.DataFrame(records)


def trials_df() -> pd.DataFrame:
    return table_df(Trial)


def events_df() -> pd.DataFrame:
    return table_df(InteractionEvent)


def participants_df() -> pd.DataFrame:
    return table_df(Participant)


def audits_df() -> pd.DataFrame:
    return table_df(AccessibilityAudit)


def gaze_df() -> pd.DataFrame:
    return table_df(GazeSample)
