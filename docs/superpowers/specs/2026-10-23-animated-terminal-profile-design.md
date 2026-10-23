# Terminal-Style Animated GitHub Profile Design

**Author:** Antigravity (Pair Programming with user)
**Date:** 2026-10-23
**Target Repository:** `chogerlate/chogerlate`
**Username:** `chogerlate` (Siwarat Laoprom)

## 1. Intent & Overview

Transform `chogerlate`'s GitHub profile README into an animated, terminal-aesthetic showcase inspired by Avi Vashishta's guide. All motion is pushed into self-contained SVGs rendered natively by GitHub via `<img>` tags (leveraging SMIL and CSS keyframes without third-party services or tokens), auto-refreshed daily via GitHub Actions.

## 2. Components & Architecture

### A. Photo Prep & ASCII Portrait
- **Input:** Reference photo `/home/cgl/Pictures/110090132.png` saved as `source-photo.png`.
- **Pipeline (`scripts/prep_photo.py`):**
  - Isolates subject with `rembg`.
  - Applies bilateral smoothing to reduce noise while maintaining sharp contours.
  - Applies CLAHE/tone stretching over subject luminance.
  - Darkens line work (Difference of Gaussians ridges).
  - Composites onto pure white and crops square -> `source-prepped.png`.
- **ASCII Conversion (`scripts/make_ascii_svg.py`):**
  - Samples image to a character grid (~180x96 chars).
  - Density ramp: `" .`:-=+*cs#%@"`.
  - Emits monochrome light-gray (`#c9d1d9`) text.
  - SMIL `<animate>` row-by-row clip-wipe revealing rows from top to bottom with a riding cursor block, then freezes.
  - Canvas: 840x880 px (matching the stats card). Output: `profile-ascii.svg`.

### B. Live GitHub Contribution Scraping
- **Script (`scripts/fetch_contributions.py`):**
  - Fetches unauthenticated public HTML from `https://github.com/users/chogerlate/contributions`.
  - Parses `td.ContributionCalendar-day` and tooltips using BeautifulSoup.
  - Computes current streak, longest streak, active days, best day, monthly totals.
  - Writes `data/contributions.json`.

### C. Animated Contribution Heatmap
- **Script (`scripts/render_heatmap_svg.py`):**
  - Renders 53-week x 7-day grid using GitHub green palette `["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]`.
  - Diagonal CSS slide-down animation (`animation: cell 0.42s cubic-bezier(.2,.8,.2,1) both;` staggered by col/row).
  - Includes Less -> More legend, month and day labels, and summary stats footer.
  - Canvas width: 860 px. Output: `contrib-heatmap.svg`.

### D. Animated Stats Card & Neofetch Card
- **Stats Card (`scripts/render_stats_svg.py`):**
  - Canvas: 840x880 px (exactly matches `profile-ascii.svg`).
  - Terminal title bar with macOS window buttons and title `chogerlate@github: ~$ ./stats.sh`.
  - 6 metric tiles (current streak, longest streak, total contributions, active days, best day, avg/active day).
  - Pre-rendered SMIL `<set>` count-up animation for numbers.
  - Animated monthly contributions bar chart sliding up at the bottom.
  - Output: `stats.svg`.
- **Neofetch Card (`scripts/make_info_card.py`):**
  - Alternative / companion neofetch-style system info card.
  - Output: `info-card.svg`.

### E. Profile README Layout
- **File (`README.md`):**
  - Centered terminal layout.
  - Header prompt: `<h3><code>chogerlate@github ~ $ ./contributions.sh</code></h3>` -> `contrib-heatmap.svg` (860px).
  - Side-by-side table:
    `<table><tr><td valign="top"><img src="./profile-ascii.svg" width="420"/></td><td valign="top"><img src="./stats.svg" width="420"/></td></tr></table>`.
  - Terminal links prompt: `<h3><code>chogerlate@github ~ $ ./links.sh</code></h3>`.
  - Bio: Machine Learning Engineer · AI / MLOps · KMUTT.
  - Shields.io badges for Portfolio (`siwarat.xyz`), Medium, LinkedIn, Email.

### F. GitHub Actions Daily Automation
- **Workflow (`.github/workflows/update-profile-art.yml`):**
  - Triggers on daily cron (`17 6 * * *`), `push` to main, and `workflow_dispatch`.
  - Permissions: `contents: write`.
  - Steps: Checkout, setup python 3.11, install dependencies, run `fetch_contributions.py`, `render_heatmap_svg.py`, `render_stats_svg.py`.
  - Auto-commit updated `data/contributions.json`, `contrib-heatmap.svg`, `stats.svg` with `[skip ci]`.
