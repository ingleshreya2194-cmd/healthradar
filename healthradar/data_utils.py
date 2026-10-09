"""
data_utils.py
-------------
Small helper functions to load the CSV files and build the numbers the
risk classifier needs. Used by app.py and train_model.py.
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

DISEASES = ["Dengue", "Influenza", "COVID-19"]
RISK_LEVELS = ["Low", "Medium", "High"]
RISK_ORDER = {"Low": 0, "Medium": 1, "High": 2}

# The columns the classifier learns from
FEATURES = ["cases_4w", "growth_rate", "population", "cases_per_100k"]


def load_csv(name):
    """Load a CSV from /data. Raises a clear error if the file is missing."""
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing data file: data/{name}. Run: python generate_sample_data.py"
        )
    return pd.read_csv(path)


def region_features(cases_df, region_col, pop_lookup):
    """
    For every region + disease, compute the features for the LATEST week:
    cases in last 4 weeks, growth rate, population, cases per 100k.
    Returns a DataFrame with one row per region + disease.
    """
    rows = []
    for (region, disease), g in cases_df.groupby([region_col, "disease"]):
        g = g.sort_values("date")
        c = g["cases"].to_numpy()
        if len(c) < 4:
            continue
        pop = pop_lookup.get(region)
        if not pop:
            continue
        last2, prev2 = c[-2:].sum(), c[-4:-2].sum()
        growth = (last2 - prev2) / max(prev2, 1)
        cases_4w = c[-4:].sum()
        rows.append({
            "region": region, "disease": disease, "date": g["date"].iloc[-1],
            "cases_4w": int(cases_4w), "growth_rate": float(growth),
            "population": int(pop),
            "cases_per_100k": float(cases_4w / pop * 100000),
            "latest_cases": int(c[-1]),
        })
    return pd.DataFrame(rows)


def rule_risk(per100k, growth):
    """Fallback rule (same as the sample-label rule) if the model file is missing."""
    if per100k >= 40 or (per100k >= 25 and growth >= 0.30):
        return "High"
    if per100k >= 12 or (per100k >= 6 and growth >= 0.25):
        return "Medium"
    return "Low"
