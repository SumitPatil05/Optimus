from __future__ import annotations

import pandas as pd

from .metrics import aggregate_kpis, aggregate_overall_kpis
from .statistical_tests import two_proportion_z_test, welch_t_test
from .utils import percent_change


KPI_COLUMNS = ["ctr", "cvr", "cpc", "roas", "acos", "aov"]


def _decision_framework(row: pd.Series) -> str:
    roas_change = row["roas_pct_change"]
    cvr_change = row["cvr_pct_change"]
    ctr_change = row["ctr_pct_change"]
    spend_change = row["spend_pct_change"]
    sales_change = row["sales_pct_change"]

    # Strong win: conversion quality and profitability both improve.
    if roas_change > 0 and cvr_change > 0:
        return "Strong Win"

    # Risky win: more traffic but less efficiency.
    if ctr_change > 0 and roas_change < 0:
        return "Risky Win"

    # Loss: more cost without proportional revenue outcome.
    if spend_change > 0 and (sales_change <= 0 or roas_change < 0):
        return "Loss"

    return "Neutral"


def compare_variants(df: pd.DataFrame) -> pd.DataFrame:
    kpis = aggregate_kpis(df)
    wide = kpis.pivot(index="campaign_id", columns="variant")

    rows = []
    for campaign_id in wide.index:
        row = {"campaign_id": campaign_id}
        for metric in ["impressions", "clicks", "spend", "orders", "sales"] + KPI_COLUMNS:
            before = float(wide.loc[campaign_id, (metric, "A")])
            after = float(wide.loc[campaign_id, (metric, "B")])
            row[f"{metric}_A"] = before
            row[f"{metric}_B"] = after
            row[f"{metric}_pct_change"] = percent_change(before, after)
        rows.append(row)

    result = pd.DataFrame(rows)
    result["decision"] = result.apply(_decision_framework, axis=1)
    return result.sort_values("campaign_id").reset_index(drop=True)


def overall_comparison(df: pd.DataFrame) -> pd.DataFrame:
    overall = aggregate_overall_kpis(df)
    wide = overall.pivot(index="campaign_id", columns="variant")
    base = {"campaign_id": "OVERALL"}
    for metric in ["impressions", "clicks", "spend", "orders", "sales"] + KPI_COLUMNS:
        before = float(wide.loc["OVERALL", (metric, "A")])
        after = float(wide.loc["OVERALL", (metric, "B")])
        base[f"{metric}_A"] = before
        base[f"{metric}_B"] = after
        base[f"{metric}_pct_change"] = percent_change(before, after)
    out = pd.DataFrame([base])
    out["decision"] = out.apply(_decision_framework, axis=1)
    return out


def run_statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for campaign_id, g in df.groupby("campaign_id"):
        a = g[g["variant"] == "A"]
        b = g[g["variant"] == "B"]

        ctr_test = two_proportion_z_test(
            int(a["clicks"].sum()),
            int(a["impressions"].sum()),
            int(b["clicks"].sum()),
            int(b["impressions"].sum()),
        )
        cvr_test = two_proportion_z_test(
            int(a["orders"].sum()),
            int(a["clicks"].sum()),
            int(b["orders"].sum()),
            int(b["clicks"].sum()),
        )
        roas_daily_a = (a["sales"] / a["spend"].replace(0, pd.NA)).fillna(0.0).tolist()
        roas_daily_b = (b["sales"] / b["spend"].replace(0, pd.NA)).fillna(0.0).tolist()
        roas_ttest = welch_t_test(roas_daily_a, roas_daily_b)

        records.append(
            {
                "campaign_id": campaign_id,
                "ctr_p_value": ctr_test.p_value,
                "ctr_significant": ctr_test.significant,
                "cvr_p_value": cvr_test.p_value,
                "cvr_significant": cvr_test.significant,
                "roas_p_value": roas_ttest.p_value,
                "roas_significant": roas_ttest.significant,
            }
        )

    return pd.DataFrame(records).sort_values("campaign_id").reset_index(drop=True)


def combine_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    comparison = compare_variants(df)
    tests = run_statistical_tests(df)
    merged = comparison.merge(tests, on="campaign_id", how="left")
    overall = overall_comparison(df)
    return merged, overall, tests
