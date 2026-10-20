"""JOB: fit a forecast and report its error. Runs in < 1 minute, no browser needed.

    python train.py --horizon 7
    python train.py --horizon 14 --alpha 10 --out /path/to/data-connector
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from model import fit_and_forecast, load 


def writable_dir(preferred):
    for d in (Path(preferred), Path("/tmp/outputs")):
        try:
            d.mkdir(parents=True, exist_ok=True)
            (d / ".write_test").touch()
            (d / ".write_test").unlink()
            return d
        except OSError:
            continue
    raise SystemExit("No writable output directory found")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--horizon", type=int, default=7, help="days to hold out and forecast")
    p.add_argument("--alpha", type=float, default=1.0, help="Ridge regularisation strength")
    p.add_argument("--out", default=os.environ.get("OUTPUT_DIR", "outputs"), help="where to write results")
    args = p.parse_args()

    print(f"[1/4] Loading data ...", flush=True)
    df = load()
    print(f"      {len(df)} days, {df.date.min().date()} to {df.date.max().date()}", flush=True)
    time.sleep(2) 

    print(f"[2/4] Fitting Ridge(alpha={args.alpha}) and forecasting the last {args.horizon} days ...", flush=True)
    forecast, mae = fit_and_forecast(df, args.horizon, args.alpha)
    time.sleep(2)

    print("[3/4] Results", flush=True)
    print(forecast.to_string(index=False), flush=True)
    print(f"      MAE = {mae:.2f} GWh/day", flush=True)

    out = writable_dir(args.out)
    path = out / f"forecast_h{args.horizon}_a{args.alpha:g}.csv"
    forecast.to_csv(path, index=False)
    print(f"[4/4] Wrote {path}", flush=True)
    print("      Note: Ensure to point --out at a data connector to keep results persistent.", flush=True)


if __name__ == "__main__":
    main()
