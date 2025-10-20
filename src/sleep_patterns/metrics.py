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
