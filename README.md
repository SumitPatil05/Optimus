# Ads Experimentation Analytics Platform

End-to-end analytics project that simulates how a performance marketing team (Amazon Ads / e-commerce) evaluates campaign optimizations.

It compares **Variant A (before change)** vs **Variant B (after change)** across business KPIs, statistical significance, and decision-oriented outcomes.

## Real-World Context

Teams often change campaign levers such as:
- Bid strategy
- Placement multipliers
- Targeting refinement

These changes can improve efficiency for some campaigns while hurting others. This project mirrors that reality by generating mixed outcomes across campaigns.

## Project Structure

```text
ads-experimentation/
│
├── data/
│   └── campaign_data.csv
│
├── src/
│   ├── data_generation.py
│   ├── metrics.py
│   ├── experiment_analysis.py
│   ├── statistical_tests.py
│   └── utils.py
│
├── app/
│   └── app.py
│
├── requirements.txt
└── README.md
```

## KPI Definitions

- `CTR = clicks / impressions`
- `CVR = orders / clicks`
- `CPC = spend / clicks`
- `ROAS = sales / spend`
- `ACOS = spend / sales`
- `AOV = sales / orders`

## Experiment Logic

1. Generate campaign-level daily data for 10 campaigns over 80 days.
2. First half of days are assigned to Variant A, second half to Variant B.
3. Campaigns are assigned mixed impact profiles:
   - strong win
   - moderate win
   - risky win
   - loss
   - neutral
4. Compute KPI deltas (% change) per campaign and overall.
5. Apply statistical testing:
   - Z-test for CTR and CVR
   - Welch t-test for ROAS daily series

## Decision Framework

Each campaign receives a practical decision tag:

- **Strong Win**: ROAS up and CVR up
- **Risky Win**: CTR up but ROAS down
- **Loss**: Spend up while Sales flat/down or ROAS down
- **Neutral**: none of the above

## Example Insights You Can Expect

- Campaigns with higher CTR may still be inefficient if ROAS declines.
- Some campaigns can show statistically significant CTR gains but no business gain.
- A strong winner often combines CVR and ROAS growth, not just traffic growth.
- Overall roll-up can hide campaign-level losers; always inspect per-campaign outcomes.

## Setup

```bash
cd ads-experimentation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate Data

```bash
python src/data_generation.py
```

Creates `data/campaign_data.csv`.

## Run Analysis in Python

```python
import pandas as pd
from src.metrics import add_row_level_metrics
from src.experiment_analysis import combine_analysis

df = pd.read_csv("data/campaign_data.csv")
df = add_row_level_metrics(df)
comparison, overall, tests = combine_analysis(df)
print(comparison.head())
print(overall)
```

## Launch Streamlit Dashboard

```bash
streamlit run app/app.py
```

Dashboard includes:
- KPI cards (CTR, CVR, ROAS, CPC)
- Campaign-level A vs B comparison with p-values
- Decision output per campaign
- Overall experiment outcome
- Matplotlib charts:
  - Funnel comparison
  - Metric comparison
  - Spend vs sales trend

## Notes

- Synthetic data is deterministic with a fixed random seed for reproducibility.
- The focus is business decision quality, not only statistical output.
