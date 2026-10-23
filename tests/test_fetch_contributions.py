import json
import pytest

MOCK_HTML = """
<table>
  <tbody>
    <tr>
      <td id="contribution-day-component-0" class="ContributionCalendar-day" data-date="2026-01-01" data-level="1"></td>
      <td id="contribution-day-component-1" class="ContributionCalendar-day" data-date="2026-01-02" data-level="2"></td>
      <td id="contribution-day-component-2" class="ContributionCalendar-day" data-date="2026-01-03" data-level="0"></td>
      <td id="contribution-day-component-3" class="ContributionCalendar-day" data-date="2026-01-04" data-level="3"></td>
      <td id="contribution-day-component-4" class="ContributionCalendar-day" data-date="2026-01-05" data-level="1"></td>
    </tr>
  </tbody>
</table>
<tool-tip for="contribution-day-component-0">1 contribution on January 1, 2026</tool-tip>
<tool-tip for="contribution-day-component-1">5 contributions on January 2, 2026</tool-tip>
<tool-tip for="contribution-day-component-2">No contributions on January 3, 2026</tool-tip>
<tool-tip for="contribution-day-component-3">12 contributions on January 4, 2026</tool-tip>
<tool-tip for="contribution-day-component-4">3 contributions on January 5, 2026</tool-tip>
"""

BROKEN_TOOLTIP_HTML = """
<table>
  <tbody>
    <tr>
      <td id="contribution-day-component-0" class="ContributionCalendar-day" data-date="2026-01-01" data-level="2"></td>
      <td id="contribution-day-component-1" class="ContributionCalendar-day" data-date="2026-01-02" data-level="3"></td>
    </tr>
  </tbody>
</table>
<!-- No tooltips matching IDs -->
"""

def test_parse_and_build_contributions():
    from scripts.fetch_contributions import parse_contributions_html, build_data

    days = parse_contributions_html(MOCK_HTML)
    assert len(days) == 5
    assert days[0]["date"] == "2026-01-01"
    assert days[0]["count"] == 1
    assert days[2]["count"] == 0

    data = build_data(days, username="testuser")
    assert data["username"] == "testuser"
    assert data["total_contributions"] == 21
    assert data["active_days"] == 4
    assert data["avg_per_active_day"] == 5.2
    assert data["best_day"]["count"] == 12
    assert data["best_day"]["date"] == "2026-01-04"
    assert data["current_streak"]["length"] == 2
    assert data["longest_streak"]["length"] == 2

def test_parse_contributions_detects_tooltip_breakage():
    from scripts.fetch_contributions import parse_contributions_html

    with pytest.raises(ValueError, match="Contribution levels detected, but all counts parsed as 0"):
        parse_contributions_html(BROKEN_TOOLTIP_HTML)
