import os
from PIL import Image

def test_make_ascii_svg_generates_valid_svg(tmp_path):
    import subprocess
    import sys

    input_img = tmp_path / "test_prepped.png"
    output_svg = tmp_path / "test_ascii.svg"

    Image.new("L", (100, 100), 200).save(input_img)

    res = subprocess.run([sys.executable, "scripts/make_ascii_svg.py", str(input_img), str(output_svg)], capture_output=True, text=True)
    assert res.returncode == 0
    assert os.path.exists(output_svg)

    with open(output_svg, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<svg" in content
    assert "<clipPath" in content
    assert "<animate" in content
    assert "chogerlate@github" in content
    assert "</svg>" in content
