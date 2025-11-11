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


def by_last_drink(merged, edges=(0, 12, 14, 16, 24)):
    """Mean sleep grouped by when the last caffeinated drink of the day was."""
    labels = [f"{lo:02d}-{hi:02d}h" for lo, hi in zip(edges, edges[1:])]
    bucket = pd.cut(merged["last_drink"], edges, labels=labels, right=False)
    bucket = bucket.cat.add_categories("none").fillna("none")
    return (
        merged.groupby(bucket, observed=False)["hours"]
        .agg(["size", "mean"])
        .rename(columns={"size": "nights", "mean": "mean_hours"})
        .reindex(["none", *labels])
    )


def late_caffeine_effect(merged, x="late_mg"):
    """Hours of sleep per mg of late caffeine, holding month and weekday fixed.

    Busy months bring both more coffee and less sleep, so the raw slope
    overstates the effect. Month and weekday dummies soak that up.
    """
    import numpy as np

    night = merged["night"]
    dummies = pd.get_dummies(
        pd.DataFrame({"month": night.dt.month, "weekday": night.dt.day_of_week}).astype(str),
        drop_first=True,
        dtype=float,
    )
    X = np.column_stack([np.ones(len(merged)), merged[x].to_numpy(float), dummies.to_numpy()])
    coef, *_ = np.linalg.lstsq(X, merged["hours"].to_numpy(float), rcond=None)
    return coef[1]
