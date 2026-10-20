"""Generate the synthetic daily electricity-consumption sample.

The numbers are SYNTHETIC (realistic seasonality, invented values) so the repo can be
public and has no licensing or data-protection questions. Swap in real open data
(e.g. from opendata.swiss) by producing a CSV with the same columns.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")
doy = dates.dayofyear.to_numpy()
dow = dates.dayofweek.to_numpy()

temperature = 10 - 9 * np.cos(2 * np.pi * (doy - 15) / 365.25) + rng.normal(0, 2.5, len(dates))
annual = 25 * np.cos(2 * np.pi * (doy - 15) / 365.25)          # winter peak
weekly = np.where(dow >= 5, -22, 0) + np.where(dow == 5, 6, 0)  # weekends lower
trend = np.linspace(0, -6, len(dates))                           # efficiency gains
heating = np.clip(12 - temperature, 0, None) * 0.9
consumption = 160 + annual + weekly + trend + heating + rng.normal(0, 3, len(dates))

pd.DataFrame(
    {"date": dates.date, "consumption_gwh": consumption.round(2), "temperature_c": temperature.round(1)}
).to_csv("data/consumption.csv", index=False)
print(f"wrote data/consumption.csv ({len(dates)} rows)")
