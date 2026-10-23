# Animated Terminal GitHub Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete terminal-aesthetic animated GitHub profile README for `chogerlate` with a monochrome typing ASCII portrait, an animated contribution heatmap, an animated stats card, and daily GitHub Actions automation.

**Architecture:** A suite of modular Python scripts processes profile assets and fetches live public contribution data, rendering self-contained animated SVGs (via SMIL and CSS keyframes) that are embedded in `README.md` with zero third-party hosted dependencies. A GitHub Actions workflow runs on a daily cron to scrape fresh contributions and commit updated SVGs.

**Tech Stack:** Python 3.11, `rembg`, `opencv-python`, `pillow`, `numpy`, `beautifulsoup4`, `requests`, SVG (SMIL & CSS3), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-23-animated-terminal-profile-design.md`

## Global Constraints
- Target GitHub username is `chogerlate`.
- Profile image must be sourced from `/home/cgl/Pictures/110090132.png`.
- All animated graphics must be standalone SVGs; no client-side JavaScript or external hosted widgets.
- SVGs must render correctly inside GitHub README `<img>` tags.
- Canvas dimensions must align cleanly: `contrib-heatmap.svg` width = 860px; `profile-ascii.svg` (840x880) and `stats.svg` (840x880) rendered in a table at width = 420px each (420 + 420 = 840 ≈ 860).
- Daily workflow must run without personal access tokens (using GitHub's public endpoint) and push with `contents: write` and `[skip ci]`.

## Review Focus
1. **GitHub HTML Markup Changes**: If GitHub changes its contributions HTML structure, `fetch_contributions.py` must fail gracefully or handle missing tooltips.
2. **Empty or Zero Contributions**: If user has 0 contributions on certain days or no streaks, calculations must not crash (avoid division by zero).
3. **Aspect Ratio and SVG Alignment**: Portrait and stats cards must maintain equal aspect ratios so the side-by-side table rows align vertically without distortion.
4. **Reduced Motion**: All animated SVGs should respect `@media (prefers-reduced-motion: reduce)` by showing static final states.
5. **Image Background Removal**: Low-contrast subject edges must not create halos or noisy artifacts in the ASCII output.

---

### Task 1: Environment Setup & Photo Asset Ingestion

**Files:**
- Create: `scripts/requirements.txt`
- Create: `source-photo.png` (copied from `/home/cgl/Pictures/110090132.png`)

**Interfaces:**
- Produces: `scripts/requirements.txt` with dependencies, `.venv` virtual environment with Python 3.11, `source-photo.png` as input for preprocessing.

- [ ] **Step 1: Create requirements.txt**

Write `scripts/requirements.txt`:
```txt
requests==2.32.3
beautifulsoup4==4.12.3
pillow>=10.0.0
numpy>=1.24.0
opencv-python-headless>=4.8.0
rembg>=2.0.50
```

- [ ] **Step 2: Copy reference photo into repository**

Copy `/home/cgl/Pictures/110090132.png` to `source-photo.png` in the repo root.

- [ ] **Step 3: Install dependencies in .venv**

Run: `uv pip install -r scripts/requirements.txt` in `.venv`.
Verify imports with `python -c "import rembg, cv2, PIL, bs4, requests; print('OK')"`.

- [ ] **Step 4: Commit**

```bash
git add scripts/requirements.txt source-photo.png
git commit -m "chore: setup dependencies and ingest source photo"
```

---

### Task 2: Photo Preprocessing Pipeline (`scripts/prep_photo.py`)

**Files:**
- Create: `scripts/prep_photo.py`
- Test: `tests/test_prep_photo.py`
- Output: `source-prepped.png`

**Interfaces:**
- Consumes: `source-photo.png`
- Produces: `source-prepped.png` (grayscale square-cropped image ready for ASCII generation)

- [ ] **Step 1: Write test for photo prep**

Create `tests/test_prep_photo.py` that executes `prep_photo.py` on a dummy image or verifies `prep_image(input_path, output_path)` outputs a valid square grayscale PNG.

- [ ] **Step 2: Implement `scripts/prep_photo.py`**

Implement image preprocessing:
1. Subject cutout using `rembg.remove`.
2. Bilateral filtering (`cv2.bilateralFilter`) for skin smoothing while keeping edges crisp.
3. Tone stretching based on subject percentile.
4. Difference-of-Gaussians ridge detection for edge enhancement.
5. Composite over pure white and crop square with margin.
Output file path configurable via CLI args (defaulting to `source-prepped.png`).

- [ ] **Step 3: Run script on `source-photo.png` and verify output**

Run: `.venv/bin/python scripts/prep_photo.py source-photo.png source-prepped.png`
Verify: `source-prepped.png` exists and is a square grayscale image.

- [ ] **Step 4: Commit**

```bash
git add scripts/prep_photo.py tests/test_prep_photo.py source-prepped.png
git commit -m "feat: add photo preprocessing script and generate source-prepped.png"
```

---

### Task 3: Monochrome Typing ASCII SVG Generator (`scripts/make_ascii_svg.py`)

**Files:**
- Create: `scripts/make_ascii_svg.py`
- Test: `tests/test_make_ascii_svg.py`
- Output: `profile-ascii.svg`

**Interfaces:**
- Consumes: `source-prepped.png`
- Produces: `profile-ascii.svg` (840x880 SVG with SMIL clip-path wipe animation and status prompt `chogerlate@github:~$ whoami`)

- [ ] **Step 1: Write test for ASCII SVG generation**

Create `tests/test_make_ascii_svg.py` to verify generated SVG contains `<svg>`, `<clipPath>`, `<animate>`, `chogerlate@github`, and valid 840x880 dimensions.

- [ ] **Step 2: Implement `scripts/make_ascii_svg.py`**

Implement character grid conversion:
1. Grayscale luminance sampling with gamma curve and white floor cutoff.
2. Density ramp: `" .`:-=+*cs#%@"`.
3. Terminal window decoration (title bar `chogerlate@github: ~$ ./portrait.sh` with macOS window buttons).
4. SMIL row-by-row clip-wipe animation with typing cursor block.
5. Bottom status prompt: `chogerlate@github:~$ whoami Siwarat Laoprom` with blinking terminal cursor.
6. Canvas dimension: 840 x 880.

- [ ] **Step 3: Run generator and verify SVG**

Run: `.venv/bin/python scripts/make_ascii_svg.py source-prepped.png profile-ascii.svg`
Verify: `profile-ascii.svg` is generated and valid.

- [ ] **Step 4: Commit**

```bash
git add scripts/make_ascii_svg.py tests/test_make_ascii_svg.py profile-ascii.svg
git commit -m "feat: add ASCII portrait SVG generator and generate profile-ascii.svg"
```

---

### Task 4: Public Contributions Scraper (`scripts/fetch_contributions.py`)

**Files:**
- Create: `scripts/fetch_contributions.py`
- Test: `tests/test_fetch_contributions.py`
- Output: `data/contributions.json`

**Interfaces:**
- Consumes: GitHub public URL `https://github.com/users/{username}/contributions`
- Produces: `data/contributions.json` containing total contributions, active days, streaks, and day-by-day counts.

- [ ] **Step 1: Write test for scraper and metrics computation**

Create `tests/test_fetch_contributions.py` with mock HTML fixtures to verify parsing of days, levels, current streak, longest streak, and monthly aggregations.

- [ ] **Step 2: Implement `scripts/fetch_contributions.py`**

Implement:
1. Fetch HTML from `https://github.com/users/{username}/contributions` (default `chogerlate`, overridable by `GH_PROFILE_USER` env var).
2. Parse `td.ContributionCalendar-day` and `<tool-tip>` tags.
3. Compute current streak (gracefully handling in-progress current day).
4. Compute longest streak, active days, average per active day, and best day.
5. Aggregate monthly totals.
6. Save structured JSON to `data/contributions.json`.

- [ ] **Step 3: Run live scrape for `chogerlate`**

Run: `.venv/bin/python scripts/fetch_contributions.py`
Verify: `data/contributions.json` is generated with valid streak metrics for `chogerlate`.

- [ ] **Step 4: Commit**

```bash
git add scripts/fetch_contributions.py tests/test_fetch_contributions.py data/contributions.json
git commit -m "feat: add public contribution scraper and fetch initial data"
```

---

### Task 5: Animated Contribution Heatmap SVG Generator (`scripts/render_heatmap_svg.py`)

**Files:**
- Create: `scripts/render_heatmap_svg.py`
- Test: `tests/test_render_heatmap_svg.py`
- Output: `contrib-heatmap.svg`

**Interfaces:**
- Consumes: `data/contributions.json`
- Produces: `contrib-heatmap.svg` (860px wide animated SVG)

- [ ] **Step 1: Write test for heatmap SVG renderer**

Create `tests/test_render_heatmap_svg.py` to verify rendered SVG contains title bar `chogerlate@github: ~/contributions --graph`, month/weekday labels, rounded rects with animation delays, legend, and footer stats.

- [ ] **Step 2: Implement `scripts/render_heatmap_svg.py`**

Implement:
1. 53-week x 7-day calendar matrix layout.
2. Color mapping: `["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]`.
3. CSS diagonal slide-down animation with `@media (prefers-reduced-motion: reduce)`.
4. Header title bar with terminal buttons and prompt.
5. Month labels (top) and Day-of-week labels (Mon, Wed, Fri).
6. "Less" to "More" legend.
7. Footer showing total contributions in the last year, date range, current streak, longest streak, and best day.
8. Output canvas width: 860px.

- [ ] **Step 3: Run renderer and verify output**

Run: `.venv/bin/python scripts/render_heatmap_svg.py`
Verify: `contrib-heatmap.svg` exists and has width 860.

- [ ] **Step 4: Commit**

```bash
git add scripts/render_heatmap_svg.py tests/test_render_heatmap_svg.py contrib-heatmap.svg
git commit -m "feat: add animated contribution heatmap SVG generator"
```

---

### Task 6: Terminal Stats Card & Neofetch Card Generators (`scripts/render_stats_svg.py` & `scripts/make_info_card.py`)

**Files:**
- Create: `scripts/render_stats_svg.py`
- Create: `scripts/make_info_card.py`
- Test: `tests/test_render_stats_svg.py`
- Output: `stats.svg` and `info-card.svg`

**Interfaces:**
- Consumes: `data/contributions.json`
- Produces: `stats.svg` (840x880 terminal stats card) and `info-card.svg` (neofetch-style terminal info card).

- [ ] **Step 1: Write test for stats card renderer**

Create `tests/test_render_stats_svg.py` checking tile count, count-up animations, monthly bar chart elements, and 840x880 viewBox.

- [ ] **Step 2: Implement `scripts/render_stats_svg.py`**

Implement:
1. 840x880 canvas matching `profile-ascii.svg`.
2. Title bar: `chogerlate@github: ~$ ./stats.sh`.
3. 6 animated stat tiles (current streak, longest streak, total contributions, active days, best day, avg / active day) with SMIL `<set>` count-up frames.
4. Animated monthly bar chart with growing bars (`scaleY` CSS animation) and monthly letter labels.
5. Output `stats.svg`.

- [ ] **Step 3: Implement `scripts/make_info_card.py`**

Implement neofetch-style SVG generator with:
1. OS / System information aesthetic: `chogerlate@kmutt`.
2. Key-value fields: Role, Focus, Languages & Tools, Portfolio, Location.
3. Slide & fade-in animations for each row.
4. Output `info-card.svg`.

- [ ] **Step 4: Run both generators and verify outputs**

Run:
```bash
.venv/bin/python scripts/render_stats_svg.py
.venv/bin/python scripts/make_info_card.py
```
Verify `stats.svg` and `info-card.svg` exist and render cleanly.

- [ ] **Step 5: Commit**

```bash
git add scripts/render_stats_svg.py scripts/make_info_card.py tests/test_render_stats_svg.py stats.svg info-card.svg
git commit -m "feat: add animated stats card and neofetch info card generators"
```

---

### Task 7: Terminal-Style README.md Layout

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `contrib-heatmap.svg`, `profile-ascii.svg`, `stats.svg`
- Produces: Centered terminal README layout for `chogerlate`

- [ ] **Step 1: Compose terminal-style README.md**

Construct `README.md` featuring:
1. Centered layout with `<div align="center">`.
2. Top section: `<h3><code>chogerlate@github ~ $ ./contributions.sh</code></h3>` with `<img src="./contrib-heatmap.svg" width="860" />`.
3. Mid section: `<h3><code>chogerlate@github ~ $ whoami</code></h3>` with `<table><tr><td valign="top"><img src="./profile-ascii.svg" width="420" /></td><td valign="top"><img src="./stats.svg" width="420" /></td></tr></table>`.
4. Bottom section: `<h3><code>chogerlate@github ~ $ ./links.sh</code></h3>`.
5. Professional badges: Portfolio (`siwarat.xyz`), Medium, LinkedIn, Email, University (KMUTT Computer Engineering).
6. Skills and interests summary preserved from original profile.

- [ ] **Step 2: Verify README rendering and table alignment**

Check HTML tag balancing and image paths.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "feat: update README with terminal-style layout and SVG embeddings"
```

---

### Task 8: GitHub Actions Daily Automation Workflow

**Files:**
- Create: `.github/workflows/update-profile-art.yml`

**Interfaces:**
- Produces: GitHub Actions workflow file that runs daily at 06:17 UTC and on push to `main`

- [ ] **Step 1: Create workflow file**

Write `.github/workflows/update-profile-art.yml`:
```yaml
name: Update profile art

on:
  schedule:
    - cron: "17 6 * * *"
  workflow_dispatch: {}
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  heatmap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install requests==2.32.3 beautifulsoup4==4.12.3

      - name: Scrape real contribution data
        run: python scripts/fetch_contributions.py

      - name: Render animated contribution graph SVG
        run: python scripts/render_heatmap_svg.py

      - name: Render streak / numbers card
        run: python scripts/render_stats_svg.py

      - name: Commit updated art
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: refresh contribution graph [skip ci]"
          file_pattern: "data/contributions.json contrib-heatmap.svg stats.svg"
```

- [ ] **Step 2: Verify workflow file syntax and test end-to-end local generation**

Run the full pipeline locally:
```bash
.venv/bin/python scripts/fetch_contributions.py
.venv/bin/python scripts/render_heatmap_svg.py
.venv/bin/python scripts/render_stats_svg.py
```
Ensure all output files (`data/contributions.json`, `contrib-heatmap.svg`, `stats.svg`, `profile-ascii.svg`) are cleanly generated without errors.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/update-profile-art.yml
git commit -m "ci: add daily GitHub Actions workflow to auto-refresh profile SVGs"
```
