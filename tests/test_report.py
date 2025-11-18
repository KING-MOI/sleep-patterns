from sleep_patterns.report import build


def test_build_writes_every_chart(tmp_path):
    paths = build(tmp_path)
    assert len(paths) == 6
    for p in paths:
        assert p.stat().st_size > 10_000
