"""Data loading for the Paris 2024 Olympic dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REQUIRED_FILES = [
    "athletes.csv",
    "athletes_disciplines.csv",
    "athletes_events.csv",
    "medals.csv",
    "medallists.csv",
    "medal_countries.csv",
    "medal_countries_tokyo.csv",
    "paris2024_athletes_enriched.csv",
]


def check_data_availability(data_dir: Path = DATA_DIR) -> tuple[bool, list[str]]:
    """Return whether all required CSV files are present."""
    missing = [name for name in REQUIRED_FILES if not (data_dir / name).exists()]
    return len(missing) == 0, missing


@st.cache_data(show_spinner=False)
def load_data(data_dir: str | Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Load all dashboard CSV files.

    The enriched athlete table comes from data.gouv.fr and uses semicolon
    delimiters. The other tables are built from the official Kaggle "Paris 2024
    Olympic Summer Games" dataset by ``scripts/build_data_from_kaggle.py``.
    """
    data_path = Path(data_dir)
    return {
        "athletes": pd.read_csv(data_path / "athletes.csv"),
        "athletes_disciplines": pd.read_csv(data_path / "athletes_disciplines.csv"),
        "athletes_events": pd.read_csv(data_path / "athletes_events.csv"),
        "medals": pd.read_csv(data_path / "medals.csv"),
        "medallists": pd.read_csv(data_path / "medallists.csv"),
        "medal_countries": pd.read_csv(data_path / "medal_countries.csv"),
        "medal_countries_tokyo": pd.read_csv(data_path / "medal_countries_tokyo.csv"),
        "enriched_athletes": pd.read_csv(
            data_path / "paris2024_athletes_enriched.csv",
            sep=";",
        ),
    }
