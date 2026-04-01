from __future__ import annotations

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Ensure `src` imports work whether Streamlit is launched from project root or app dir.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.experiment_analysis import combine_analysis
from src.metrics import add_row_level_metrics


st.set_page_config(page_title="Ads Experimentation Analytics Platform", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    data_file = PROJECT_ROOT / "data" / "campaign_data.csv"
    df = pd.read_csv(data_file)
    df["date"] = pd.to_datetime(df["date"])
    return add_row_level_metrics(df)


def plot_funnel(df: pd.DataFrame, campaign_id: str):
    if campaign_id != "ALL":
        d = df[df["campaign_id"] == campaign_id]
    else:
        d = df
    agg = d.groupby("variant")[["impressions", "clicks", "orders", "sales"]].sum()

    fig, ax = plt.subplots(figsize=(8, 4))
    steps = ["impressions", "clicks", "orders", "sales"]
    x = range(len(steps))
    ax.plot(x, agg.loc["A", steps], marker="o", label="Variant A (Before)")
    ax.plot(x, agg.loc["B", steps], marker="o", label="Variant B (After)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.title() for s in steps])
    ax.set_title("Funnel Comparison")
    ax.legend()
    ax.grid(alpha=0.25)
    return fig


def plot_metric_comparison(summary_row: pd.Series):
    metrics = ["ctr", "cvr", "roas", "cpc", "acos", "aov"]
    a_vals = [summary_row[f"{m}_A"] for m in metrics]
    b_vals = [summary_row[f"{m}_B"] for m in metrics]

    fig, ax = plt.subplots(figsize=(9, 4))
    x = range(len(metrics))
    width = 0.38
    ax.bar([i - width / 2 for i in x], a_vals, width=width, label="A")
    ax.bar([i + width / 2 for i in x], b_vals, width=width, label="B")
    ax.set_xticks(list(x))
    ax.set_xticklabels([m.upper() for m in metrics])
    ax.set_title("Metric Comparison (A vs B)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    return fig


def plot_spend_sales_trend(df: pd.DataFrame, campaign_id: str):
    d = df[df["campaign_id"] == campaign_id] if campaign_id != "ALL" else df.copy()
    ts = d.groupby(["date", "variant"])[["spend", "sales"]].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    for variant in ["A", "B"]:
        z = ts[ts["variant"] == variant]
        ax.plot(z["date"], z["spend"], label=f"Spend {variant}", alpha=0.8)
        ax.plot(z["date"], z["sales"], label=f"Sales {variant}", alpha=0.8)
    ax.set_title("Spend vs Sales Trend")
    ax.legend(ncol=2, fontsize=8)
    ax.grid(alpha=0.25)
    return fig


def main():
    st.title("Ads Experimentation Analytics Platform")
    st.caption("Evaluate campaign changes: bidding, placements, and targeting updates.")

    df = load_data()
    comparison, overall, _tests = combine_analysis(df)

    campaign_options = ["ALL"] + sorted(df["campaign_id"].unique().tolist())
    selected_campaign = st.sidebar.selectbox("Select campaign", campaign_options, index=0)

    if selected_campaign == "ALL":
        row = overall.iloc[0]
    else:
        row = comparison[comparison["campaign_id"] == selected_campaign].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CTR", f"{row['ctr_B']:.2%}", f"{row['ctr_pct_change']:.2f}%")
    c2.metric("CVR", f"{row['cvr_B']:.2%}", f"{row['cvr_pct_change']:.2f}%")
    c3.metric("ROAS", f"{row['roas_B']:.2f}", f"{row['roas_pct_change']:.2f}%")
    c4.metric("CPC", f"{row['cpc_B']:.2f}", f"{row['cpc_pct_change']:.2f}%")

    st.subheader("Decision")
    st.write(f"**{row['decision']}**")

    st.subheader("Campaign-Level Comparison")
    show_cols = [
        "campaign_id",
        "decision",
        "ctr_pct_change",
        "cvr_pct_change",
        "cpc_pct_change",
        "roas_pct_change",
        "sales_pct_change",
        "spend_pct_change",
        "ctr_p_value",
        "cvr_p_value",
        "roas_p_value",
    ]
    st.dataframe(comparison[show_cols], use_container_width=True)

    st.subheader("Overall Experiment Result")
    st.dataframe(overall, use_container_width=True)

    st.subheader("Visualizations")
    st.pyplot(plot_funnel(df, selected_campaign))
    st.pyplot(plot_metric_comparison(row))
    st.pyplot(plot_spend_sales_trend(df, selected_campaign))


if __name__ == "__main__":
    main()
