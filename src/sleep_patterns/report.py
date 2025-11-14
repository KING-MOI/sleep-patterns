"""Rebuild every chart in assets/ from the CSVs in data/.

python -m sleep_patterns.report
"""

from pathlib import Path

from . import plots
from .caffeine import by_last_drink, with_caffeine
from .clean import nightly
from .io import load_caffeine, load_sleep
from .metrics import sleep_debt, weekday_summary

ASSETS = Path(__file__).resolve().parents[2] / "assets"


def build(out=ASSETS):
    out.mkdir(parents=True, exist_ok=True)
    nights = nightly(load_sleep())
    merged = with_caffeine(nights, load_caffeine())

    return [
        plots.save(plots.weekday_bars(weekday_summary(nights)), out / "weekday.png"),
        plots.save(plots.debt_line(sleep_debt(nights)), out / "sleep_debt.png"),
        plots.save(plots.caffeine_scatter(merged), out / "caffeine.png"),
        plots.save(plots.calendar_heatmap(nights), out / "calendar.png"),
        plots.save(plots.cutoff_bars(by_last_drink(merged)), out / "caffeine_cutoff.png"),
    ]


if __name__ == "__main__":
    for path in build():
        print(path)
