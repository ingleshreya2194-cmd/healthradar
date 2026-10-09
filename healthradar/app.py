"""
app.py
------
HealthRadar - Flask backend.

Run:  python app.py      then open  http://127.0.0.1:5000

Pages:    /  /travel  /local  /disease/<name>  /model-info
API:      /api/countries            list of countries with risk levels
          /api/country/<name>       full details for one country (used by side panel and travel check)
          /api/forecast/<region>    history + forecast (?disease=Dengue)
          /api/risk/<region>        risk level per disease for a country or state
          /api/disease/<name>       awareness content for a disease
          /api/states, /api/local   local mode (state list, nearest state from location)
          /api/model-info           accuracy and confusion matrix
All data is SAMPLE data until you replace the CSV files in /data.
"""

import json
import math
import os

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

from data_utils import (DISEASES, FEATURES, MODEL_DIR, RISK_ORDER, RISK_LEVELS,
                        load_csv, region_features, rule_risk)
from diseases import DISCLAIMER, DISEASE_INFO, HOME_CARE_NOTE, get_disease_by_name
from forecast import forecast_series

app = Flask(__name__)

# Change this to False when you connect real data
DATA_IS_SAMPLE = True


# ---------------------------------------------------------------------------
# Load data and models once when the server starts
# ---------------------------------------------------------------------------
def load_everything():
    """Load CSVs and models. Problems are collected so the app can still start."""
    store = {"errors": []}
    try:
        store["countries"] = load_csv("countries.csv")
        store["country_cases"] = load_csv("country_cases.csv")
        store["states"] = load_csv("states.csv")
        store["state_cases"] = load_csv("state_cases.csv")
        store["advisories"] = load_csv("advisories.csv")
    except Exception as err:
        store["errors"].append(str(err))
        return store

    # Trained models are optional: the app falls back to simple rules / live forecasts
    try:
        store["model"] = joblib.load(os.path.join(MODEL_DIR, "risk_model.joblib"))
    except Exception:
        store["model"] = None
        store["errors"].append("Risk model not found. Run: python train_model.py (using fallback rules).")
    try:
        store["forecasts"] = joblib.load(os.path.join(MODEL_DIR, "forecasts.joblib"))
    except Exception:
        store["forecasts"] = {}
    try:
        with open(os.path.join(MODEL_DIR, "metrics.json")) as f:
            store["metrics"] = json.load(f)
    except Exception:
        store["metrics"] = None

    # Work out the latest risk level for every country / state and disease
    country_pop = dict(zip(store["countries"]["country"], store["countries"]["population"]))
    state_pop = dict(zip(store["states"]["state"], store["states"]["population"]))
    store["country_feat"] = add_risk(region_features(store["country_cases"], "country", country_pop), store["model"])
    store["state_feat"] = add_risk(region_features(store["state_cases"], "state", state_pop), store["model"])
    return store


def add_risk(feat, model):
    """Add a 'risk' column (Low/Medium/High) using the ML model, or rules if no model."""
    if feat.empty:
        feat["risk"] = []
        return feat
    if model is not None:
        feat["risk"] = model.predict(feat[FEATURES])
    else:
        feat["risk"] = [rule_risk(r.cases_per_100k, r.growth_rate) for r in feat.itertuples()]
    return feat


DB = load_everything()


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def data_ready():
    """True if the CSV files loaded correctly."""
    return "country_cases" in DB


def find_name(wanted, names):
    """Match a name ignoring upper/lower case. Returns the real name or None."""
    wanted = (wanted or "").strip().lower()
    for n in names:
        if n.lower() == wanted:
            return n
    return None


def overall_risk(risks):
    """A region's overall risk = the highest risk among its diseases."""
    if not len(risks):
        return "Low"
    return max(risks, key=lambda r: RISK_ORDER[r])


def advisory_text(disease, risk):
    """Look up the short travel advisory for a disease and risk level."""
    adv = DB["advisories"]
    row = adv[(adv["disease"] == disease) & (adv["risk_level"] == risk)]
    return row["advisory"].iloc[0] if len(row) else "No advisory available."


def disease_rows(feat, region):
    """Per-disease numbers for one region, as a list of dicts (sorted by cases)."""
    sub = feat[feat["region"] == region]
    out = []
    for r in sub.itertuples():
        out.append({
            "disease": r.disease, "risk": r.risk,
            "cases_4w": int(r.cases_4w), "latest_week_cases": int(r.latest_cases),
            "cases_per_100k": round(r.cases_per_100k, 2),
            "growth_pct": round(r.growth_rate * 100, 1),
            "date": r.date,
        })
    return sorted(out, key=lambda d: d["cases_4w"], reverse=True)


def history(cases_df, region_col, region, disease, weeks=26):
    """Last N weeks of real (sample) cases for a chart."""
    g = cases_df[(cases_df[region_col] == region) & (cases_df["disease"] == disease)]
    g = g.sort_values("date").tail(weeks)
    return [{"date": d, "cases": int(c)} for d, c in zip(g["date"], g["cases"])]


def error(message, code=404):
    """Return a simple JSON error."""
    return jsonify({"error": message}), code


@app.before_request
def check_data():
    """If CSV files are missing, show a clear message instead of crashing."""
    if not data_ready() and request.endpoint not in ("static",):
        msg = DB["errors"][0] if DB["errors"] else "Data not loaded."
        if request.path.startswith("/api/"):
            return error(msg, 500)
        return render_template("error.html", message=msg, disclaimer=DISCLAIMER), 500


@app.context_processor
def inject_globals():
    """Values every template can use (disclaimer, sample-data flag, disease list)."""
    return {"disclaimer": DISCLAIMER, "data_is_sample": DATA_IS_SAMPLE,
            "disease_names": [(d, DISEASE_INFO[d]["slug"]) for d in DISEASES]}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/travel")
def travel():
    return render_template("travel.html")


@app.route("/local")
def local():
    return render_template("local.html")


@app.route("/disease/<name>")
def disease_page(name):
    found = get_disease_by_name(name)
    if not found:
        return render_template("error.html", message="Disease not found."), 404
    disease, info = found
    return render_template("disease.html", disease=disease, info=info, home_note=HOME_CARE_NOTE)


@app.route("/model-info")
def model_info_page():
    return render_template("model_info.html")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.route("/api/countries")
def api_countries():
    """All countries with overall risk, plus per-disease numbers."""
    out = []
    latest = DB["country_cases"]["date"].max()
    for c in DB["countries"].itertuples():
        rows = disease_rows(DB["country_feat"], c.country)
        out.append({
            "country": c.country, "iso3": c.iso3, "continent": c.continent,
            "population": int(c.population), "lat": c.lat, "lon": c.lon,
            "risk": overall_risk([r["risk"] for r in rows]),
            "diseases": rows,
        })
    return jsonify({"sample_data": DATA_IS_SAMPLE, "data_date": latest, "countries": out})


@app.route("/api/country/<name>")
def api_country(name):
    """Details for one country: per-disease risk, advisory text and 26-week trend."""
    country = find_name(name, DB["countries"]["country"])
    if not country:
        return error(f"Country '{name}' not found.")
    rows = disease_rows(DB["country_feat"], country)
    for r in rows:
        r["advisory"] = advisory_text(r["disease"], r["risk"])
        r["trend"] = history(DB["country_cases"], "country", country, r["disease"])
    return jsonify({
        "country": country, "sample_data": DATA_IS_SAMPLE,
        "data_date": DB["country_cases"]["date"].max(),
        "risk": overall_risk([r["risk"] for r in rows]),
        "diseases": rows,
    })


@app.route("/api/forecast/<region>")
def api_forecast(region):
    """History + forecast for a country or state. Use ?disease=Dengue."""
    disease = request.args.get("disease", "Dengue")
    disease = find_name(disease, DISEASES)
    if not disease:
        return error("Unknown disease. Use Dengue, Influenza or COVID-19.", 400)

    # Is it a country or a state?
    name = find_name(region, DB["countries"]["country"])
    if name:
        df, col = DB["country_cases"], "country"
    else:
        name = find_name(region, DB["states"]["state"])
        df, col = DB["state_cases"], "state"
    if not name:
        return error(f"Region '{region}' not found.")

    hist = history(df, col, name, disease, weeks=26)
    fc = DB["forecasts"].get((name, disease))
    if fc is None:  # not pre-computed: fit now
        try:
            g = df[(df[col] == name) & (df["disease"] == disease)].sort_values("date")
            fc = forecast_series(g["cases"].tolist(), 4)
            last = pd.Timestamp(g["date"].iloc[-1])
            fc["dates"] = [(last + pd.Timedelta(weeks=i + 1)).strftime("%Y-%m-%d") for i in range(4)]
        except Exception as err:
            return error(f"Could not forecast: {err}", 500)

    return jsonify({
        "region": name, "disease": disease, "sample_data": DATA_IS_SAMPLE,
        "history": hist,
        "forecast": [{"date": d, "predicted": p, "lower": lo, "upper": up}
                     for d, p, lo, up in zip(fc["dates"], fc["predicted"], fc["lower"], fc["upper"])],
        "method": fc["method"],
    })


@app.route("/api/risk/<region>")
def api_risk(region):
    """Risk level (Low/Medium/High) for each disease in a country or state."""
    name = find_name(region, DB["countries"]["country"])
    feat = DB["country_feat"]
    if not name:
        name = find_name(region, DB["states"]["state"])
        feat = DB["state_feat"]
    if not name:
        return error(f"Region '{region}' not found.")
    rows = disease_rows(feat, name)
    return jsonify({"region": name, "sample_data": DATA_IS_SAMPLE,
                    "risk": overall_risk([r["risk"] for r in rows]), "diseases": rows})


@app.route("/api/disease/<name>")
def api_disease(name):
    """Awareness content (symptoms, prevention, warning signs...) for a disease."""
    found = get_disease_by_name(name)
    if not found:
        return error(f"Disease '{name}' not found.")
    disease, info = found
    return jsonify({"disease": disease, "disclaimer": DISCLAIMER,
                    "home_care_note": HOME_CARE_NOTE, **info})


@app.route("/api/states")
def api_states():
    """List of states for the fallback dropdown."""
    s = DB["states"].sort_values("state")
    return jsonify({"states": [{"state": r.state, "country": r.country} for r in s.itertuples()]})


def distance_km(lat1, lon1, lat2, lon2):
    """Straight-line distance between two points on Earth (haversine formula)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


MAX_STATE_DISTANCE_KM = 1000  # if the nearest state is farther than this, ask the user to choose


@app.route("/api/local")
def api_local():
    """
    Local mode. Give either ?state=Name  or  ?lat=..&lon=..
    With lat/lon we pick the NEAREST state centre (approximate).
    """
    state = None
    detected = False
    if request.args.get("state"):
        state = find_name(request.args["state"], DB["states"]["state"])
        if not state:
            return error("State not found.")
    else:
        try:
            lat, lon = float(request.args["lat"]), float(request.args["lon"])
        except (KeyError, ValueError):
            return error("Send a state name, or lat and lon.", 400)
        best, best_d = None, None
        for s in DB["states"].itertuples():
            d = distance_km(lat, lon, s.lat, s.lon)
            if best_d is None or d < best_d:
                best, best_d = s.state, d
        if best_d is None or best_d > MAX_STATE_DISTANCE_KM:
            return error("No supported region near your location. Please choose a state.", 404)
        state, detected = best, True

    rows = disease_rows(DB["state_feat"], state)
    sc = DB["state_cases"]
    sc = sc[sc["state"] == state]
    last_dates = sorted(sc["date"].unique())[-8:][::-1]  # newest first
    table = []
    for d in last_dates:
        entry = {"date": d}
        for dis in DISEASES:
            v = sc[(sc["date"] == d) & (sc["disease"] == dis)]["cases"]
            entry[dis] = int(v.iloc[0]) if len(v) else None
        table.append(entry)

    return jsonify({
        "state": state, "detected_from_location": detected, "sample_data": DATA_IS_SAMPLE,
        "data_date": sc["date"].max(),
        "risk": overall_risk([r["risk"] for r in rows]),
        "diseases": rows,  # already sorted: most cases first
        "recent_records": table,
    })


@app.route("/api/model-info")
def api_model_info():
    """Accuracy, confusion matrix and other facts about the trained model."""
    if not DB.get("metrics"):
        return error("Model not trained yet. Run: python train_model.py", 404)
    return jsonify(DB["metrics"])


if __name__ == "__main__":
    for e in DB["errors"]:
        print("WARNING:", e)
    app.run(debug=True)
