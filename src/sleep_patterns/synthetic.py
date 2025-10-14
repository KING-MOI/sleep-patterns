"""Generate a synthetic year of sleep-tracker data.

The real export is private, so this produces a stand-in with the same
columns and roughly the same quirks.
"""

import numpy as np
import pandas as pd

# hours added to bedtime / duration, indexed by weekday of the night (Mon=0)
BEDTIME_SHIFT = np.array([0.0, 0.0, 0.1, 0.3, 1.1, 1.3, 0.6])
DURATION_SHIFT = np.array([0.0, 0.1, -0.1, -0.3, 0.5, 0.9, -0.8])

# (first day, last day, hours lost per night) - exam season and end-of-year deadlines
CRUNCH_PERIODS = [
    ("03-10", "04-25", 0.7),
    ("11-03", "12-12", 0.5),
]
SUMMER = ("07-01", "08-20", -0.3)


def _seasonal_loss(nights):
    loss = np.zeros(len(nights))
    md = nights.strftime("%m-%d")
    for lo, hi, hours in CRUNCH_PERIODS + [SUMMER]:
        loss[(md >= lo) & (md <= hi)] += hours
    return loss


DRINKS = {
    "coffee": 95,
    "espresso": 63,
    "black tea": 47,
    "cola": 34,
    "energy drink": 160,
}
DRINK_WEIGHTS = [0.45, 0.2, 0.2, 0.08, 0.07]


def generate_caffeine(start="2025-01-01", days=365, seed=7):
    rng = np.random.default_rng(seed + 1)
    days_idx = pd.date_range(start, periods=days, freq="D")
    crunch = _seasonal_loss(days_idx) > 0

    rows = []
    for day, in_crunch in zip(days_idx, crunch):
        n = rng.poisson(2.6 if in_crunch else 1.8)
        # first drink in the morning, the rest spread over the day
        hours = np.sort(np.concatenate([
            rng.normal(8.0, 0.6, min(n, 1)),
            rng.uniform(10, 19.5 if in_crunch else 17.5, max(n - 1, 0)),
        ]))
        for h in hours:
            drink = rng.choice(list(DRINKS), p=DRINK_WEIGHTS)
            rows.append((day + pd.Timedelta(hours=float(h)), drink, DRINKS[drink]))

    out = pd.DataFrame(rows, columns=["timestamp", "drink", "caffeine_mg"])
    out["timestamp"] = out["timestamp"].dt.round("min")
    return out


def _late_caffeine(caffeine, nights, after_hour=14):
    late = caffeine[caffeine["timestamp"].dt.hour >= after_hour]
    per_day = late.groupby(late["timestamp"].dt.normalize())["caffeine_mg"].sum()
    return per_day.reindex(nights, fill_value=0).to_numpy()


def generate_sleep(start="2025-01-01", days=365, seed=7, caffeine=None):
    rng = np.random.default_rng(seed)
    nights = pd.date_range(start, periods=days, freq="D")
    weekday = nights.weekday.to_numpy()

    late_mg = np.zeros(days) if caffeine is None else _late_caffeine(caffeine, nights)

    bed_hour = rng.normal(23.1, 0.5, days) + BEDTIME_SHIFT[weekday] + late_mg * 0.002
    duration = (
        rng.normal(7.2, 0.6, days)
        + DURATION_SHIFT[weekday]
        - _seasonal_loss(nights)
        - late_mg * 0.004
    )

    awakenings = rng.poisson(1.2 + late_mg * 0.006)
    efficiency = np.clip(rng.normal(91, 3, days) - awakenings * 1.2, 70, 99)

    start_ts = nights + pd.to_timedelta(bed_hour, unit="h")
    end_ts = start_ts + pd.to_timedelta(duration, unit="h")

    out = pd.DataFrame(
        {
            "start": start_ts.round("min"),
            "end": end_ts.round("min"),
            "awakenings": awakenings,
            "efficiency": efficiency.round(1),
        }
    )
    # the watch was on the charger some nights
    worn = rng.random(days) > 0.03
    out = out[worn]

    # and a handful of junk sessions: afternoon naps and a day it never came off
    junk_days = rng.choice(nights, size=6, replace=False)
    junk_start = junk_days + pd.to_timedelta(rng.uniform(13, 16, 6), unit="h")
    junk_len = np.array([0.4, 0.6, 0.3, 0.5, 15.5, 0.7])
    junk = pd.DataFrame(
        {
            "start": junk_start.round("min"),
            "end": (junk_start + pd.to_timedelta(junk_len, unit="h")).round("min"),
            "awakenings": 0,
            "efficiency": 95.0,
        }
    )
    return pd.concat([out, junk]).sort_values("start").reset_index(drop=True)


def generate(start="2025-01-01", days=365, seed=7):
    caffeine = generate_caffeine(start, days, seed)
    sleep = generate_sleep(start, days, seed, caffeine=caffeine)
    return sleep, caffeine


def main(argv=None):
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)

    sleep, caffeine = generate(args.start, args.days, args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    sleep.to_csv(args.out / "sleep_log.csv", index=False)
    caffeine.to_csv(args.out / "caffeine_log.csv", index=False)
    print(f"wrote {len(sleep)} sessions and {len(caffeine)} drinks to {args.out}/")


if __name__ == "__main__":
    main()
