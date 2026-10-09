# HealthRadar data files

**All files here are SAMPLE data (made up, for testing only).** The app must label
them as sample data in the UI. To use real data, replace a CSV with one that has
the same column names. Real sources: WHO (data.who.int), CDC (data.cdc.gov), disease.sh.

| File | Columns | Used for |
|------|---------|----------|
| countries.csv | country, iso3, continent, population, lat, lon | Country list, travel check |
| country_cases.csv | date, country, iso3, disease, cases | Weekly cases per country, forecast, trend chart |
| states.csv | state, country, population, lat, lon | Local mode (nearest state from location, dropdown fallback) |
| state_cases.csv | date, state, country, disease, cases | Weekly cases per state, recent records |
| risk_training.csv | region, level, disease, date, cases_4w, growth_rate, population, cases_per_100k, risk_level | Training the Low/Medium/High classifier |
| advisories.csv | disease, risk_level, advisory | Travel advisory text |

Notes
- `date` is the week-ending date, format YYYY-MM-DD. Latest sample week: 2026-10-04.
- `disease` is one of: Dengue, Influenza, COVID-19.
- `risk_level` is one of: Low, Medium, High.
- `growth_rate` = (cases in last 2 weeks - cases in the 2 weeks before) / cases in the 2 weeks before.
- Sample risk labels come from a simple rule in `generate_sample_data.py`. With real data, use labels from health authorities.
- Re-create the sample files any time with: `python generate_sample_data.py`
