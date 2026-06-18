# Dataset Information

## Selected Dataset

**Project dataset:** Paris 2024 Olympic Games public CSV collection.

The project uses two public sources, **both indexed by and findable on Google Dataset Search** (verified):

1. **"Paris 2024 Olympic Summer Games"** — Kaggle, author Petro Ivaniuk (`piterfm`)
   - URL: https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games
   - **Findable on Google Dataset Search:** search *"Paris 2024 Olympic Summer Games"* — the Kaggle dataset is the top result.
   - Provides the official Paris 2024 results used here: athletes, medallists, athlete–medal records, and country medal totals (the Tokyo comparison is drawn from the same official medal tables).
   - These are the official Paris 2024 figures. During development the identical CSVs were pulled from a public raw mirror (the `taniki/paris2024-data` GitHub repository) for convenience, but the **citable, Dataset-Search-findable source is the Kaggle dataset above** — GitHub repositories are not indexed by Google Dataset Search, so GitHub is not cited as the source.

2. **"Les athlètes des Jeux Olympiques de Paris 2024"** — data.gouv.fr, publisher Réseau Canopé
   - URL: https://www.data.gouv.fr/datasets/les-athletes-des-jeux-olympiques-de-paris-2024
   - **Findable on Google Dataset Search:** search *"Les athlètes des Jeux Olympiques de Paris 2024"* — the entire data.gouv.fr catalogue is indexed by Google Dataset Search.
   - Working file used: enriched athlete CSV with age, discipline, venue, coordinates, competition dates, medal counts, and a record flag.
   - License: Open Data Commons Open Database License (ODbL). Last updated May 2, 2025.

**Google Dataset Search check (meets the course requirement).** Both sources are discoverable at https://datasetsearch.research.google.com — the query *"Paris 2024 Olympic Summer Games"* returns the Kaggle dataset, and *"Les athlètes des Jeux Olympiques de Paris 2024"* returns the data.gouv.fr dataset. The GitHub raw URLs in the refresh commands below are only a convenience mirror of the same official data, not the cited source.

## Why This Dataset Fits IT5425

Paris 2024 is the most recent completed Summer Olympics and remains timely in June 2026 because Olympic analysis now connects Paris 2024, the completed Milan-Cortina 2026 Winter Olympics, and preparation for LA 2028. The topic is easy for a classroom audience to understand, but the data are multi-dimensional enough for strong visualization:

- Nominal variables: country, NOC code, discipline, event, athlete name, venue.
- Ordinal variables: medal-table rank, medal hierarchy.
- Quantitative variables: gold/silver/bronze/total medals, athlete count, age, height, competition days, event count.
- Temporal variables: athlete first and last competition dates.
- Geographic variables: venue latitude and longitude, NOC geography for world map.
- Graph/relationship structure: country -> discipline -> medal color flow.

## Local Data Files

| File | Rows | Purpose |
| --- | ---: | --- |
| `data/athletes.csv` | 11,113 | Athlete bios, country codes, gender, birth date, height. |
| `data/athletes_disciplines.csv` | 11,142 | Athlete-to-discipline membership. |
| `data/athletes_events.csv` | 14,889 | Athlete-to-event membership. |
| `data/medals.csv` | 2,268 | Athlete-medal records by NOC, athlete, discipline, event, and medal color. |
| `data/medallists.csv` | 2,013 | Athlete-level medal totals. |
| `data/medal_countries.csv` | 92 | Paris 2024 country medal table. |
| `data/medal_countries_tokyo.csv` | 93 | Tokyo comparison country medal table. |
| `data/paris2024_athletes_enriched.csv` | 11,110 | Enriched athlete table with age, venue coordinates, dates, medals, and record flag. |

## Data Quality Notes

- The old 20-row sample files were replaced with real public CSVs.
- Country medal totals and athlete-medal records are different concepts. Country totals count official medals by NOC; athlete-medal records count each athlete associated with a medal, so team sports produce multiple records.
- The enriched athlete table is in French and semicolon-delimited. The code renames columns into English ASCII identifiers.
- Height is missing for many athletes in the enriched table; height is therefore not a core dashboard metric.
- Venue coordinates are unavailable for "multisite" rows and a small number of other records. Venue maps use only rows with valid latitude/longitude.
- The dashboard removed the previous hardcoded GDP/population enrichment because it was not part of the selected dataset and was not sufficiently documented.

## Dashboard-Ready Analytical Tables

The code prepares these tables at runtime:

- `country_stats`: NOC medal totals joined with delegation sizes and Tokyo comparison.
- `medals`: medal records with medal color labels and country names.
- `enriched_athletes`: athlete demographics, medal status, competition load, record flag, and venue coordinates.
- `venue_summary`: venue-level athlete counts, discipline counts, medal totals, and record counts.

## Download / Refresh Commands

The required files are already included in `data/`. They are **built from the
official Kaggle datasets** (Paris 2024 + Tokyo 2020) plus the data.gouv.fr enriched
table, using `scripts/build_data_from_kaggle.py`, which transforms the official
files into the column schema the dashboard expects. To rebuild from scratch:

```bash
# 1. Download the two official Kaggle datasets (both on Google Dataset Search)
kaggle datasets download -d piterfm/paris-2024-olympic-summer-games -p /tmp/kaggle_paris --unzip
kaggle datasets download -d piterfm/tokyo-2020-olympics            -p /tmp/kaggle_tokyo --unzip

# 2. Transform them into data/ (athletes, medals, medallists, medal_countries[_tokyo], …)
python scripts/build_data_from_kaggle.py

# 3. The enriched athlete table is the data.gouv.fr file (kept as-is, no login needed):
curl -L -o data/paris2024_athletes_enriched.csv \
  'https://static.data.gouv.fr/resources/les-athletes-des-jeaux-olympiques-de-paris-2024/20250502-164217/paris2024-athletes.csv'
```

## References

- Kaggle "Paris 2024 Olympic Summer Games" (citable source, findable on Google Dataset Search): https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games
- data.gouv.fr "Les athlètes des Jeux Olympiques de Paris 2024" (findable on Google Dataset Search): https://www.data.gouv.fr/datasets/les-athletes-des-jeux-olympiques-de-paris-2024
- Google Dataset Search: https://datasetsearch.research.google.com (queries: "Paris 2024 Olympic Summer Games"; "Les athlètes des Jeux Olympiques de Paris 2024")
- Raw mirror used during development (not a cited source, not GDS-indexed): https://github.com/taniki/paris2024-data
