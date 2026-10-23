import os
from PIL import Image
import pytest

def test_make_ascii_svg_generates_valid_svg(tmp_path):
    from scripts.make_ascii_svg import generate_ascii_svg

    input_img = tmp_path / "test_prepped.png"
    output_svg = tmp_path / "test_ascii.svg"

    # Create dummy 100x100 grayscale image
    Image.new("L", (100, 100), 200).save(input_img)

    result_path = generate_ascii_svg(
        str(input_img),
        str(output_svg),
        user="chogerlate",
        name="Siwarat Laoprom",
    )
    assert os.path.exists(result_path)

    with open(result_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<svg" in content
    assert 'viewBox="0 0 840 880"' in content or ('width="840"' in content and 'height="880"' in content)
    assert "<clipPath" in content
    assert "<animate" in content
    assert "chogerlate@github" in content
    assert "Siwarat Laoprom" in content
    assert "</svg>" in content
