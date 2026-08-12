import pandas as pd

from stats_utils import bootstrap_mean_ci, cohen_d, one_way_anova, welch_test


def test_cohen_d_returns_number():
    result = cohen_d([1, 2, 3, 4], [2, 3, 4, 5])
    assert isinstance(result, float)


def test_welch_test_returns_p_value():
    result = welch_test([1, 2, 3, 4], [4, 5, 6, 7])
    assert result is not None
    assert 0 <= result["p"] <= 1


def test_anova():
    df = pd.DataFrame({
        "group": ["a", "a", "a", "b", "b", "b"],
        "value": [1, 2, 3, 3, 4, 5],
    })
    result = one_way_anova(df, "value", "group")
    assert result is not None
    assert 0 <= result["p"] <= 1


def test_bootstrap_ci_order():
    low, high = bootstrap_mean_ci([1, 2, 3, 4, 5], iterations=200)
    assert low <= high
