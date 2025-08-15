
import pandas as pd
import numpy as np
import argparse
import os
from datetime import date
from dateutil.relativedelta import relativedelta

def build_message_types():
    # Only one message type for this run
    return ["MT103"]

def generate(rows_replication:int, days:int=92, seed:int=42):
    rng = np.random.default_rng(seed)
    end = pd.to_datetime(date.today())
    start = end - relativedelta(days=days-1)
    dates = pd.date_range(start, end, freq="D")
    directions = ["inbound","outbound"]
    message_types = build_message_types()
    rows = []
    for d in dates:
        dow = d.weekday()
        dow_factor = 1.2 if dow in (1,2,3) else (0.9 if dow in (5,6) else 1.0)
        month_factor = 1.0 + 0.05 * (d.month % 2)
        iso_date = d.strftime('%Y-%m-%d')
        for mt in message_types:
            if mt.startswith("MT1") or "pacs.00" in mt or "pain.001" in mt:
                base = 120
            elif mt.startswith("MT2") or "pacs.009" in mt:
                base = 80
            elif mt.startswith("MT5"):
                base = 60
            elif mt.startswith("MT7"):
                base = 40
            elif mt.startswith("MT9") or "camt." in mt:
                base = 70
            elif mt.startswith("MT3") or mt.startswith("MT6"):
                base = 30
            else:
                base = 25
            mean = base * dow_factor * month_factor
            for direction in directions:
                lam = max(5, mean * (1.1 if direction == "inbound" else 0.95))
                for _ in range(rows_replication):
                    count = int(max(1, rng.poisson(lam)))
                    rows.append((iso_date, mt, direction, count))
    df = pd.DataFrame(rows, columns=["date","message_type","direction","count"])
    # Sort by date ascending
    df = df.sort_values("date").reset_index(drop=True)
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replications", type=int, default=2, help="Rows per type/day/direction. Increase to grow file size.")
    ap.add_argument("--days", type=int, default=100, help="Number of days (last 100 days)")
    ap.add_argument("--out", type=str, default="swift_transactions_last_3_months.csv", help="Output CSV path")
    ap.add_argument("--target_mb", type=float, default=2.0, help="Optional: adjust replications until file is close to this size (MB)")
    ap.add_argument("--tolerance_mb", type=float, default=0.25, help="Size tolerance (MB) when targeting")
    args = ap.parse_args()

    # First pass
    df = generate(args.replications, days=args.days)
    df.to_csv(args.out, index=False)
    size_mb = os.path.getsize(args.out)/(1024*1024)

    # If target_mb provided, adjust by scaling replications up/down heuristically
    if args.target_mb > 0:
        # crude proportional adjustment loop (max 6 tries)
        tries = 0
        reps = args.replications
        while abs(size_mb - args.target_mb) > args.tolerance_mb and tries < 6 and size_mb > 0:
            factor = args.target_mb / size_mb
            reps = max(1, int(round(reps * factor)))
            df = generate(reps, days=args.days, seed=42+tries)
            df.to_csv(args.out, index=False)
            size_mb = os.path.getsize(args.out)/(1024*1024)
            tries += 1

    print(f"Saved to {args.out} ({size_mb:.2f} MB). Columns: date,message_type,direction,count")

if __name__ == "__main__":
    main()
