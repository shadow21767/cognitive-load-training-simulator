import math
import numpy as np
import pandas as pd
from scipy import stats


def cohen_d(group1, group2):
    a = pd.Series(group1, dtype="float64").dropna()
    b = pd.Series(group2, dtype="float64").dropna()
    if len(a) < 2 or len(b) < 2:
        return None
    pooled_num = ((len(a) - 1) * a.var(ddof=1)) + ((len(b) - 1) * b.var(ddof=1))
    pooled_den = len(a) + len(b) - 2
    pooled_sd = math.sqrt(pooled_num / pooled_den) if pooled_den else 0
    return 0.0 if pooled_sd == 0 else float((a.mean() - b.mean()) / pooled_sd)


def welch_test(group1, group2):
    a = pd.Series(group1, dtype="float64").dropna()
    b = pd.Series(group2, dtype="float64").dropna()
    if len(a) < 2 or len(b) < 2:
        return None
    result = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
    return {"t": float(result.statistic), "p": float(result.pvalue)}


def one_way_anova(df: pd.DataFrame, value: str, group: str):
    grouped = [
        chunk[value].dropna().astype(float).values
        for _, chunk in df.groupby(group)
        if len(chunk[value].dropna()) >= 2
    ]
    if len(grouped) < 2:
        return None
    result = stats.f_oneway(*grouped)
    return {"f": float(result.statistic), "p": float(result.pvalue)}


def bootstrap_mean_ci(values, confidence=0.95, iterations=2000, seed=42):
    arr = pd.Series(values, dtype="float64").dropna().to_numpy()
    if len(arr) < 2:
        return None
    rng = np.random.default_rng(seed)
    means = np.empty(iterations)
    for i in range(iterations):
        means[i] = rng.choice(arr, size=len(arr), replace=True).mean()
    alpha = 1 - confidence
    return (
        float(np.quantile(means, alpha / 2)),
        float(np.quantile(means, 1 - alpha / 2)),
    )


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


def correlation_matrix(df):
    columns = [
        c for c in ["response_time", "cognitive_load", "difficulty", "correct"]
        if c in df.columns
    ]
    if len(columns) < 2:
        return pd.DataFrame()
    return df[columns].astype(float).corr()
