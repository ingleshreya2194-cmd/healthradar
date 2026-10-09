# HealthRadar

A disease awareness and trend prediction web app for **SDG 3: Good Health and Well-being**.
It covers **Dengue, Influenza (Flu) and COVID-19**.

> **All data in this project is SAMPLE data** (made up for demonstration). The app labels it as sample data on every page. See "Using real data" below.
>
> This app gives general information only and is not medical advice. Consult a doctor for diagnosis and treatment.

## Features

- **Home page** with the WHO photo as the hero, and risk cards for every country (green = Low, yellow = Medium, red = High). Search, filter by disease or risk level, and click a country to open a side panel with the case trend, a 4-week forecast and a travel advisory note.
- **Travel Check**: choose a destination to see active diseases, risk level and precautions.
- **Local Mode**: uses the browser location to find the nearest state (falls back to a state drop-down if permission is denied). Shows which diseases have the most cases, recent weekly records, the data date, and a forecast.
- **Disease pages** for Dengue, Flu and COVID-19: symptoms, how it spreads, prevention, medical care, home comfort measures, and a "See a doctor immediately if..." box.
- **Machine learning**
  - Forecast of weekly cases for the next 4 weeks per country and state.
  - Random Forest risk classifier (Low / Medium / High) using cases, growth rate and population. Accuracy and confusion matrix are on the **Model Info** page.

## Setup and run

You need Python 3.10 or newer.

```bash
# 1. (optional) make a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install the libraries
pip install -r requirements.txt

# 3. train the models (saves files in /models)
python train_model.py

# 4. start the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

If the `data/` folder is empty, create the sample files first with `python generate_sample_data.py`.

## Project structure

```
healthradar/
  app.py                  Flask server: pages and API endpoints
  train_model.py          trains the risk classifier and pre-computes forecasts (joblib)
  forecast.py             forecasting code (ARIMA if statsmodels is installed, else a simple lag model)
  data_utils.py           helper functions to load CSVs and build model features
  diseases.py             disease awareness text (edit content here)
  generate_sample_data.py creates the SAMPLE CSV files
  requirements.txt
  data/                   CSV files (+ README_DATA.md describing every column)
  models/                 saved models: risk_model.joblib, forecasts.joblib, metrics.json
  static/css/style.css    styling (mobile first)
  static/js/              main.js (helpers), charts.js (SVG chart), home.js, travel.js, local.js, model.js
  static/img/who-hero.jpg hero image on the home page
  templates/              HTML pages (base, index, travel, local, disease, model_info, error)
```

## API endpoints

| Endpoint | What it returns |
|----------|-----------------|
| `/api/countries` | All countries with overall risk and per-disease numbers |
| `/api/country/<name>` | One country: risk, advisory text and 26-week trend per disease |
| `/api/forecast/<region>?disease=Dengue` | Recent weekly cases and the 4-week forecast for a country or state |
| `/api/risk/<region>` | Risk level for each disease in a country or state |
| `/api/disease/<name>` | Awareness content for `dengue`, `influenza` (or `flu`), `covid-19` |
| `/api/states` | State list (for the Local Mode drop-down) |
| `/api/local?state=Goa` or `?lat=..&lon=..` | Local Mode data for a state |
| `/api/model-info` | Accuracy, confusion matrix and feature importance |

## Using real data

1. Download data from WHO (data.who.int), CDC (data.cdc.gov) or disease.sh.
2. Convert it to the same columns as the sample files (see `data/README_DATA.md`) and replace the CSVs in `data/`.
3. Set `DATA_IS_SAMPLE = False` in `app.py` (this removes the sample-data labels).
4. For `data/risk_training.csv`, use risk labels from health authorities if you have them. The sample labels come from a simple rule.
5. Run `python train_model.py` again.

## Notes for explaining the project

- **Sample risk labels come from a simple rule**, so the high accuracy on the Model Info page only proves the pipeline works. It is not a claim about real-world accuracy.
- The model is tested on the **newest 26 weeks**, not a random split, because a real app has to predict the future.
- **Local Mode** picks the nearest state centre from your coordinates, so it can be wrong near state borders. The drop-down lets the user correct it. It currently has sample data for 20 Indian states; add more rows to `states.csv` and `state_cases.csv` to extend it.
- Forecasts use ARIMA when `statsmodels` is installed; otherwise a Ridge regression on the last 8 weeks. The method used is shown in `/api/forecast/...` and on the Model Info page.
- Medical text in `diseases.py` follows general WHO and CDC public guidance. Home measures are comfort measures only. Have a medical professional review the text before any public use.
