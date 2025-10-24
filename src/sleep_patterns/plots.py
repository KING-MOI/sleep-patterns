"""Matplotlib charts for the README and notebooks."""

import matplotlib

matplotlib.use("Agg")

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
