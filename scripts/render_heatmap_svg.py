#!/usr/bin/env python3
"""
Render data/contributions.json as an animated GitHub-style contribution heatmap SVG.
Canvas width: 860px.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INP = os.path.join(HERE, "..", "data", "contributions.json")
DEFAULT_OUT = os.path.join(HERE, "..", "contrib-heatmap.svg")

# GitHub green palette: empty -> neon peak
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
CANVAS_W = 860
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#1f6feb"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

COL_T = 0.018
ROW_T = 0.045
CELL_DUR = 0.42


def level_for(count: int) -> int:
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(days):
    if not days:
        return []
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # sunday=0
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        count = d.get("count", 0)
        level = d.get("level", level_for(count))
        col.append((d["date"], count, level))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def render_heatmap(data, out_path=DEFAULT_OUT, user=None):
    if user is None:
        user = data.get("username", "chogerlate")

    days = data.get("days", [])
    grid = build_grid(days)
    n_cols = len(grid) if grid else 53
    art_w = n_cols * STEP
    art_h = 7 * STEP

    # Calculate padding to center horizontally inside CANVAS_W (860px)
    pad = max(16, (CANVAS_W - LEFT_LABEL_W - art_w) // 2)
    grid_left = pad + LEFT_LABEL_W
    grid_top = TITLEBAR_H + TOP_LABEL_H

    month_labels = []
    seen_months = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    stats_h = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + pad

    css = f"""
@keyframes cell {{
  0%   {{ opacity: 0; transform: translateY(-6px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
.c {{ opacity: 0; animation: cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
@media (prefers-reduced-motion: reduce) {{
  .c {{ opacity: 1 !important; transform: none !important; animation: none !important; }}
}}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{canvas_h}" '
        f'viewBox="0 0 {CANVAS_W} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{canvas_h}" rx="12" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{canvas_h-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]

    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{pad + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">{user}@github: ~/contributions --graph</text>')

    for ci, label in month_labels:
        x = grid_left + ci * STEP
        parts.append(f'<text x="{x}" y="{TITLEBAR_H + 14}" fill="{MUTED}" font-size="10">{label}</text>')

    for wi, wname in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + wi * STEP + CELL * 0.78
        parts.append(f'<text x="{pad}" y="{y:.1f}" fill="{MUTED}" font-size="9">{wname}</text>')

    # Grid cells
    for ci, column in enumerate(grid):
        gx = grid_left + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            gy = grid_top + ri * STEP
            delay = ci * COL_T + ri * ROW_T
            plural = "s" if count != 1 else ""
            lvl = max(0, min(len(PALETTE) - 1, lvl))
            parts.append(
                f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_s}: {count} contribution{plural}</title></rect>'
            )

    # Legend Less -> More
    leg_y = grid_top + art_h + 8
    leg_x = CANVAS_W - pad - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(f'<text x="{leg_x}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    lx = leg_x + 8
    for lvl, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{color}"/>')
        lx += CELL
    parts.append(f'<text x="{lx + 4}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')

    sep_y = leg_y + CELL + 14
    parts.append(f'<line x1="0" y1="{sep_y}" x2="{CANVAS_W}" y2="{sep_y}" stroke="{FRAME}" stroke-opacity="0.25"/>')

    cs = data.get("current_streak", {}).get("length", 0)
    ls = data.get("longest_streak", {}).get("length", 0)
    total = data.get("total_contributions", 0)
    best = data.get("best_day", {"count": 0, "date": "—"})
    rng = data.get("range", {"start": "—", "end": "—"})

    ly = sep_y + 24
    parts.append(f'<text x="{pad}" y="{ly}" font-size="13" fill="{GREEN}">'
                 f'<tspan font-weight="700">{total:,}</tspan>'
                 f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    parts.append(f'<text x="{CANVAS_W - pad}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'{rng["start"]} &#8594; {rng["end"]}</text>')
    ly += 24
    parts.append(f'<text x="{pad}" y="{ly}" font-size="13" fill="{MUTED}">current streak '
                 f'<tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan>'
                 f'<tspan fill="{MUTED}">   &#183;   longest </tspan>'
                 f'<tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>')
    parts.append(f'<text x="{CANVAS_W - pad}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'best day <tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')

    parts.append("</svg>")
    svg = "".join(parts)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out_path} ({len(svg)} bytes, width {CANVAS_W})")
    return out_path


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INP
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    with open(inp, "r", encoding="utf-8") as f:
        data = json.load(f)
    render_heatmap(data, out)
