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

    # Must contain SVG references
    assert 'src="./contrib-heatmap.svg"' in content
    assert 'src="./profile-ascii.svg"' in content
    assert 'src="./stats.svg"' in content

    # Check image width alignment (860 heatmap, 420 + 420 table cells)
    assert 'width="860"' in content
    assert content.count('width="420"') == 2

    # Check balanced HTML tags
    div_opens = len(re.findall(r"<div\b", content, re.I))
    div_closes = len(re.findall(r"</div>", content, re.I))
    assert div_opens == div_closes

    table_opens = len(re.findall(r"<table\b", content, re.I))
    table_closes = len(re.findall(r"</table>", content, re.I))
    assert table_opens == table_closes
