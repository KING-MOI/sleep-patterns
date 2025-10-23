"""Line the caffeine log up against the night that followed it."""

import pandas as pd


def daily_caffeine(caffeine, late_hour=14):
    df = caffeine.assign(
        day=caffeine["timestamp"].dt.normalize(),
        hour=caffeine["timestamp"].dt.hour + caffeine["timestamp"].dt.minute / 60,
    )
    df["late_mg"] = df["caffeine_mg"].where(df["hour"] >= late_hour, 0)
    return df.groupby("day").agg(
        total_mg=("caffeine_mg", "sum"),
        late_mg=("late_mg", "sum"),
        drinks=("caffeine_mg", "size"),
        last_drink=("hour", "max"),
    )


def with_caffeine(nights, caffeine, late_hour=14):
    """Attach each day's caffeine to that evening's night. No log = 0 mg."""
    daily = daily_caffeine(caffeine, late_hour)
    out = nights.merge(daily, left_on="night", right_index=True, how="left")
    out[["total_mg", "late_mg", "drinks"]] = out[["total_mg", "late_mg", "drinks"]].fillna(0)
    return out


def caffeine_correlations(merged, cols=("total_mg", "late_mg", "drinks")):
    targets = ["hours", "efficiency", "awakenings"]
    rows = {
        method: merged[list(cols) + targets].corr(method=method).loc[list(cols), targets]
        for method in ("pearson", "spearman")
    }
    return pd.concat(rows, names=["method", "caffeine"])
