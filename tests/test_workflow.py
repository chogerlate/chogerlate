import os
import subprocess

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

def test_full_pipeline_local_execution():
    res1 = subprocess.run([".venv/bin/python", "scripts/fetch_contributions.py"], capture_output=True, text=True)
    assert res1.returncode == 0
    assert os.path.exists("data/contributions.json")

    res2 = subprocess.run([".venv/bin/python", "scripts/render_heatmap_svg.py"], capture_output=True, text=True)
    assert res2.returncode == 0
    assert os.path.exists("contrib-heatmap.svg")

    res3 = subprocess.run([".venv/bin/python", "scripts/render_stats_svg.py"], capture_output=True, text=True)
    assert res3.returncode == 0
    assert os.path.exists("stats.svg")
