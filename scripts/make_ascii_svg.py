#!/usr/bin/env python3
"""
Convert a portrait photo into a monochrome ASCII-art SVG that "types"
itself in like a terminal, then holds.

Output canvas: 840 x 880 (matches stats card for side-by-side alignment).
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, "..", "source-prepped.png")
DEFAULT_OUT = os.path.join(HERE, "..", "profile-ascii.svg")

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears bg

CANVAS_W = 840
CANVAS_H = 880
PAD = 20
TITLEBAR_H = 30
STATUS_H = 34

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"


def generate_ascii_svg(
    src_path: str,
    out_path: str,
    user: str = "chogerlate",
    name: str = "Siwarat Laoprom",
    cols: int = 180,
    static: bool = False,
) -> str:
    art_w = CANVAS_W - PAD * 2  # 800
    available_h = CANVAS_H - TITLEBAR_H - STATUS_H - PAD * 2  # 776
    cell_w = art_w / cols
    cell_h = cell_w * 15 / 8
    rows = max(1, round(available_h / cell_h))
    actual_art_h = rows * cell_h

    # Center vertically in available space
    art_top = TITLEBAR_H + PAD + (available_h - actual_art_h) / 2

    im = Image.open(src_path).convert("L")
    im = ImageEnhance.Brightness(im).enhance(1.0)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = im.resize((cols, rows), Image.LANCZOS)
    px = im.load()

    gamma = 1.18
    white_floor = 0.80

    rows_txt = []
    for y in range(rows):
        chars = []
        for x in range(cols):
            lum = px[x, y] / 255.0
            lum = pow(lum, gamma)
            if lum >= white_floor:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows_txt.append("".join(chars))

    total_dur = 5.8
    row_dur = total_dur / rows
    stagger = row_dur

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<style>',
        '@media (prefers-reduced-motion: reduce) {',
        '  clipPath rect { width: 100% !important; animation: none !important; }',
        '  rect.cursor { display: none !important; }',
        '}',
        '</style>',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
                 f'text-anchor="middle">{user}@github: ~$ ./portrait.sh</text>')

    font_size = cell_h * 0.86
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * cell_h + cell_h * 0.74
        row_y = art_top + ry * cell_h
        delay = ry * stagger
        safe = html.escape(line)
        text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
                f'font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacing">{safe}</text>')

        if static:
            parts.append(text)
            continue

        parts.append(
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{cell_h}" width="0">'
            f'<animate attributeName="width" from="0" to="{art_w}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        parts.append(
            f'<rect class="cursor" y="{row_y+1:.1f}" width="{cell_w}" height="{cell_h-2}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+art_w}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+row_dur:.3f}s"/></rect>'
        )

    # Status line
    status_line_y = CANVAS_H - STATUS_H
    status_y = status_line_y + 22
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="14">'
                 f'{user}@github:~$ whoami <tspan fill="{INK}">{name}</tspan></text>')
    status_prompt_str = f"{user}@github:~$ whoami {name} "
    cursor_x = PAD + len(status_prompt_str) * 14 * 0.58
    parts.append(f'<rect x="{cursor_x:.1f}" y="{status_y-13:.1f}" width="8" height="15" fill="{INK}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')

    parts.append("</svg>")
    svg = "".join(parts)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out_path}: {CANVAS_W} x {CANVAS_H}, {len(svg)//1024} KB")
    return out_path


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    is_static = bool(os.environ.get("STATIC"))
    user = os.environ.get("GH_PROFILE_USER", "chogerlate")
    name = os.environ.get("GH_PROFILE_NAME", "Siwarat Laoprom")
    generate_ascii_svg(src, out, user=user, name=name, static=is_static)
