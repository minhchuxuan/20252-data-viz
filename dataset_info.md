# Dataset Information

## Selected Dataset

**Project dataset:** Paris 2024 Olympic Games public CSV collection.

This project uses two complementary public sources:

1. **paris2024-data GitHub repository**
   - URL: https://github.com/taniki/paris2024-data
   - Working files used: athletes, athlete disciplines, athlete events, medal records, medallists, Paris country medal table, Tokyo country medal table.
   - Source note from the repository: data are processed from the official Olympics website; when publishing, cite `source: Paris 2024, data processing: tam kien duong`.

2. **data.gouv.fr - Les athletes des Jeux Olympiques de Paris 2024**
   - URL: https://www.data.gouv.fr/datasets/les-athletes-des-jeux-olympiques-de-paris-2024
   - Working file used: enriched athlete CSV with age, discipline, venue, coordinates, competition dates, medal counts, and record flag.
   - License: Open Data Commons Open Database License (ODbL).
   - Last update shown by data.gouv.fr: May 2, 2025.

**Google Dataset Search requirement:** The Paris 2024 Olympic dataset topic is findable through Google Dataset Search. Use:

https://datasetsearch.research.google.com/search?query=Paris%202024%20Olympic%20Summer%20Games

The Kaggle result "Paris 2024 Olympic Summer Games" is visible in Google Dataset Search and documents a similar Paris 2024 Olympic CSV collection. The working project files are downloaded from public raw CSV sources to avoid Kaggle authentication during development.

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
| `data/athletes.csv` | 11,183 | Athlete bios, country codes, gender, birth date, height. |
| `data/athletes_disciplines.csv` | 11,225 | Athlete-to-discipline membership. |
| `data/athletes_events.csv` | 14,679 | Athlete-to-event membership. |
| `data/medals.csv` | 2,271 | Athlete-medal records by NOC, athlete, discipline, event, and medal color. |
| `data/medallists.csv` | 2,015 | Athlete-level medal totals. |
| `data/medal_countries.csv` | 91 | Paris 2024 country medal table. |
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

The required files are already included in `data/`. To refresh them manually on Windows PowerShell:

```powershell
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/athletes.csv' -OutFile 'data\athletes.csv'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/athletes_disciplines.csv' -OutFile 'data\athletes_disciplines.csv'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/athletes_events.csv' -OutFile 'data\athletes_events.csv'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/medals.csv' -OutFile 'data\medals.csv'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/medallists.csv' -OutFile 'data\medallists.csv'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/medal_countries.wide.auto.csv' -OutFile 'data\medal_countries.csv'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taniki/paris2024-data/main/datasets/medal_countries_tokyo.wide.csv' -OutFile 'data\medal_countries_tokyo.csv'
Invoke-WebRequest -Uri 'https://static.data.gouv.fr/resources/les-athletes-des-jeaux-olympiques-de-paris-2024/20250502-164217/paris2024-athletes.csv' -OutFile 'data\paris2024_athletes_enriched.csv'
```

## References

- Paris 2024 data repository: https://github.com/taniki/paris2024-data
- data.gouv.fr athlete dataset: https://www.data.gouv.fr/datasets/les-athletes-des-jeux-olympiques-de-paris-2024
- Kaggle Paris 2024 Olympic Summer Games dataset page: https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games
- Google Dataset Search query: https://datasetsearch.research.google.com/search?query=Paris%202024%20Olympic%20Summer%20Games
