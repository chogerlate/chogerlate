#!/usr/bin/env python3
"""
Generate a neofetch-style terminal info card SVG.
Canvas: 840 x 880 (matches profile-ascii.svg and stats.svg).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "..", "info-card.svg")

W, H = 840, 880
PAD = 28
TITLEBAR_H = 34

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
CYAN = "#22d3ee"
GREEN = "#39d353"
PURPLE = "#bc8cff"
YELLOW = "#e3b341"


def generate_info_card(out_path=DEFAULT_OUT, user="chogerlate", name="Siwarat Laoprom"):
    rows = [
        ("user", f"{user} ({name})", CYAN),
        ("role", "Machine Learning Engineer", GREEN),
        ("host", "Computer Engineering @ KMUTT", YELLOW),
        ("focus", "Deep Learning, Computer Vision, Generative AI, MLOps", TEXT),
        ("frameworks", "PyTorch, TorchVision, OpenCV, HuggingFace", PURPLE),
        ("stack", "Python, C++, Docker, FastAPI, Git, Linux", TEXT),
        ("projects", "https://siwarat.xyz", CYAN),
        ("articles", "medium.com/@siwaratlaoprom", TEXT),
        ("contact", "siwarat.laoprom.forwork@gmail.com", TEXT),
        ("uptime", "Lifelong Learner & AI Builder", GREEN),
    ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<style>',
        '.r { opacity: 0; animation: fadeSlide 0.4s ease-out both; }',
        '@keyframes fadeSlide { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }',
        '@media (prefers-reduced-motion: reduce) { .r { opacity: 1 !important; transform: none !important; animation: none !important; } }',
        '</style>',
        '<defs>',
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">{user}@kmutt: ~$ neofetch</text>')

    # ASCII logo / symbol on left
    logo_lines = [
        r"      /\_/\      ",
        r"     ( o.o )     ",
        r"      > ^ <      ",
        r"   ___________   ",
        r"  /  AI & ML  \  ",
        r" /   ENGINEER  \ ",
        r" \_____________/ ",
        r"    |       |    ",
        r"    |_______|    ",
    ]
    logo_top = TITLEBAR_H + 46
    for i, line in enumerate(logo_lines):
        parts.append(
            f'<text x="{PAD}" y="{logo_top + i * 22}" fill="{CYAN}" font-size="16" '
            f'xml:space="preserve">{line}</text>'
        )

    # Info rows on right
    content_left = PAD + 230
    title_y = TITLEBAR_H + 50
    parts.append(f'<text x="{content_left}" y="{title_y}" font-size="20" font-weight="700" fill="{CYAN}">{user}<tspan fill="{MUTED}">@</tspan>kmutt</text>')
    parts.append(f'<line x1="{content_left}" y1="{title_y + 10}" x2="{W - PAD}" y2="{title_y + 10}" stroke="{FRAME}"/>')

    row_start_y = title_y + 40
    for idx, (label, val, val_color) in enumerate(rows):
        y = row_start_y + idx * 46
        delay = 0.15 + idx * 0.08
        parts.append(f'<g class="r" style="animation-delay:{delay:.2f}s">')
        parts.append(f'<text x="{content_left}" y="{y}" fill="{MUTED}" font-size="16" font-weight="600">{label}:</text>')
        # Truncate long value if needed
        parts.append(f'<text x="{content_left + 140}" y="{y}" fill="{val_color}" font-size="16">{val}</text>')
        parts.append('</g>')

    # Color palette blocks at bottom
    colors = ["#161b22", "#ff5f56", "#27c93f", "#e3b341", "#22d3ee", "#bc8cff", "#f0883e", "#e6edf3"]
    block_y = H - PAD - 26
    parts.append(f'<line x1="{PAD}" y1="{block_y - 18}" x2="{W - PAD}" y2="{block_y - 18}" stroke="{FRAME}"/>')
    bx = content_left
    for c in colors:
        parts.append(f'<rect x="{bx}" y="{block_y}" width="28" height="20" rx="3" fill="{c}"/>')
        bx += 36

    parts.append('</svg>')
    svg = "".join(parts)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out_path}: {W} x {H}, {len(svg)//1024} KB")
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    user = os.environ.get("GH_PROFILE_USER", "chogerlate")
    name = os.environ.get("GH_PROFILE_NAME", "Siwarat Laoprom")
    generate_info_card(out, user=user, name=name)
