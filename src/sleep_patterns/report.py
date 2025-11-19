"""Rebuild every chart in assets/ from the CSVs in data/ and print the headline numbers.

python -m sleep_patterns.report
"""

from pathlib import Path

from . import plots
from .caffeine import by_last_drink, late_caffeine_effect, with_caffeine
from .clean import nightly
from .io import load_caffeine, load_sleep
from .metrics import sleep_debt, social_jetlag, weekday_summary, worst_weekday

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
        plots.save(plots.sleep_window(nights), out / "sleep_window.png"),
    ]


def headline(target=7.5):
    nights = nightly(load_sleep())
    merged = with_caffeine(nights, load_caffeine())
    summary = weekday_summary(nights)
    worst = worst_weekday(nights)
    debt = sleep_debt(nights, target=target)
    return {
        "nights logged": len(nights),
        "median night (h)": round(nights["hours"].median(), 2),
        "worst night": worst,
        "worst night mean (h)": round(summary.loc[worst, "mean_hours"], 2),
        f"peak 14-night debt vs {target} h": round(debt["debt"].max(), 1),
        "peak debt date": f"{debt['debt'].idxmax():%Y-%m-%d}",
        "social jetlag (min)": round(social_jetlag(nights) * 60),
        "late caffeine (min per 100 mg)": round(late_caffeine_effect(merged) * 100 * 60),
    }


if __name__ == "__main__":
    for path in build():
        print(path)
    print()
    print("| metric | value |\n|---|---|")
    for key, value in headline().items():
        print(f"| {key} | {value} |")
