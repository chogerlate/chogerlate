import os
import re

def test_readme_structure_and_links():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    assert os.path.exists(readme_path)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must contain terminal prompt sections
    assert "chogerlate@github ~ $ ./contributions.sh" in content
    assert "chogerlate@github ~ $ whoami" in content
    assert "chogerlate@github ~ $ ./links.sh" in content

    # Must contain SVG references matching the guide
    assert 'src="./contrib-heatmap.svg"' in content
    assert 'src="./chogerlate-ascii.svg"' in content or 'src="./avi-ascii.svg"' in content
    assert 'src="./info-card.svg"' in content

    # Check image width alignment (860 heatmap, 370 + 490 table cells)
    assert 'width="860"' in content
    assert 'width="370"' in content
    assert 'width="490"' in content

    # Check balanced HTML tags
    div_opens = len(re.findall(r"<div\b", content, re.I))
    div_closes = len(re.findall(r"</div>", content, re.I))
    assert div_opens == div_closes

    table_opens = len(re.findall(r"<table\b", content, re.I))
    table_closes = len(re.findall(r"</table>", content, re.I))
    assert table_opens == table_closes
