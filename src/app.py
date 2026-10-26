"""APP: public Streamlit dashboard of (synthetic) Swiss-style electricity consumption."""
import sys
from pathlib import Path
import os

def list_files_walk(start_path='.'):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            print(os.path.join(root, file))

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import fit_and_forecast, load

st.set_page_config(page_title="Energy consumption monitor", layout="wide")
st.title("Energy consumption monitor")
st.caption("Synthetic sample data, not real measurements")

try:
    df = load()
except:
    directory_path = '../../'
    list_files_walk(directory_path)


start, end = st.slider(
    "Period", min_value=df.date.min().date(), max_value=df.date.max().date(),
    value=(df.date.max().date().replace(month=1, day=1), df.date.max().date()),
)
view = df[(df.date.dt.date >= start) & (df.date.dt.date <= end)].set_index("date")

c1, c2, c3 = st.columns(3)
c1.metric("Average per day", f"{view.consumption_gwh.mean():.1f} GWh")
c2.metric("Peak day", f"{view.consumption_gwh.max():.1f} GWh", str(view.consumption_gwh.idxmax().date()))
c3.metric("Mean temperature", f"{view.temperature_c.mean():.1f} °C")

st.subheader("Daily consumption and 7-day average")
st.line_chart(view.assign(rolling_7d=view.consumption_gwh.rolling(7).mean())[["consumption_gwh", "rolling_7d"]])

st.subheader("Forecast check")
horizon = st.select_slider("Hold out the last N days", options=[7, 14, 28, 56], value=14)
forecast, mae = fit_and_forecast(df, horizon)
st.line_chart(forecast.set_index("date"))
st.write(f"Mean absolute error: **{mae:.2f} GWh/day** (the job `train.py` computes the same thing in the background)")
