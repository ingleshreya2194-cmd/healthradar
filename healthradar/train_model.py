"""
train_model.py
--------------
Run this ONE time (and again whenever you change the data):

    python train_model.py

It does two things:
1. Trains a Random Forest that classifies a region as Low / Medium / High risk
   using: cases in the last 4 weeks, growth rate, population, cases per 100k.
   Saves the model and its accuracy / confusion matrix.
2. Pre-computes 4-week case forecasts for every country and state, so the
   app can show forecast charts instantly.

Files written to /models:  risk_model.joblib, metrics.json, forecasts.joblib
"""

import json
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

from data_utils import (DISEASES, FEATURES, MODEL_DIR, RISK_LEVELS, load_csv)
from forecast import forecast_series, HAVE_STATSMODELS

FORECAST_WEEKS = 4
TEST_WEEKS = 26  # the most recent 26 weeks are kept aside to test the model


def train_risk_classifier():
    """Step 1: train and evaluate the Random Forest."""
    data = load_csv("risk_training.csv")
    data = data.dropna(subset=FEATURES + ["risk_level"])

    # Split by TIME (not randomly): train on older weeks, test on newer weeks.
    # This is more honest, because a real app must predict the future.
    dates = sorted(data["date"].unique())
    cutoff = dates[-TEST_WEEKS]
    train = data[data["date"] < cutoff]
    test = data[data["date"] >= cutoff]
    print(f"Training rows: {len(train)}, test rows: {len(test)}")

    model = RandomForestClassifier(
        n_estimators=150, max_depth=10, random_state=42,
        class_weight="balanced",  # High risk rows are rare, so give them more weight
        n_jobs=-1,
    )
    model.fit(train[FEATURES], train["risk_level"])

    predicted = model.predict(test[FEATURES])
    accuracy = accuracy_score(test["risk_level"], predicted)
    cm = confusion_matrix(test["risk_level"], predicted, labels=RISK_LEVELS)
    report = classification_report(
        test["risk_level"], predicted, labels=RISK_LEVELS,
        output_dict=True, zero_division=0,
    )
    importance = dict(zip(FEATURES, [round(float(x), 4) for x in model.feature_importances_]))

    print(f"Accuracy on test weeks: {accuracy:.3f}")
    print("Confusion matrix (rows = real, columns = predicted):")
    print(pd.DataFrame(cm, index=RISK_LEVELS, columns=RISK_LEVELS))

    # Re-train on ALL data before saving, so the final model uses everything
    model.fit(data[FEATURES], data["risk_level"])
    joblib.dump(model, os.path.join(MODEL_DIR, "risk_model.joblib"))

    metrics = {
        "model": "Random Forest (150 trees)",
        "features": FEATURES,
        "labels": RISK_LEVELS,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "test_period_start": str(cutoff),
        "accuracy": round(float(accuracy), 4),
        "confusion_matrix": cm.tolist(),
        "per_class": {k: {m: round(float(v[m]), 3) for m in ("precision", "recall", "f1-score")}
                      for k, v in report.items() if k in RISK_LEVELS},
        "feature_importance": importance,
        "forecast_method": "ARIMA(2,1,1)" if HAVE_STATSMODELS else "lag-regression",
        "note": ("Risk labels in the SAMPLE data come from a simple rule, so a high "
                 "accuracy here only shows the pipeline works. It is not a claim about "
                 "real-world performance. Use official alert levels as labels with real data."),
    }
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)


def train_forecasts():
    """Step 2: forecast the next weeks for every region + disease."""
    results = {}
    for file, region_col in (("country_cases.csv", "country"), ("state_cases.csv", "state")):
        df = load_csv(file)
        for (region, disease), g in df.groupby([region_col, "disease"]):
            g = g.sort_values("date")
            try:
                out = forecast_series(g["cases"].tolist(), FORECAST_WEEKS)
            except Exception as err:  # skip a region if it has too little data
                print(f"  skipped {region}/{disease}: {err}")
                continue
            # Forecast dates = the next weekly dates after the last real date
            last = pd.Timestamp(g["date"].iloc[-1])
            out["dates"] = [(last + pd.Timedelta(weeks=i + 1)).strftime("%Y-%m-%d")
                            for i in range(FORECAST_WEEKS)]
            results[(region, disease)] = out
    joblib.dump(results, os.path.join(MODEL_DIR, "forecasts.joblib"))
    print(f"Saved forecasts for {len(results)} region/disease pairs.")


if __name__ == "__main__":
    os.makedirs(MODEL_DIR, exist_ok=True)
    train_risk_classifier()
    train_forecasts()
    print("Done. Models saved in /models.")
