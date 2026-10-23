import os
import pytest

MOCK_DATA = {
    "username": "chogerlate",
    "range": {"start": "2025-10-19", "end": "2026-10-23"},
    "total_contributions": 1630,
    "active_days": 141,
    "avg_per_active_day": 11.6,
    "current_streak": {"length": 7, "start": "2026-10-17", "end": "2026-10-23"},
    "longest_streak": {"length": 11, "start": "2026-05-27", "end": "2026-06-06"},
    "best_day": {"date": "2026-10-18", "count": 226},
    "monthly": [
        {"month": f"2026-{i:02d}", "total": 100 + i * 10} for i in range(1, 13)
    ],
    "days": [
        {"date": f"2026-01-{i:02d}", "count": 5, "level": 1} for i in range(1, 30)
    ]
}

def test_render_stats_svg(tmp_path):
    from scripts.render_stats_svg import render_stats

    out_file = tmp_path / "test_stats.svg"
    svg_path = render_stats(MOCK_DATA, str(out_file), user="chogerlate")

    assert os.path.exists(svg_path)
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<svg" in content
    assert 'viewBox="0 0 840 880"' in content
    assert "chogerlate@github: ~$ ./stats.sh" in content
    assert "current streak" in content
    assert "longest streak" in content
    assert "contributions / month" in content
    assert "</svg>" in content

def test_make_info_card(tmp_path):
    from scripts.make_info_card import generate_info_card

    out_file = tmp_path / "test_info.svg"
    svg_path = generate_info_card(str(out_file), user="chogerlate")

    assert os.path.exists(svg_path)
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<svg" in content
    assert "chogerlate@" in content
    assert "Machine Learning" in content or "Role" in content
    assert "</svg>" in content
