"""Summary numbers over the nightly table."""

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def weekday_summary(nights):
    return (
        nights.groupby("weekday")
        .agg(
            nights=("hours", "size"),
            mean_hours=("hours", "mean"),
            median_hours=("hours", "median"),
            efficiency=("efficiency", "mean"),
            awakenings=("awakenings", "mean"),
        )
        .reindex(WEEKDAYS)
    )


def worst_weekday(nights):
    return weekday_summary(nights)["mean_hours"].idxmin()


def sleep_debt(nights, target=7.5, window=14):
    """Per-night deficit against a target, plus rolling and cumulative debt.

    Missing nights stay NaN; the rolling debt is the mean deficit of the
    nights we do have, scaled up to the window, so gaps don't look like rest.
    """
    s = nights.set_index("night")["hours"].asfreq("D")
    deficit = target - s
    out = deficit.to_frame("deficit")
    out["debt"] = deficit.rolling(window, min_periods=window // 2).mean() * window
    out["cumulative"] = deficit.fillna(0).cumsum()
    return out
