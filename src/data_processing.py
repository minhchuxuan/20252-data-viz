"""Data cleaning and feature engineering for the Olympic dashboard."""

from __future__ import annotations

import pandas as pd


OPENING_DAY = pd.Timestamp("2024-07-26")
MEDAL_COLUMNS = ["gold", "silver", "bronze"]

MEDAL_LABELS = {
    "G": "Gold",
    "S": "Silver",
    "B": "Bronze",
}

# Plotly choropleth expects ISO-3 codes. Olympic/NOC codes differ for a few
# common countries, so we patch those cases explicitly.
ISO3_OVERRIDES = {
    "AIN": None,
    "EOR": None,
    "GER": "DEU",
    "NED": "NLD",
    "SUI": "CHE",
}

ENRICHED_COLUMNS = [
    "name",
    "source_url",
    "discipline",
    "birth_date_text",
    "country",
    "age",
    "role",
    "height_cm",
    "gender",
    "venue",
    "latitude",
    "longitude",
    "events_count",
    "start_date",
    "end_date",
    "competition_days",
    "gold",
    "silver",
    "bronze",
    "record",
]

DISCIPLINE_TRANSLATIONS = {
    "Athl\u00e9tisme": "Athletics",
    "Aviron": "Rowing",
    "Basketball 3x3": "3x3 Basketball",
    "Boxe": "Boxing",
    "Cano\u00eb-kayak slalom": "Canoe Slalom",
    "Cano\u00eb-kayak sprint": "Canoe Sprint",
    "Cyclisme BMX Freestyle": "Cycling BMX Freestyle",
    "Cyclisme BMX Racing": "Cycling BMX Racing",
    "Cyclisme Mountain Bike": "Cycling Mountain Bike",
    "Cyclisme sur piste": "Cycling Track",
    "Cyclisme sur route": "Cycling Road",
    "Escalade": "Sport Climbing",
    "Escrime": "Fencing",
    "Gymnastique artistique": "Artistic Gymnastics",
    "Gymnastique rythmique": "Rhythmic Gymnastics",
    "Halt\u00e9rophilie": "Weightlifting",
    "Lutte": "Wrestling",
    "Natation": "Swimming",
    "Natation artistique": "Artistic Swimming",
    "Natation, marathon": "Marathon Swimming",
    "Pentathlon moderne": "Modern Pentathlon",
    "Plongeon": "Diving",
    "Rugby \u00e0 sept": "Rugby Sevens",
    "Skateboard": "Skateboarding",
    "Sports \u00e9questres": "Equestrian",
    "Surf": "Surfing",
    "Tennis de table": "Table Tennis",
    "Tir": "Shooting",
    "Tir \u00e0 l'arc": "Archery",
    "Trampoline": "Trampoline Gymnastics",
    "Voile": "Sailing",
    "Volleyball de plage": "Beach Volleyball",
    "Water-polo": "Water Polo",
}


def prepare_datasets(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Clean all raw tables and return analysis-ready dataframes."""
    countries = _prepare_medal_countries(
        raw["medal_countries"],
        raw["medal_countries_tokyo"],
    )
    athletes = _prepare_athletes(raw["athletes"])
    athlete_discipline = _prepare_athlete_discipline(
        raw["athletes_disciplines"],
        athletes,
    )
    athlete_events = _prepare_athlete_events(raw["athletes_events"], athletes)
    medals = _prepare_medals(raw["medals"], countries)
    medallists = _prepare_medallists(raw["medallists"], countries)
    enriched = _prepare_enriched_athletes(raw["enriched_athletes"])
    country_stats = _prepare_country_stats(countries, athletes, athlete_discipline)

    return {
        "countries": countries,
        "country_stats": country_stats,
        "athletes": athletes,
        "athlete_discipline": athlete_discipline,
        "athlete_events": athlete_events,
        "medals": medals,
        "medallists": medallists,
        "enriched_athletes": enriched,
    }


def apply_country_filter(
    df: pd.DataFrame,
    selected_codes: list[str] | None,
    code_column: str = "code",
) -> pd.DataFrame:
    """Filter a dataframe by NOC/country code."""
    if not selected_codes:
        return df.copy()
    return df[df[code_column].isin(selected_codes)].copy()


def apply_medal_filters(
    medals: pd.DataFrame,
    selected_codes: list[str] | None = None,
    selected_disciplines: list[str] | None = None,
    selected_medals: list[str] | None = None,
) -> pd.DataFrame:
    """Filter medal records for medal-facing views."""
    filtered = medals.copy()
    if selected_codes:
        filtered = filtered[filtered["code"].isin(selected_codes)]
    if selected_disciplines:
        filtered = filtered[filtered["discipline"].isin(selected_disciplines)]
    if selected_medals:
        filtered = filtered[filtered["medal"].isin(selected_medals)]
    return filtered


def apply_athlete_filters(
    athletes: pd.DataFrame,
    selected_disciplines: list[str] | None = None,
    gender: str = "All",
    age_range: tuple[int, int] | None = None,
    medal_status: str = "All",
) -> pd.DataFrame:
    """Filter enriched athlete records for demographic and venue views."""
    filtered = athletes.copy()
    if selected_disciplines:
        filtered = filtered[filtered["discipline"].isin(selected_disciplines)]
    if gender != "All":
        filtered = filtered[filtered["gender"] == gender]
    if age_range:
        low, high = age_range
        filtered = filtered[(filtered["age"] >= low) & (filtered["age"] <= high)]
    if medal_status != "All":
        filtered = filtered[filtered["medal_status"] == medal_status]
    return filtered


def summarize_venues(enriched: pd.DataFrame) -> pd.DataFrame:
    """Aggregate enriched athlete data by venue for map and table views."""
    venue_df = enriched.dropna(subset=["latitude", "longitude"]).copy()
    if venue_df.empty:
        return pd.DataFrame(
            columns=[
                "venue",
                "latitude",
                "longitude",
                "athletes",
                "disciplines",
                "medal_total",
                "records",
            ]
        )

    summary = (
        venue_df.groupby(["venue", "latitude", "longitude"], as_index=False)
        .agg(
            athletes=("name", "count"),
            disciplines=("discipline", "nunique"),
            medal_total=("medal_total", "sum"),
            records=("record_flag", "sum"),
        )
        .sort_values(["athletes", "medal_total"], ascending=False)
    )
    return summary


def _prepare_medal_countries(
    paris: pd.DataFrame,
    tokyo: pd.DataFrame,
) -> pd.DataFrame:
    df = paris.copy()
    for col in MEDAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["total"] = df[MEDAL_COLUMNS].sum(axis=1)
    df["rank"] = range(1, len(df) + 1)
    df["iso_alpha"] = df["code"].map(lambda code: ISO3_OVERRIDES.get(code, code))

    tokyo_df = tokyo.copy()
    tokyo_df = tokyo_df.loc[:, ~tokyo_df.columns.str.startswith("Unnamed")]
    for col in MEDAL_COLUMNS:
        tokyo_df[col] = pd.to_numeric(tokyo_df[col], errors="coerce").fillna(0).astype(int)
    tokyo_df["tokyo_total"] = tokyo_df[MEDAL_COLUMNS].sum(axis=1)
    tokyo_df = tokyo_df.rename(
        columns={
            "gold": "tokyo_gold",
            "silver": "tokyo_silver",
            "bronze": "tokyo_bronze",
            "country": "tokyo_country",
        }
    )

    df = df.merge(
        tokyo_df[["code", "tokyo_gold", "tokyo_silver", "tokyo_bronze", "tokyo_total"]],
        on="code",
        how="left",
    )
    for col in ["tokyo_gold", "tokyo_silver", "tokyo_bronze", "tokyo_total"]:
        df[col] = df[col].fillna(0).astype(int)
    df["total_delta"] = df["total"] - df["tokyo_total"]
    df["gold_delta"] = df["gold"] - df["tokyo_gold"]
    return df


def _prepare_athletes(athletes: pd.DataFrame) -> pd.DataFrame:
    df = athletes.copy()
    df["birthDate"] = pd.to_datetime(df["birthDate"], errors="coerce")
    df["age"] = ((OPENING_DAY - df["birthDate"]).dt.days / 365.25).round(1)
    df["height"] = pd.to_numeric(df["height"], errors="coerce").replace(0, pd.NA)
    df["gender"] = df["gender"].map({"F": "Female", "M": "Male"}).fillna(df["gender"])
    return df


def _prepare_athlete_discipline(
    athlete_discipline: pd.DataFrame,
    athletes: pd.DataFrame,
) -> pd.DataFrame:
    df = athlete_discipline.copy()
    df = df.merge(
        athletes[
            [
                "code",
                "name",
                "country_code",
                "country_name",
                "country_name_long",
                "gender",
                "age",
                "height",
            ]
        ],
        on="code",
        how="left",
    )
    return df


def _prepare_athlete_events(
    athlete_events: pd.DataFrame,
    athletes: pd.DataFrame,
) -> pd.DataFrame:
    df = athlete_events.copy()
    df = df.merge(
        athletes[["code", "name", "country_code", "country_name", "gender", "age"]],
        on="code",
        how="left",
    )
    return df


def _prepare_medals(medals: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    df = medals.copy()
    df["medal"] = df["color"].map(MEDAL_LABELS).fillna(df["color"])
    df = df.merge(
        countries[["code", "country", "rank", "total"]],
        on="code",
        how="left",
        suffixes=("", "_country"),
    )
    df["country"] = df["country"].fillna(df["code"])
    return df


def _prepare_medallists(
    medallists: pd.DataFrame,
    countries: pd.DataFrame,
) -> pd.DataFrame:
    df = medallists.copy()
    for col in MEDAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["total"] = df[MEDAL_COLUMNS].sum(axis=1)
    df = df.merge(countries[["code", "country"]], on="code", how="left")
    df["country"] = df["country"].fillna(df["code"])
    return df


def _prepare_enriched_athletes(enriched: pd.DataFrame) -> pd.DataFrame:
    df = enriched.copy()
    if len(df.columns) >= len(ENRICHED_COLUMNS):
        df = df.iloc[:, : len(ENRICHED_COLUMNS)]
        df.columns = ENRICHED_COLUMNS

    df["discipline_source"] = df["discipline"]
    df["discipline"] = df["discipline"].replace(DISCIPLINE_TRANSLATIONS)

    for col in [
        "age",
        "height_cm",
        "latitude",
        "longitude",
        "events_count",
        "competition_days",
        "gold",
        "silver",
        "bronze",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["gender"] = df["gender"].map({"Femme": "Female", "Homme": "Male"}).fillna(df["gender"])
    df["start_date"] = pd.to_datetime(df["start_date"], format="%d/%m/%y", errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], format="%d/%m/%y", errors="coerce")
    df["medal_total"] = df[MEDAL_COLUMNS].sum(axis=1).fillna(0).astype(int)
    df["medal_status"] = df["medal_total"].map(lambda value: "Medalist" if value > 0 else "No medal")
    df["record_flag"] = df["record"].astype(str).str.lower().eq("oui")
    df["height_available"] = df["height_cm"].notna()
    return df


def _prepare_country_stats(
    countries: pd.DataFrame,
    athletes: pd.DataFrame,
    athlete_discipline: pd.DataFrame,
) -> pd.DataFrame:
    athlete_counts = (
        athletes.groupby(["country_code", "country_name_long"], as_index=False)
        .agg(
            athlete_count=("code", "nunique"),
            female_athletes=("gender", lambda values: (values == "Female").sum()),
            male_athletes=("gender", lambda values: (values == "Male").sum()),
        )
        .rename(columns={"country_code": "code", "country_name_long": "country_from_athletes"})
    )
    discipline_counts = (
        athlete_discipline.groupby("country_code", as_index=False)
        .agg(disciplines_entered=("disciplines", "nunique"))
        .rename(columns={"country_code": "code"})
    )

    df = athlete_counts.merge(countries, on="code", how="left")
    df = df.merge(discipline_counts, on="code", how="left")
    df["country"] = df["country"].fillna(df["country_from_athletes"])
    df["iso_alpha"] = df["code"].map(lambda code: ISO3_OVERRIDES.get(code, code))
    for col in MEDAL_COLUMNS + ["total", "tokyo_total", "total_delta", "gold_delta"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["rank"] = df["rank"].fillna(pd.NA)
    df["disciplines_entered"] = df["disciplines_entered"].fillna(0).astype(int)
    df["medals_per_100_athletes"] = (
        df["total"].div(df["athlete_count"]).mul(100).replace([pd.NA, pd.NaT], 0)
    )
    df["medal_tier"] = pd.cut(
        df["total"],
        bins=[-1, 0, 9, 29, 10_000],
        labels=["No medals", "1-9 medals", "10-29 medals", "30+ medals"],
    )
    return df
