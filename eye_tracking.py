import pandas as pd


REQUIRED_COLUMNS = {"timestamp_ms", "x_norm", "y_norm"}


def validate_gaze_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return False, f"Missing columns: {', '.join(sorted(missing))}"

    for col in ["x_norm", "y_norm"]:
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.isna().any():
            return False, f"{col} contains non-numeric values."
        if ((numeric < 0) | (numeric > 1)).any():
            return False, f"{col} must be normalized between 0 and 1."

    return True, "ok"


def fixation_summary(df: pd.DataFrame, grid_size: int = 5) -> pd.DataFrame:
    working = df.copy()
    working["x_bin"] = (working["x_norm"].clip(0, 0.999999) * grid_size).astype(int)
    working["y_bin"] = (working["y_norm"].clip(0, 0.999999) * grid_size).astype(int)
    return (
        working.groupby(["y_bin", "x_bin"])
        .size()
        .reset_index(name="samples")
        .sort_values("samples", ascending=False)
    )


def adapter_notes() -> str:
    return (
        "Import normalized gaze data from WebGazer, Tobii, Pupil Labs, or another "
        "eye-tracking source using timestamp_ms, x_norm, y_norm, and optional confidence."
    )
