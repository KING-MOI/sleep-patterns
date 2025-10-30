import pandas as pd

from sleep_patterns.synthetic import generate


def test_same_seed_same_data():
    a, _ = generate(days=60, seed=3)
    b, _ = generate(days=60, seed=3)
    pd.testing.assert_frame_equal(a, b)


def test_planted_effects_show_up():
    sleep, caffeine = generate()
    hours = (sleep["end"] - sleep["start"]).dt.total_seconds() / 3600
    real = sleep[hours.between(2, 14)]
    real_hours = hours[hours.between(2, 14)]
    night = (real["start"] - pd.Timedelta(hours=12)).dt.day_name()
    assert real_hours.groupby(night).mean().idxmin() == "Sunday"
    assert caffeine["caffeine_mg"].gt(0).all()
