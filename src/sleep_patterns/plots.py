"""Matplotlib charts for the README and notebooks."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.size": 10,
        "lines.linewidth": 2,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    }
)


def save(fig, path):
    fig.savefig(path)
    plt.close(fig)
    return path


def weekday_bars(summary, ax=None):
    """Mean hours per weekday, worst night called out."""
    ax = ax or plt.subplots(figsize=(8, 4))[1]
    worst = summary["mean_hours"].idxmin()
    colors = [ORANGE if day == worst else BLUE for day in summary.index]
    bars = ax.bar(
        [d[:3] for d in summary.index], summary["mean_hours"], color=colors, width=0.6
    )
    for bar, day in zip(bars, summary.index):
        if day == worst:
            ax.annotate(
                f"{bar.get_height():.2f} h",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                color=INK,
            )
    ax.set_ylim(0, summary["mean_hours"].max() + 1)
    ax.set_ylabel("mean hours asleep")
    ax.set_title(f"{worst} night is the shortest")
    ax.grid(axis="x", visible=False)
    return ax.figure


def debt_line(debt, window=14, title="Rolling sleep debt", ax=None):
    """Rolling sleep debt across the year."""
    ax = ax or plt.subplots(figsize=(10, 4))[1]
    ax.plot(debt.index, debt["debt"], color=BLUE)
    ax.axhline(0, color=BASELINE, linewidth=1)
    peak = debt["debt"].idxmax()
    ax.annotate(
        f"peak {debt['debt'].max():.1f} h ({peak:%d %b})",
        (peak, debt["debt"].max()),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
        color=INK,
    )
    ax.plot(peak, debt["debt"].max(), "o", color=BLUE, markersize=7, markeredgecolor=SURFACE)
    ax.set_ylim(top=debt["debt"].max() * 1.15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_ylabel(f"hours owed, last {window} nights")
    ax.set_title(title)
    ax.margins(x=0.01)
    return ax.figure


def caffeine_scatter(merged, x="late_mg", ax=None):
    """Afternoon caffeine against that night's sleep, with a least-squares line."""
    import numpy as np

    ax = ax or plt.subplots(figsize=(7, 5))[1]
    ax.scatter(
        merged[x], merged["hours"], s=28, color=BLUE, alpha=0.55, edgecolors=SURFACE, linewidths=0.8
    )
    slope, intercept = np.polyfit(merged[x], merged["hours"], 1)
    xs = np.array([0, merged[x].max()])
    ax.plot(xs, intercept + slope * xs, color=ORANGE)
    r = merged[[x, "hours"]].corr().iloc[0, 1]
    ax.text(
        0.97,
        0.95,
        f"r = {r:.2f}\n{slope * 100:+.2f} h per 100 mg",
        transform=ax.transAxes,
        ha="right",
        va="top",
        color=INK,
    )
    ax.set_xlabel("caffeine after 2pm (mg)")
    ax.set_ylabel("hours asleep that night")
    ax.set_title("Afternoon caffeine costs sleep")
    return ax.figure
