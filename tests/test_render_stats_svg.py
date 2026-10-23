import os

def test_make_info_card(tmp_path):
    from scripts.make_info_card import generate_info_card

    out_file = tmp_path / "test_info.svg"
    svg_path = generate_info_card(str(out_file))

    assert os.path.exists(svg_path)
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<svg" in content
    assert "chogerlate@" in content
    assert "Machine Learning" in content or "Now" in content
    assert "</svg>" in content
