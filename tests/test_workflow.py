import os

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
