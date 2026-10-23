import os
from PIL import Image
import pytest

def test_prep_photo_creates_square_grayscale_image(tmp_path):
    from scripts.prep_photo import prep_image

    input_img = tmp_path / "test_input.png"
    output_img = tmp_path / "test_output.png"

    # Create dummy 100x120 test image with a circle in the center
    im = Image.new("RGBA", (100, 120), (255, 255, 255, 0))
    for x in range(30, 70):
        for y in range(40, 80):
            im.putpixel((x, y), (50, 50, 50, 255))
    im.save(input_img)

    result_path = prep_image(str(input_img), str(output_img))
    assert os.path.exists(result_path)

    out = Image.open(result_path)
    assert out.mode == "L"
    assert out.width == out.height
