"""Tiny forecasting model shared by the job (train.py) and the app (src/app.py)."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

DATA = Path(__file__).resolve().parent.parent.parent / "energy-input-data" / "consumption.csv"


def load(path=DATA):
    df = pd.read_csv(path, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


def features(dates, temperature):
    doy = dates.dt.dayofyear.to_numpy()
    dow = dates.dt.dayofweek.to_numpy()
    X = np.column_stack(
        [np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25),
         np.clip(12 - temperature, 0, None)]
        + [(dow == d).astype(float) for d in range(6)]
    )
    return X


def fit_and_forecast(df, horizon, alpha=1.0):
    """Hold out the last `horizon` days, fit on the rest, return (forecast_df, mae)."""
    train, test = df.iloc[:-horizon], df.iloc[-horizon:]
    model = Ridge(alpha=alpha).fit(features(train.date, train.temperature_c), train.consumption_gwh)
    pred = model.predict(features(test.date, test.temperature_c))
    out = test[["date", "consumption_gwh"]].assign(forecast_gwh=pred.round(2))
    mae = float(np.mean(np.abs(out.forecast_gwh - out.consumption_gwh)))
    return out, mae
