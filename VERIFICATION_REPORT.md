# Verification Report

Date: 2026-06-07

This report reflects **actual** end-to-end verification on this machine. The app
was run, the data validated, the figures regenerated, and both PDFs compiled.
(The previous version of this file incorrectly claimed the app and `pdflatex`
were never run and that `report.tex`/`presentation.tex` were finished — in fact
those two `.tex` files were empty and have since been written from scratch.)

## Environment

- Python 3.11 conda env (`mpg`, reused per the storage constraint; see `USAGE.md`).
- streamlit 1.58.0, pandas 3.0.1, numpy 2.4.3, plotly 6.8.0, kaleido 1.3.0.
- `kaleido` + a headless Chrome (with conda-forge GUI libs) added for static export.
- `tectonic` installed via conda-forge for LaTeX compilation.

## UI redesign (rebuilt presentation layer)

The presentation layer was rebuilt in two passes for visual quality and direct
interaction, guided by *The Big Book of Dashboards* and the sibling reference app:

- **No sidebar.** Navigation is now inline `st.tabs`; every filter sits in a
  bordered in-page toolbar next to the charts it drives (segmented-control pills,
  multiselects, sliders) — you interact with the data directly. This matches the
  reference project's tab-based, sidebar-collapsed pattern.
- **Animated KPIs + density.** BANs now count up (self-contained HTML/JS
  component), sections use dense 2-column chart grids, and a medal-efficiency
  chart (medals per 100 athletes), a day-by-day medal timeline, and an animated
  cumulative race were added — 19 chart builders total (17 exported as figures).
- Because `st.tabs` renders all sections every run, every `st.plotly_chart` got a
  stable explicit `key` (fixes `StreamlitDuplicateElementId` when filtered charts
  collapse to identical empty placeholders).

Guided by the same book in the first pass:

- **No more data dumps.** The two raw `st.dataframe` tables (the 11-column medal
  table and the venue table) were removed. Values are now shown visually — a
  gold/silver/bronze **podium**, ranked bars, and a new busiest-venues bar —
  with detail on hover.
- **BANs.** Each section opens with headline KPI cards (some live-updating with
  the filters), built as custom HTML.
- **Colourblind-safe colour.** `src/utils.py` now uses the Okabe–Ito palette;
  hardcoded chart colours were routed through shared constants, so the live app
  and the exported figures match.
- **Visual hierarchy.** Hero banner, a 5-step "stepper", custom section headers,
  story-note captions, an inline control bar (no sidebar), and chart cards.
- Screenshots of all five redesigned sections are in `docs/screenshots/`,
  captured from the running server with Playwright.

Verified after the rebuild: AppTest still passes all sections + filters (below),
and `scripts/make_figures.py` re-exported all 17 figures with the new palette.

## App — run and driven (PASS)

- Headless server (`streamlit run app.py --server.headless true`) starts clean
  and serves HTTP 200; no tracebacks in the startup log.
- All **5 sections** and **every inline filter** were exercised programmatically
  via `streamlit.testing.v1.AppTest`:
  - Each section rendered with default filters — 0 exceptions.
  - Filter-stress cases (country focus + small top-N; discipline + Female +
    Medalist; empty medal-colors; Male-only geography; near-empty narrow combo)
    — 0 exceptions; empty selections fall back to styled placeholders.
- One low-risk polish applied: replaced deprecated `use_container_width=True`
  with `width="stretch"` (18 call sites) to silence the Streamlit deprecation.

## Data validity (PASS)

Loaders parse every quirk correctly and all documented counts reconcile:

| Quantity | Documented | Verified |
| --- | --- | --- |
| NOCs (`country_stats`) | 206 | 206 |
| Medaling NOCs | — | 91 |
| Athletes | 11,183 | 11,183 |
| Athlete–medal records | 2,271 | 2,271 |
| Enriched athletes | 11,110 | 11,110 |
| Normalized disciplines | 45 | 45 |

- Enriched table parsed correctly despite `;` delimiter, French headers, and
  UTF-8 BOM (20 cols); `medal_countries_tokyo.csv` unnamed index column dropped.
- Dtypes clean: numeric medals/age/coords, `datetime64` dates, boolean flags.
- Missing data documented (not imputed): height 6,033/11,110 (54%); venue
  coordinates 1,715 (15%, mostly "multisite") → 41 mapped venues.
- Country totals vs. athlete–medal records kept as distinct concepts on separate
  pages. No real loader bugs found.

## Figures (PASS)

- `scripts/make_figures.py` regenerates **17** figures as vector PDF + high-DPI
  PNG from the same prepared data and `src/visualizations.py` builders the app
  uses. One command; all 17 export successfully.

## Report and slides (PASS)

- `report.tex` written from scratch → `report.pdf` (21 pages) compiles clean with
  `tectonic`. Per-chapter Technique Application (Ch. 1–9), dataset overview,
  data-cleaning notes, embedded vector figures, and insights.
- `presentation.tex` written from scratch → `presentation.pdf` (14 slides)
  compiles clean. Title, dataset, objective, technique map, 6 key visualizations,
  interaction/storytelling, insights, close.

## Known limitations / assumptions

- The reused env is named `mpg` (not a fresh `dataviz261`) due to disk pressure;
  `requirements.txt` + `USAGE.md` capture the exact versions to recreate it.
- A pixel-perfect browser screenshot of the live app was **not** included:
  headless Chrome captures only Streamlit's loading skeleton (charts render via
  an async websocket). Evidence of rendering is instead the AppTest pass and the
  17 exported Plotly figures (the dashboard's own charts).
- Figure export and Chrome require the GUI libs in `USAGE.md`; the pipeline sets
  `LD_LIBRARY_PATH` itself so the export is self-contained.

## Rebuild commands

```bash
conda activate mpg
python scripts/make_figures.py          # writes figures/ at repo root
( cd report_and_slides && tectonic report.tex && tectonic presentation.tex )
streamlit run app.py
```
