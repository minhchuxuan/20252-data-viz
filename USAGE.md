# Usage Guide

This guide records the **exact, reproducible** commands used to set up, run,
verify, and rebuild every deliverable on this machine.

## 1. Environment

- Python **3.11** (the original `requirements.txt` pins lacked Python-3.13 wheels).
- A dedicated conda env. On this machine an existing suitable Python-3.11 env
  (`mpg`) was reused instead of creating a new one, because disk space was tight
  (`/mnt` was at 97%). It already provided streamlit, pandas, plotly, and numpy;
  only `kaleido` (+ a headless Chrome) had to be added.

### Fresh setup (recommended for a clean machine)

```bash
source /mnt/tp/miniconda/etc/profile.d/conda.sh
conda create -y -n dataviz261 python=3.11
conda activate dataviz261
pip install --upgrade pip
pip install -r requirements.txt
```

### Reusing an existing env (what was done here)

```bash
source /mnt/tp/miniconda/etc/profile.d/conda.sh
conda activate mpg            # Python 3.11, already had streamlit/pandas/plotly/numpy
pip install kaleido           # the one missing piece for figure export
```

Verified working versions (also pinned in `requirements.txt`):
streamlit 1.58.0, pandas 3.0.1, numpy 2.4.3, plotly 6.8.0, kaleido 1.3.0.

### One-time setup for static figure export (kaleido + Chrome)

`kaleido` 1.x renders figures through a headless Chrome. Install the browser and,
on a minimal Linux box, the GUI shared libraries it needs (no root required —
everything goes into the conda env / user dir):

```bash
conda activate mpg
plotly_get_chrome -y          # downloads Chrome for Plotly into ~/.local/share/choreographer

# Chrome's runtime libraries, installed into the env (only needed if missing system-wide):
conda install -n mpg -c conda-forge -y \
  gtk3 atk-1.0 at-spi2-atk at-spi2-core pango cairo gdk-pixbuf \
  nss nspr dbus libcups alsa-lib mesalib libxkbcommon \
  xorg-libxcomposite xorg-libxdamage xorg-libxfixes xorg-libxrandr \
  xorg-libxtst xorg-libxrender xorg-libxext xorg-libx11 xorg-libxcb
```

`scripts/make_figures.py` automatically prepends the env's `lib/` directory to
`LD_LIBRARY_PATH` before Kaleido launches Chrome, so figure export is
self-contained — no manual `export` needed.

## 2. Run the Dashboard

```bash
conda activate mpg
streamlit run app.py
# headless demo:
streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

### How to use it

There is **no sidebar**. Switch chapters with the **tabs** at the top:

1. **Opening Lens** — global scale and medal geography.
2. **Medal Race** — leaders, podium, Paris-vs-Tokyo movement, medal efficiency.
3. **Specialization** — discipline strengths, heatmap, treemap, flow graph.
4. **Athlete Lens** — age, gender, workload, medals.
5. **Geography** — venue map, competition rhythm, busiest venues, records.

Every control is **inline**, in a toolbar next to the charts it drives:
segmented-control pills (gender, medal status, medal colours, sort), multiselects
(focus NOCs / disciplines), and sliders (top-N, age range). Empty/narrow
selections fall back to a styled "no data" placeholder rather than crashing.
Plotly charts support hover, zoom, pan, and legend toggling.

## 3. Regenerate Report Figures

One command rebuilds every figure used by the report and slides, as vector PDF
**and** high-DPI PNG, into `figures/`:

```bash
conda activate mpg
python scripts/make_figures.py     # 17 figures -> figures/*.pdf + figures/*.png
```

The script loads the **same** prepared data and the **same**
`src/visualizations.py` builders the live app uses, so the figures are exactly
what the dashboard renders (no screenshots, no mock data).

## 4. Compile the Report and Slides

A LaTeX engine is installed via conda (`tectonic`, no root needed):

```bash
conda install -n mpg -c conda-forge -y tectonic
conda activate mpg
cd report_and_slides         # the .tex sources live here
tectonic report.tex          # -> report.pdf
tectonic presentation.tex    # -> presentation.pdf
```

The sources resolve `figures/` one level up via `\graphicspath`, so regenerate
figures from the repo root (`python scripts/make_figures.py`) and compile from
inside `report_and_slides/`.

Tectonic resolves cross-references and downloads any missing packages
automatically, so a single pass per file is enough. The design uses a
charcoal / gold / teal / coral palette rather than a default template.

## 5. Verification Performed

- **App, end-to-end:** all five sections and every inline filter were driven
  programmatically with Streamlit's `AppTest` harness (`streamlit.testing.v1`),
  including empty- and narrow-filter stress cases, with **zero exceptions**. The
  headless server also starts clean and serves HTTP 200.
- **Charts:** all 19 chart builders render with the real data; 17 export to
  PDF/PNG via Kaleido (the animated race and the busiest-venues bar are app-only).
- **Data:** row counts, dtypes, and missing-value rates were checked against the
  documented figures (see `VERIFICATION_REPORT.md` and `dataset_info.md`).

### Quick non-Streamlit sanity check

```bash
conda activate mpg
python - <<'PY'
from src.data_loader import check_data_availability, load_data
from src.data_processing import prepare_datasets
from src import visualizations as viz
print(check_data_availability())
frames = prepare_datasets(load_data())
print({k: v.shape for k, v in frames.items()})
print("map traces:", len(viz.create_world_medal_map(frames["country_stats"]).data))
PY
```

### Optional: live-app screenshots (dev only)

The screenshots in `docs/screenshots/` were captured from the running server.
These tools are **not** app runtime dependencies (not in `requirements.txt`):

```bash
pip install playwright          # Python package only; reuses the Chrome from plotly_get_chrome
# emoji glyphs in headless Chrome (most desktop OSes already have one):
curl -sL -o ~/.local/share/fonts/NotoColorEmoji.ttf \
  https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf && fc-cache -f
```

The app itself needs none of this — it runs in any modern browser.

## 6. Data Refresh

The dataset is already included in `data/`. Refresh commands (URLs) are in
`dataset_info.md`.
