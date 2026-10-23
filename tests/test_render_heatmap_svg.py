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
    "monthly": [{"month": "2025-10", "total": 50}, {"month": "2026-10", "total": 300}],
    "days": [
        {"date": f"2026-01-{i:02d}", "count": i % 5, "level": i % 5} for i in range(1, 29)
    ]
}

def test_render_heatmap_svg_creates_valid_svg(tmp_path):
    from scripts.render_heatmap_svg import render_heatmap

    out_file = tmp_path / "test_heatmap.svg"
    svg_path = render_heatmap(MOCK_DATA, str(out_file), user="chogerlate")

    assert os.path.exists(svg_path)
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<svg" in content
    assert 'width="860"' in content
    assert "chogerlate@github: ~/contributions --graph" in content
    assert "Less" in content
    assert "More" in content
    assert "1,630" in content
    assert "current streak" in content
    assert "longest" in content
    assert "</svg>" in content
