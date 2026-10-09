"""
forecast.py
-----------
Predicts weekly cases for the next 2-4 weeks.

Two methods (the app picks automatically):
1. ARIMA from statsmodels - used if statsmodels is installed.
2. Simple "lag model" (Ridge regression on the last 8 weeks) - uses only
   scikit-learn, so it always works. Easy to explain: "next week looks like
   a weighted mix of the previous 8 weeks".

Both return the same structure, so the rest of the app does not care which
one was used.
"""

import numpy as np
from sklearn.linear_model import Ridge

try:
    from statsmodels.tsa.arima.model import ARIMA  # optional
    HAVE_STATSMODELS = True
except Exception:  # statsmodels not installed
    HAVE_STATSMODELS = False

N_LAGS = 8  # how many past weeks the lag model looks at


def _lag_forecast(values, steps):
    """Forecast with a Ridge regression on the previous N_LAGS weeks."""
    y = np.log1p(np.asarray(values, dtype=float))  # log keeps numbers stable
    # Build training rows: [y(t-8) ... y(t-1)] -> y(t)
    X, target = [], []
    for i in range(N_LAGS, len(y)):
        X.append(y[i - N_LAGS:i])
        target.append(y[i])
    X, target = np.array(X), np.array(target)
    model = Ridge(alpha=1.0).fit(X, target)
    # Typical error on training data, used for the "uncertainty band"
    resid_std = float(np.std(target - model.predict(X)))

    history = list(y)
    preds = []
    for _ in range(steps):
        nxt = float(model.predict(np.array(history[-N_LAGS:]).reshape(1, -1))[0])
        preds.append(nxt)
        history.append(nxt)  # feed prediction back in for the next step
    preds = np.array(preds)
    # Band grows a little with distance into the future
    widen = resid_std * np.sqrt(np.arange(1, steps + 1))
    return preds, preds - 1.64 * widen, preds + 1.64 * widen


def _arima_forecast(values, steps):
    """Forecast with ARIMA(2,1,1) on log-cases (needs statsmodels)."""
    y = np.log1p(np.asarray(values, dtype=float))
    fit = ARIMA(y, order=(2, 1, 1)).fit()
    res = fit.get_forecast(steps=steps)
    mean = np.asarray(res.predicted_mean)
    ci = np.asarray(res.conf_int(alpha=0.1))
    return mean, ci[:, 0], ci[:, 1]


def forecast_series(values, steps=4):
    """
    values: list of weekly case counts (oldest first).
    Returns dict with 'method', 'predicted', 'lower', 'upper' (lists of ints).
    """
    values = [float(v) for v in values]
    if len(values) < N_LAGS + 8:
        raise ValueError("Not enough data points to forecast")

    method = "lag-regression"
    try:
        if HAVE_STATSMODELS:
            mean, low, high = _arima_forecast(values, steps)
            method = "ARIMA(2,1,1)"
        else:
            mean, low, high = _lag_forecast(values, steps)
    except Exception:
        # If ARIMA fails for any reason, use the simple model
        mean, low, high = _lag_forecast(values, steps)
        method = "lag-regression"

    def back(a):  # undo the log transform, no negative cases
        return [int(max(0, round(float(v)))) for v in np.expm1(a)]

    return {"method": method, "predicted": back(mean),
            "lower": back(low), "upper": back(high)}
