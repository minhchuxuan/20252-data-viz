#!/usr/bin/env python
"""Reproducible figure-export pipeline for the Paris 2024 dashboard report.

This script loads the SAME prepared data used by the live Streamlit app
(``src.data_loader`` + ``src.data_processing``) and the SAME chart builders
(``src.visualizations``), then exports every figure used in the LaTeX report
and slides as a vector PDF (preferred for LaTeX) and a high-DPI PNG (preview).

Run from the project root with the project env active:

    conda activate mpg
    python scripts/make_figures.py

One command regenerates every figure in ``figures/``. No mock data, no manual
screenshots: the figures are exactly what the dashboard renders.

Static export uses Plotly + Kaleido, which drives a headless Chrome. The Chrome
binary (installed via ``plotly_get_chrome``) needs GUI shared libraries; we add
the active conda env's ``lib`` directory to ``LD_LIBRARY_PATH`` before Kaleido
launches Chrome so the export works without system-wide installs.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

# --- Make the headless-Chrome export self-contained -------------------------
# Kaleido 1.x launches Chrome as a subprocess; it inherits this process's env.
# Prepending the env lib dir lets Chrome resolve libatk/pango/cairo/etc. that
# were installed into the conda env rather than system-wide.
_ENV_LIB = Path(sys.prefix) / "lib"
if _ENV_LIB.is_dir():
    os.environ["LD_LIBRARY_PATH"] = f"{_ENV_LIB}:{os.environ.get('LD_LIBRARY_PATH', '')}"

# Project root on path so ``import src...`` works regardless of CWD.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

warnings.filterwarnings("ignore")  # silence Streamlit "no runtime" + Plotly notes

from src.data_loader import load_data  # noqa: E402
from src.data_processing import (  # noqa: E402
    apply_country_filter,
    apply_medal_filters,
    apply_athlete_filters,
    prepare_datasets,
    summarize_venues,
)
from src import visualizations as viz  # noqa: E402

FIGURES_DIR = ROOT / "figures"

# Consistent ranking depth across every figure so the report reads coherently.
TOP_N = 15

# Default export geometry (px). Vector PDF is resolution-independent; PNG uses
# scale=2 for crisp previews. Tall ranked charts get extra height.
W, H = 1100, 620


def _build_figures():
    """Return an ordered list of (slug, figure, height) for export."""
    frames = prepare_datasets(load_data())

    countries = apply_country_filter(frames["country_stats"], [])
    medals = apply_medal_filters(frames["medals"])
    athletes = apply_athlete_filters(frames["enriched_athletes"])
    venues = summarize_venues(athletes)

    # (slug, figure, height-in-px) — slugs match \includegraphics in report.tex
    specs = [
        ("world_medal_map", viz.create_world_medal_map(countries), 560),
        ("medal_composition", viz.create_stacked_medal_bar(countries, top_n=TOP_N, sort_by="total"), 640),
        ("athletes_vs_medals", viz.create_athletes_vs_medals(countries), 560),
        ("tokyo_delta", viz.create_paris_tokyo_delta(countries, top_n=10), 620),
        ("medal_efficiency", viz.create_efficiency_bar(countries, top_n=12), 520),
        ("daily_medals", viz.create_daily_medal_chart(athletes), 520),
        ("discipline_medals", viz.create_discipline_medal_bar(medals, top_n=TOP_N), 640),
        ("specialization_heatmap", viz.create_country_discipline_heatmap(medals, top_countries=14, top_disciplines=16), 620),
        ("medal_flow_sankey", viz.create_medal_flow_sankey(medals, top_countries=8, top_disciplines=9), 600),
        ("medal_treemap", viz.create_medal_treemap(medals, top_disciplines=14), 600),
        ("age_distribution", viz.create_age_histogram(athletes), 520),
        ("gender_balance", viz.create_gender_balance_by_discipline(athletes, top_n=TOP_N), 640),
        ("age_by_discipline", viz.create_age_boxplot_by_discipline(athletes, top_n=TOP_N), 640),
        ("competition_load", viz.create_competition_load_scatter(athletes), 560),
        ("venue_geography", viz.create_venue_map(venues), 600),
        ("records_by_discipline", viz.create_record_bar(athletes, top_n=TOP_N), 540),
    ]
    return specs


def main() -> int:
    FIGURES_DIR.mkdir(exist_ok=True)
    specs = _build_figures()
    print(f"Exporting {len(specs)} figures to {FIGURES_DIR} (PDF + PNG)...\n")

    failures = []
    for slug, fig, height in specs:
        pdf = FIGURES_DIR / f"{slug}.pdf"
        png = FIGURES_DIR / f"{slug}.png"
        # Export on an opaque white canvas. The live app uses a transparent
        # background to blend into its CSS theme, but transparent PNG/PDF print
        # unpredictably (dark in some viewers, invisible on dark slides). White
        # is the safe, neutral canvas for LaTeX and print.
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
        try:
            fig.write_image(str(pdf), width=W, height=height)
            fig.write_image(str(png), width=W, height=height, scale=2)
            print(f"  ok   {slug:24s}  pdf={pdf.stat().st_size//1024:>4d}KB  png={png.stat().st_size//1024:>4d}KB")
        except Exception as exc:  # pragma: no cover - export environment issue
            failures.append((slug, exc))
            print(f"  FAIL {slug:24s}  {type(exc).__name__}: {exc}")

    print()
    if failures:
        print(f"{len(failures)} figure(s) failed to export.")
        return 1
    print(f"All {len(specs)} figures exported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
