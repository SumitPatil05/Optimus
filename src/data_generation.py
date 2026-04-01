from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _campaign_profiles(num_campaigns: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    campaigns = []
    effect_buckets = [
        "strong_win",
        "moderate_win",
        "risky_win",
        "loss",
        "neutral",
    ]
    for idx in range(num_campaigns):
        cid = f"CMP_{idx+1:03d}"
        profile = {
            "campaign_id": cid,
            "base_impressions": int(rng.integers(18000, 90000)),
            "base_ctr": float(rng.uniform(0.006, 0.035)),
            "base_cvr": float(rng.uniform(0.04, 0.18)),
            "base_cpc": float(rng.uniform(0.35, 1.9)),
            "base_aov": float(rng.uniform(18.0, 90.0)),
            "effect": effect_buckets[idx % len(effect_buckets)],
        }
        campaigns.append(profile)
    return pd.DataFrame(campaigns)


def _variant_adjustments(effect: str) -> dict[str, float]:
    if effect == "strong_win":
        return {"imp": 1.05, "ctr": 1.08, "cvr": 1.10, "cpc": 0.96, "aov": 1.04}
    if effect == "moderate_win":
        return {"imp": 1.03, "ctr": 1.04, "cvr": 1.05, "cpc": 0.99, "aov": 1.02}
    if effect == "risky_win":
        return {"imp": 1.06, "ctr": 1.12, "cvr": 0.98, "cpc": 1.04, "aov": 0.98}
    if effect == "loss":
        return {"imp": 1.02, "ctr": 0.96, "cvr": 0.93, "cpc": 1.08, "aov": 0.97}
    return {"imp": 1.00, "ctr": 1.00, "cvr": 1.00, "cpc": 1.00, "aov": 1.00}


def generate_campaign_data(
    num_campaigns: int = 10, total_days: int = 80, seed: int = 42
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    profiles = _campaign_profiles(num_campaigns=num_campaigns, seed=seed)
    dates = pd.date_range("2025-01-01", periods=total_days, freq="D")
    switch_day = total_days // 2

    rows = []
    for _, p in profiles.iterrows():
        adj = _variant_adjustments(p["effect"])
        for day_idx, dt in enumerate(dates):
            variant = "A" if day_idx < switch_day else "B"
            weekend_factor = 1.08 if dt.weekday() in [5, 6] else 1.0
            seasonality = 1.0 + 0.06 * np.sin(day_idx / 7.0)
            noise = float(rng.normal(1.0, 0.06))

            imp = p["base_impressions"] * weekend_factor * seasonality * noise
            ctr = p["base_ctr"] * float(rng.normal(1.0, 0.07))
            cvr = p["base_cvr"] * float(rng.normal(1.0, 0.06))
            cpc = p["base_cpc"] * float(rng.normal(1.0, 0.07))
            aov = p["base_aov"] * float(rng.normal(1.0, 0.05))

            if variant == "B":
                imp *= adj["imp"]
                ctr *= adj["ctr"]
                cvr *= adj["cvr"]
                cpc *= adj["cpc"]
                aov *= adj["aov"]

            impressions = max(1000, int(imp))
            clicks = max(0, int(impressions * max(0.001, ctr)))
            orders = max(0, int(clicks * max(0.001, cvr)))
            spend = round(clicks * max(0.05, cpc), 2)
            sales = round(orders * max(5.0, aov), 2)

            rows.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "campaign_id": p["campaign_id"],
                    "variant": variant,
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": spend,
                    "orders": orders,
                    "sales": sales,
                }
            )

    return pd.DataFrame(rows).sort_values(["date", "campaign_id"]).reset_index(drop=True)


def save_generated_data(path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_campaign_data(num_campaigns=10, total_days=80, seed=42)
    df.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "data" / "campaign_data.csv"
    save_generated_data(output)
    print(f"Generated: {output}")
