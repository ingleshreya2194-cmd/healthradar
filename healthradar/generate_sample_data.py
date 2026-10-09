"""
generate_sample_data.py
-----------------------
Creates SAMPLE (made-up but realistic-looking) CSV files in the /data folder.

IMPORTANT: This is NOT real surveillance data. It exists so the app can run
before real data is connected. To use real data, replace the CSV files in
/data with files that have the SAME COLUMN NAMES (see data/README_DATA.md).
Good real sources: WHO (https://data.who.int), CDC (https://data.cdc.gov),
and disease.sh (https://disease.sh).

Run:  python generate_sample_data.py
"""

import os
import numpy as np
import pandas as pd

# Fixed seed so everyone gets the same sample data every time
rng = np.random.default_rng(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# The last week of data (a Sunday). Data is weekly.
LAST_WEEK = pd.Timestamp("2026-10-04")
N_WEEKS = 104  # two years of history
WEEKS = pd.date_range(end=LAST_WEEK, periods=N_WEEKS, freq="W-SUN")

DISEASES = ["Dengue", "Influenza", "COVID-19"]

# ---------------------------------------------------------------------------
# 1) Countries: name, ISO code, continent, population (approx.), lat, lon,
#    and a "climate" tag used only to shape the sample dengue/flu seasons.
# ---------------------------------------------------------------------------
COUNTRIES = [
    # country, iso3, continent, population, lat, lon, climate
    ("India", "IND", "Asia", 1428000000, 20.6, 78.9, "tropical"),
    ("Bangladesh", "BGD", "Asia", 172000000, 23.7, 90.4, "tropical"),
    ("Pakistan", "PAK", "Asia", 240000000, 30.4, 69.3, "tropical"),
    ("Sri Lanka", "LKA", "Asia", 22000000, 7.9, 80.8, "tropical"),
    ("Thailand", "THA", "Asia", 72000000, 15.9, 100.99, "tropical"),
    ("Vietnam", "VNM", "Asia", 99000000, 14.1, 108.3, "tropical"),
    ("Indonesia", "IDN", "Asia", 277000000, -0.8, 113.9, "tropical"),
    ("Philippines", "PHL", "Asia", 117000000, 12.9, 121.8, "tropical"),
    ("Malaysia", "MYS", "Asia", 34000000, 4.2, 101.98, "tropical"),
    ("Singapore", "SGP", "Asia", 5900000, 1.35, 103.8, "tropical"),
    ("China", "CHN", "Asia", 1412000000, 35.9, 104.2, "temperate_north"),
    ("Japan", "JPN", "Asia", 124000000, 36.2, 138.3, "temperate_north"),
    ("United Arab Emirates", "ARE", "Asia", 9500000, 23.4, 53.8, "arid"),
    ("Brazil", "BRA", "South America", 216000000, -14.2, -51.9, "tropical_south"),
    ("Argentina", "ARG", "South America", 46000000, -38.4, -63.6, "temperate_south"),
    ("Colombia", "COL", "South America", 52000000, 4.6, -74.1, "tropical_south"),
    ("Peru", "PER", "South America", 34000000, -9.2, -75.0, "tropical_south"),
    ("Mexico", "MEX", "North America", 128000000, 23.6, -102.6, "tropical"),
    ("United States", "USA", "North America", 335000000, 37.1, -95.7, "temperate_north"),
    ("Canada", "CAN", "North America", 40000000, 56.1, -106.3, "temperate_north"),
    ("United Kingdom", "GBR", "Europe", 67000000, 55.4, -3.4, "temperate_north"),
    ("France", "FRA", "Europe", 68000000, 46.2, 2.2, "temperate_north"),
    ("Germany", "DEU", "Europe", 84000000, 51.2, 10.5, "temperate_north"),
    ("Italy", "ITA", "Europe", 59000000, 41.9, 12.6, "temperate_north"),
    ("Russia", "RUS", "Europe", 144000000, 61.5, 105.3, "temperate_north"),
    ("Nigeria", "NGA", "Africa", 224000000, 9.1, 8.7, "tropical"),
    ("Kenya", "KEN", "Africa", 55000000, -0.02, 37.9, "tropical"),
    ("Ethiopia", "ETH", "Africa", 126000000, 9.1, 40.5, "tropical"),
    ("South Africa", "ZAF", "Africa", 60000000, -30.6, 22.9, "temperate_south"),
    ("Egypt", "EGY", "Africa", 112000000, 26.8, 30.8, "arid"),
    ("Australia", "AUS", "Oceania", 26000000, -25.3, 133.8, "temperate_south"),
    ("New Zealand", "NZL", "Oceania", 5200000, -40.9, 174.9, "temperate_south"),
]

countries_df = pd.DataFrame(
    COUNTRIES,
    columns=["country", "iso3", "continent", "population", "lat", "lon", "climate"],
)


# ---------------------------------------------------------------------------
# Helper: build a weekly curve = baseline * seasonal wave * noise
# ---------------------------------------------------------------------------
def week_of_year(dates):
    """Week number 1..52 for each date."""
    return dates.isocalendar().week.to_numpy().astype(float)


def seasonal_wave(dates, peak_week, sharpness=2.0):
    """A smooth yearly wave that peaks at 'peak_week' (1..52)."""
    w = week_of_year(dates)
    angle = 2 * np.pi * (w - peak_week) / 52.0
    wave = (np.cos(angle) + 1) / 2          # 0..1
    return wave ** sharpness                # make the peak sharper


def make_series(dates, disease, climate, population, region_scale=1.0):
    """
    Returns an array of weekly case counts for one place + disease.
    Numbers are SAMPLE values only.
    """
    n = len(dates)
    t = np.arange(n)

    if disease == "Dengue":
        # Dengue: high in tropical places, rainy season peak, almost none elsewhere
        if climate in ("tropical", "tropical_south"):
            peak = 36 if climate == "tropical" else 10   # northern vs southern rains
            base_per100k = 4.0
            wave = 0.15 + seasonal_wave(dates, peak, 2.5) * 1.6
        elif climate == "arid":
            base_per100k = 0.15
            wave = 0.5 + seasonal_wave(dates, 38, 2.0)
        else:
            base_per100k = 0.02   # imported cases only
            wave = 0.5 + seasonal_wave(dates, 36, 2.0)
        trend = 1 + 0.002 * t     # slight rise over time
    elif disease == "Influenza":
        # Flu: winter peaks. North = ~week 3, South = ~week 30, tropics = mild
        if climate in ("temperate_north",):
            peak, base_per100k, amp = 3, 5.0, 3.0
        elif climate == "temperate_south":
            peak, base_per100k, amp = 30, 5.0, 3.0
        elif climate == "tropical":
            peak, base_per100k, amp = 30, 2.5, 1.2   # monsoon-linked
        elif climate == "tropical_south":
            peak, base_per100k, amp = 24, 2.5, 1.2
        else:
            peak, base_per100k, amp = 2, 2.0, 1.5
        wave = 0.2 + seasonal_wave(dates, peak, 2.0) * amp
        trend = np.ones(n)
    else:
        # COVID-19: irregular waves, overall lower than early pandemic
        base_per100k = 3.0
        wave = (
            0.4
            + 1.2 * np.exp(-((t - n * 0.25) ** 2) / (2 * 6 ** 2))
            + 1.6 * np.exp(-((t - n * 0.62) ** 2) / (2 * 7 ** 2))
            + 1.0 * np.exp(-((t - n * 0.92) ** 2) / (2 * 4 ** 2))
        )
        trend = np.ones(n)

    expected = population / 100000.0 * base_per100k * wave * trend * region_scale
    # Random noise (about +/- 15%) and a small chance of a reporting dip
    noise = rng.normal(1.0, 0.15, size=n).clip(0.5, 1.6)
    cases = expected * noise
    cases = np.maximum(cases, 0)
    return np.round(cases).astype(int)


# ---------------------------------------------------------------------------
# 2) Country weekly cases  ->  data/country_cases.csv
# ---------------------------------------------------------------------------
rows = []
for _, c in countries_df.iterrows():
    # Each country gets a small random "intensity" so they are not identical
    intensity = rng.uniform(0.5, 1.8)
    for disease in DISEASES:
        cases = make_series(WEEKS, disease, c["climate"], c["population"], intensity)
        for d, v in zip(WEEKS, cases):
            rows.append((d.strftime("%Y-%m-%d"), c["country"], c["iso3"], disease, int(v)))

country_cases = pd.DataFrame(rows, columns=["date", "country", "iso3", "disease", "cases"])
country_cases.to_csv(os.path.join(DATA_DIR, "country_cases.csv"), index=False)

# Save the country list (without the helper 'climate' column)
countries_df.drop(columns=["climate"]).to_csv(
    os.path.join(DATA_DIR, "countries.csv"), index=False
)

# ---------------------------------------------------------------------------
# 3) India states (for Local Mode)  ->  data/states.csv + data/state_cases.csv
#    lat/lon = approximate centre of each state, used to find the nearest
#    state from the browser location (and as a fallback dropdown list).
#    You can add more countries' states later using the same columns.
# ---------------------------------------------------------------------------
STATES = [
    # state, country, population (approx.), lat, lon, climate
    ("Maharashtra", "India", 126000000, 19.7, 75.7, "tropical"),
    ("Karnataka", "India", 68000000, 15.3, 75.7, "tropical"),
    ("Tamil Nadu", "India", 78000000, 11.1, 78.7, "tropical"),
    ("Kerala", "India", 35000000, 10.9, 76.3, "tropical"),
    ("Telangana", "India", 38000000, 18.1, 79.0, "tropical"),
    ("Andhra Pradesh", "India", 54000000, 15.9, 79.7, "tropical"),
    ("Gujarat", "India", 71000000, 22.3, 71.2, "tropical"),
    ("Rajasthan", "India", 81000000, 27.0, 74.2, "tropical"),
    ("Madhya Pradesh", "India", 85000000, 22.9, 78.7, "tropical"),
    ("Uttar Pradesh", "India", 237000000, 26.8, 80.9, "tropical"),
    ("Bihar", "India", 130000000, 25.1, 85.3, "tropical"),
    ("West Bengal", "India", 100000000, 22.9, 87.9, "tropical"),
    ("Odisha", "India", 46000000, 20.9, 84.0, "tropical"),
    ("Punjab", "India", 31000000, 31.1, 75.3, "tropical"),
    ("Haryana", "India", 29000000, 29.1, 76.1, "tropical"),
    ("Delhi", "India", 21000000, 28.7, 77.1, "tropical"),
    ("Assam", "India", 35000000, 26.2, 92.9, "tropical"),
    ("Jharkhand", "India", 39000000, 23.6, 85.3, "tropical"),
    ("Chhattisgarh", "India", 30000000, 21.3, 81.9, "tropical"),
    ("Goa", "India", 1600000, 15.3, 74.1, "tropical"),
]
states_df = pd.DataFrame(
    STATES, columns=["state", "country", "population", "lat", "lon", "climate"]
)

rows = []
for _, s in states_df.iterrows():
    intensity = rng.uniform(0.5, 2.0)
    for disease in DISEASES:
        cases = make_series(WEEKS, disease, s["climate"], s["population"], intensity)
        for d, v in zip(WEEKS, cases):
            rows.append((d.strftime("%Y-%m-%d"), s["state"], s["country"], disease, int(v)))

state_cases = pd.DataFrame(rows, columns=["date", "state", "country", "disease", "cases"])
state_cases.to_csv(os.path.join(DATA_DIR, "state_cases.csv"), index=False)
states_df.drop(columns=["climate"]).to_csv(os.path.join(DATA_DIR, "states.csv"), index=False)


# ---------------------------------------------------------------------------
# 4) Training table for the risk classifier  ->  data/risk_training.csv
#    For every region + disease + week we compute:
#       cases_4w      = total cases in the last 4 weeks
#       growth_rate   = change of the last 2 weeks vs the 2 weeks before
#       population
#       cases_per_100k = cases_4w per 100,000 people
#    and a risk label (Low / Medium / High) using a simple, explainable rule.
#    NOTE: With real data, replace this rule with labels from health
#    authorities (for example alert levels). The rule below is for SAMPLE use.
# ---------------------------------------------------------------------------
def risk_label(per100k, growth):
    """Simple explainable rule used to create SAMPLE labels."""
    if per100k >= 40 or (per100k >= 25 and growth >= 0.30):
        return "High"
    if per100k >= 12 or (per100k >= 6 and growth >= 0.25):
        return "Medium"
    return "Low"


def build_training(cases_df, region_col, pop_lookup):
    out = []
    for (region, disease), g in cases_df.groupby([region_col, "disease"]):
        g = g.sort_values("date").reset_index(drop=True)
        c = g["cases"].to_numpy()
        pop = pop_lookup[region]
        # start at index 4 so we have 4 weeks of history
        for i in range(4, len(g)):
            last2 = c[i - 1:i + 1].sum()
            prev2 = c[i - 3:i - 1].sum()
            growth = (last2 - prev2) / max(prev2, 1)
            cases_4w = c[i - 3:i + 1].sum()
            per100k = cases_4w / pop * 100000
            out.append((
                region, disease, g.loc[i, "date"], int(cases_4w),
                round(float(growth), 4), int(pop), round(float(per100k), 3),
                risk_label(per100k, growth),
            ))
    return pd.DataFrame(out, columns=[
        "region", "disease", "date", "cases_4w", "growth_rate",
        "population", "cases_per_100k", "risk_level",
    ])


country_pop = dict(zip(countries_df["country"], countries_df["population"]))
state_pop = dict(zip(states_df["state"], states_df["population"]))

train_c = build_training(country_cases, "country", country_pop)
train_c.insert(1, "level", "country")
train_s = build_training(state_cases, "state", state_pop)
train_s.insert(1, "level", "state")

risk_training = pd.concat([train_c, train_s], ignore_index=True)
risk_training.to_csv(os.path.join(DATA_DIR, "risk_training.csv"), index=False)

# ---------------------------------------------------------------------------
# 5) Travel advisory notes  ->  data/advisories.csv
#    Short, general awareness text only. Based on the general public-health
#    advice published by WHO and CDC. Not medical advice.
# ---------------------------------------------------------------------------
ADVISORIES = [
    ("Dengue", "Low",
     "Dengue activity looks low. Still, avoid mosquito bites during the day: use repellent, wear long sleeves and stay in screened or air-conditioned rooms."),
    ("Dengue", "Medium",
     "Dengue activity is moderate. Use insect repellent, wear long sleeves and trousers, use bed nets or screens, and remove standing water around where you stay. See a doctor if you get fever after travel."),
    ("Dengue", "High",
     "Dengue activity is high. Protect yourself from mosquito bites all day (repellent, long clothing, screens or nets) and avoid places with standing water. If you develop fever, joint pain or rash, see a doctor and watch for warning signs."),
    ("Influenza", "Low",
     "Flu activity looks low. Wash hands often and consider a seasonal flu vaccine, especially if you are in a higher-risk group."),
    ("Influenza", "Medium",
     "Flu activity is moderate. Get vaccinated if you can, wash hands often, and wear a mask in crowded indoor places. Stay home if you feel sick."),
    ("Influenza", "High",
     "Flu activity is high. Vaccination is recommended, wash hands often, wear a mask in crowded places, avoid close contact with sick people and stay home when ill. Seek care early if you are at higher risk."),
    ("COVID-19", "Low",
     "COVID-19 activity looks low. Keep vaccinations up to date and stay home and test if you have symptoms."),
    ("COVID-19", "Medium",
     "COVID-19 activity is moderate. Stay up to date with vaccination, wear a mask in crowded or poorly ventilated places, wash hands, and test if you have symptoms."),
    ("COVID-19", "High",
     "COVID-19 activity is high. Stay up to date with vaccination, wear a mask in crowded or poorly ventilated places, improve ventilation, test if you have symptoms and isolate while sick. People at higher risk should talk to a doctor early."),
]
pd.DataFrame(ADVISORIES, columns=["disease", "risk_level", "advisory"]).to_csv(
    os.path.join(DATA_DIR, "advisories.csv"), index=False
)

print("Sample data created in:", DATA_DIR)
for f in sorted(os.listdir(DATA_DIR)):
    if f.endswith(".csv"):
        print(f"  {f}: {len(pd.read_csv(os.path.join(DATA_DIR, f)))} rows")
