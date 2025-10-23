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
