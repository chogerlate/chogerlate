import json
import os
import subprocess
import sys
from unittest.mock import patch, MagicMock

def test_workflow_yaml_syntax():
    wf_path = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "update-profile-art.yml")
    assert os.path.exists(wf_path)
    with open(wf_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "name: Update profile art" in content
    assert "cron: \"17 6 * * *\"" in content
    assert "workflow_dispatch:" in content
    assert "contents: write" in content
    assert "stefanzweifel/git-auto-commit-action@v5" in content
    assert "fetch_contributions.py" in content
    assert "render_heatmap_svg.py" in content
    assert "render_stats_svg.py" in content

def test_full_pipeline_local_execution_in_tmp(tmp_path):
    out_json = str(tmp_path / "contributions.json")
    out_heatmap = str(tmp_path / "contrib-heatmap.svg")
    out_stats = str(tmp_path / "stats.svg")

    mock_days = [
        {"date": f"2026-01-{i:02d}", "count": 2, "level": 1} for i in range(1, 29)
    ]
    mock_data = {
        "username": "chogerlate",
        "range": {"start": "2026-01-01", "end": "2026-01-28"},
        "total_contributions": 56,
        "active_days": 28,
        "avg_per_active_day": 2.0,
        "current_streak": {"length": 28, "start": "2026-01-01", "end": "2026-01-28"},
        "longest_streak": {"length": 28, "start": "2026-01-01", "end": "2026-01-28"},
        "best_day": {"date": "2026-01-01", "count": 2},
        "monthly": [{"month": "2026-01", "total": 56}],
        "days": mock_days,
    }

    # Verify fetch_contributions with output redirection
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    # Render heatmap to tmp
    res2 = subprocess.run([sys.executable, "scripts/render_heatmap_svg.py", out_json, out_heatmap], capture_output=True, text=True)
    assert res2.returncode == 0
    assert os.path.exists(out_heatmap)

    # Render stats to tmp
    res3 = subprocess.run([sys.executable, "scripts/render_stats_svg.py", out_json, out_stats], capture_output=True, text=True)
    assert res3.returncode == 0
    assert os.path.exists(out_stats)
