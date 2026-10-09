# HealthRadar

## Deploy on Render

The Flask application lives in `healthradar/`. Connect this repository to Render as a **Blueprint** and deploy using the root [`render.yaml`](./render.yaml). Render runs from the repository root and installs dependencies using [`requirements.txt`](./requirements.txt), which includes the app's canonical [`healthradar/requirements.txt`](./healthradar/requirements.txt). Gunicorn serves the app on Render's assigned `$PORT`.

Before deploying, make sure the CSV files in `healthradar/data/` are committed; the app needs them at startup. The `healthradar/models/` artifacts are included in this repository, and scikit-learn is pinned to the model's saved version.

If creating a Web Service manually, use:

- **Root Directory:** repository root (leave blank)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --chdir healthradar app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
- **Health Check Path:** `/`
- **Environment Variable:** `PYTHON_VERSION=3.12.4`
