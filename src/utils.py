from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide values and return 0.0 when denominator is 0."""
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def percent_change(before: float, after: float) -> float:
    """
    Compute percent change from before to after.

    Returns 0 when both values are 0.
    """
    if before == 0 and after == 0:
        return 0.0
    if before == 0:
        return 100.0
    return (after - before) / abs(before) * 100.0


def format_pct(value: float) -> str:
    return f"{value:.2f}%"


@dataclass
class TestResult:
    test_name: str
    p_value: float
    significant: bool
    alpha: float = 0.05
    extra: dict[str, Any] | None = None
