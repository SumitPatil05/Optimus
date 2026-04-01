from __future__ import annotations

import math

from .utils import TestResult


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def two_proportion_z_test(
    success_a: int, total_a: int, success_b: int, total_b: int, alpha: float = 0.05
) -> TestResult:
    if total_a == 0 or total_b == 0:
        return TestResult(
            test_name="two_proportion_z_test",
            p_value=1.0,
            significant=False,
            alpha=alpha,
            extra={"z_score": 0.0},
        )

    p1 = success_a / total_a
    p2 = success_b / total_b
    pooled = (success_a + success_b) / (total_a + total_b)
    se = math.sqrt(pooled * (1 - pooled) * ((1 / total_a) + (1 / total_b)))

    if se == 0:
        return TestResult(
            test_name="two_proportion_z_test",
            p_value=1.0,
            significant=False,
            alpha=alpha,
            extra={"z_score": 0.0},
        )

    z = (p2 - p1) / se
    p_value = 2 * (1 - _normal_cdf(abs(z)))
    return TestResult(
        test_name="two_proportion_z_test",
        p_value=float(p_value),
        significant=p_value < alpha,
        alpha=alpha,
        extra={"z_score": float(z), "p1": p1, "p2": p2},
    )


def welch_t_test(sample_a: list[float], sample_b: list[float], alpha: float = 0.05) -> TestResult:
    """
    Approximate two-sided Welch's t-test using normal approximation for p-value.
    For daily series with n>30 per group this is generally acceptable.
    """
    n1, n2 = len(sample_a), len(sample_b)
    if n1 < 2 or n2 < 2:
        return TestResult(
            test_name="welch_t_test",
            p_value=1.0,
            significant=False,
            alpha=alpha,
            extra={"t_score": 0.0},
        )

    mean1 = sum(sample_a) / n1
    mean2 = sum(sample_b) / n2
    var1 = sum((x - mean1) ** 2 for x in sample_a) / (n1 - 1)
    var2 = sum((x - mean2) ** 2 for x in sample_b) / (n2 - 1)
    se = math.sqrt((var1 / n1) + (var2 / n2))

    if se == 0:
        return TestResult(
            test_name="welch_t_test",
            p_value=1.0,
            significant=False,
            alpha=alpha,
            extra={"t_score": 0.0},
        )

    t_score = (mean2 - mean1) / se
    p_value = 2 * (1 - _normal_cdf(abs(t_score)))
    return TestResult(
        test_name="welch_t_test",
        p_value=float(p_value),
        significant=p_value < alpha,
        alpha=alpha,
        extra={"t_score": float(t_score), "mean_a": mean1, "mean_b": mean2},
    )
