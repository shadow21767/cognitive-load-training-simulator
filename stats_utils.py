import math
import pandas as pd


def cohen_d(group1, group2):
    a = pd.Series(group1, dtype="float64").dropna()
    b = pd.Series(group2, dtype="float64").dropna()

    if len(a) < 2 or len(b) < 2:
        return None

    pooled_num = ((len(a) - 1) * a.var(ddof=1)) + ((len(b) - 1) * b.var(ddof=1))
    pooled_den = len(a) + len(b) - 2

    if pooled_den <= 0:
        return None

    pooled_sd = math.sqrt(pooled_num / pooled_den)
    if pooled_sd == 0:
        return 0.0

    return float((a.mean() - b.mean()) / pooled_sd)


def welch_t(group1, group2):
    a = pd.Series(group1, dtype="float64").dropna()
    b = pd.Series(group2, dtype="float64").dropna()

    if len(a) < 2 or len(b) < 2:
        return None

    var_a = a.var(ddof=1)
    var_b = b.var(ddof=1)
    denominator = math.sqrt((var_a / len(a)) + (var_b / len(b)))

    if denominator == 0:
        return 0.0

    return float((a.mean() - b.mean()) / denominator)


def repeated_measures_summary(df):
    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby(["participant_id", "condition_name"])
        .agg(
            trials=("id", "count"),
            accuracy=("correct", "mean"),
            avg_response_time=("response_time", "mean"),
            avg_cognitive_load=("cognitive_load", "mean"),
        )
        .reset_index()
    )
    summary["accuracy"] *= 100
    return summary
