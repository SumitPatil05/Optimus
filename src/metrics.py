from __future__ import annotations

import pandas as pd

from .utils import safe_divide


def add_row_level_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ctr"] = out.apply(lambda r: safe_divide(r["clicks"], r["impressions"]), axis=1)
    out["cvr"] = out.apply(lambda r: safe_divide(r["orders"], r["clicks"]), axis=1)
    out["cpc"] = out.apply(lambda r: safe_divide(r["spend"], r["clicks"]), axis=1)
    out["roas"] = out.apply(lambda r: safe_divide(r["sales"], r["spend"]), axis=1)
    out["acos"] = out.apply(lambda r: safe_divide(r["spend"], r["sales"]), axis=1)
    out["aov"] = out.apply(lambda r: safe_divide(r["sales"], r["orders"]), axis=1)
    return out


def aggregate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate raw metrics at the currently grouped level.
    Expects raw columns:
      impressions, clicks, spend, orders, sales
    """
    grouped = (
        df.groupby(["campaign_id", "variant"], as_index=False)[
            ["impressions", "clicks", "spend", "orders", "sales"]
        ]
        .sum()
        .copy()
    )
    grouped["ctr"] = grouped.apply(
        lambda r: safe_divide(r["clicks"], r["impressions"]), axis=1
    )
    grouped["cvr"] = grouped.apply(lambda r: safe_divide(r["orders"], r["clicks"]), axis=1)
    grouped["cpc"] = grouped.apply(lambda r: safe_divide(r["spend"], r["clicks"]), axis=1)
    grouped["roas"] = grouped.apply(lambda r: safe_divide(r["sales"], r["spend"]), axis=1)
    grouped["acos"] = grouped.apply(lambda r: safe_divide(r["spend"], r["sales"]), axis=1)
    grouped["aov"] = grouped.apply(lambda r: safe_divide(r["sales"], r["orders"]), axis=1)
    return grouped


def aggregate_overall_kpis(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["variant"], as_index=False)[
            ["impressions", "clicks", "spend", "orders", "sales"]
        ]
        .sum()
        .copy()
    )
    grouped["campaign_id"] = "OVERALL"
    grouped["ctr"] = grouped.apply(
        lambda r: safe_divide(r["clicks"], r["impressions"]), axis=1
    )
    grouped["cvr"] = grouped.apply(lambda r: safe_divide(r["orders"], r["clicks"]), axis=1)
    grouped["cpc"] = grouped.apply(lambda r: safe_divide(r["spend"], r["clicks"]), axis=1)
    grouped["roas"] = grouped.apply(lambda r: safe_divide(r["sales"], r["spend"]), axis=1)
    grouped["acos"] = grouped.apply(lambda r: safe_divide(r["spend"], r["sales"]), axis=1)
    grouped["aov"] = grouped.apply(lambda r: safe_divide(r["sales"], r["orders"]), axis=1)
    cols = ["campaign_id", "variant", "impressions", "clicks", "spend", "orders", "sales"]
    cols += ["ctr", "cvr", "cpc", "roas", "acos", "aov"]
    return grouped[cols]
