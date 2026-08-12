import pandas as pd

from eye_tracking import fixation_summary, validate_gaze_dataframe


def test_valid_gaze_data():
    df = pd.DataFrame({
        "timestamp_ms": [0, 100],
        "x_norm": [0.2, 0.7],
        "y_norm": [0.3, 0.8],
    })
    valid, _ = validate_gaze_dataframe(df)
    assert valid


def test_invalid_gaze_range():
    df = pd.DataFrame({
        "timestamp_ms": [0],
        "x_norm": [1.5],
        "y_norm": [0.4],
    })
    valid, _ = validate_gaze_dataframe(df)
    assert not valid


def test_fixation_summary():
    df = pd.DataFrame({
        "timestamp_ms": [0, 1, 2],
        "x_norm": [0.1, 0.1, 0.8],
        "y_norm": [0.1, 0.1, 0.8],
    })
    summary = fixation_summary(df)
    assert summary["samples"].sum() == 3
