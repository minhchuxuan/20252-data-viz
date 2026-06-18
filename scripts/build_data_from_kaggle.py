"""Build the project's ``data/`` CSVs from the official Kaggle datasets.

Source (both findable on Google Dataset Search):
  * Kaggle "Paris 2024 Olympic Summer Games" (piterfm) -> core athlete/medal tables
  * Kaggle "Tokyo 2020 Olympic Summer Games" (piterfm) -> Tokyo medal table (delta)
  * data.gouv.fr "Les athletes des JO de Paris 2024" -> enriched athlete CSV (kept as-is)

This script transforms the official Kaggle files into the exact column schema the
dashboard already expects (``src/data_loader.py`` / ``src/data_processing.py``),
so the application code does not change. Run after downloading + unzipping the two
Kaggle datasets:

    kaggle datasets download -d piterfm/paris-2024-olympic-summer-games -p /tmp/kaggle_paris --unzip
    kaggle datasets download -d piterfm/tokyo-2020-olympics          -p /tmp/kaggle_tokyo --unzip
    python scripts/build_data_from_kaggle.py
"""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd

PARIS = Path("/tmp/kaggle_paris")
TOKYO = Path("/tmp/kaggle_tokyo")
OUT = Path(__file__).resolve().parent.parent / "data"


def _explode_list(df: pd.DataFrame, col: str, new: str) -> pd.DataFrame:
    rows = []
    for code, val in zip(df["code"], df[col]):
        try:
            items = ast.literal_eval(val) if isinstance(val, str) else []
        except (ValueError, SyntaxError):
            items = []
        if not isinstance(items, (list, tuple)):
            items = [items]
        for it in items:
            rows.append((code, it))
    return pd.DataFrame(rows, columns=["code", new])


def main() -> None:
    a = pd.read_csv(PARIS / "athletes.csv", low_memory=False)
    medl = pd.read_csv(PARIS / "medallists.csv", low_memory=False)
    mt = pd.read_csv(PARIS / "medals_total.csv")
    tok = pd.read_csv(TOKYO / "medals_total.csv")

    # athletes.csv  ->  code,name,birthDate,height,gender,country_code,country_name,country_name_long
    pd.DataFrame({
        "code": a["code"], "name": a["name"], "birthDate": a["birth_date"],
        "height": a["height"], "gender": a["gender"],
        "country_code": a["country_code"], "country_name": a["country"],
        "country_name_long": a["country_long"],
    }).to_csv(OUT / "athletes.csv", index=False)

    # medals.csv (athlete-medal records, keyed by NOC code) -> code,name,discipline,event,color
    md = medl[medl["is_medallist"] == True].copy()  # noqa: E712
    medals = pd.DataFrame({
        "code": md["country_code"], "name": md["name"], "discipline": md["discipline"],
        "event": md["event"], "color": md["medal_type"].str.replace(" Medal", "", regex=False),
    })
    medals.to_csv(OUT / "medals.csv", index=False)

    # medallists.csv (athlete medal totals) -> code,name,gold,silver,bronze
    # Keyed by NOC code (string) so the downstream country merge stays type-clean;
    # athlete identity is preserved by ``name``. (This table is auxiliary.)
    piv = (md.assign(v=1)
           .pivot_table(index=["country_code", "name"], columns="medal_type",
                        values="v", aggfunc="sum", fill_value=0).reset_index())
    for c in ["Gold Medal", "Silver Medal", "Bronze Medal"]:
        if c not in piv:
            piv[c] = 0
    pd.DataFrame({
        "code": piv["country_code"], "name": piv["name"],
        "gold": piv["Gold Medal"], "silver": piv["Silver Medal"], "bronze": piv["Bronze Medal"],
    }).to_csv(OUT / "medallists.csv", index=False)

    # medal_countries.csv -> code,country,gold,silver,bronze (official rank order)
    (pd.DataFrame({
        "code": mt["country_code"], "country": mt["country"],
        "gold": mt["Gold Medal"], "silver": mt["Silver Medal"], "bronze": mt["Bronze Medal"],
    }).sort_values(["gold", "silver", "bronze"], ascending=False)
      .reset_index(drop=True)
      .to_csv(OUT / "medal_countries.csv", index=False))

    # medal_countries_tokyo.csv -> code,country,gold,silver,bronze
    pd.DataFrame({
        "code": tok["Country Code"], "country": tok["Country"],
        "gold": tok["Gold Medal"], "silver": tok["Silver Medal"], "bronze": tok["Bronze Medal"],
    }).to_csv(OUT / "medal_countries_tokyo.csv", index=False)

    # athletes_disciplines.csv / athletes_events.csv (membership, exploded from list cols)
    _explode_list(a, "disciplines", "disciplines").to_csv(OUT / "athletes_disciplines.csv", index=False)
    _explode_list(a, "events", "events").to_csv(OUT / "athletes_events.csv", index=False)

    print("Wrote:", ", ".join(sorted(p.name for p in OUT.glob("*.csv"))))


if __name__ == "__main__":
    main()
