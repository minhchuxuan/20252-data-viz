"""Plotly visualization builders for the Paris 2024 dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils import (
    GENDER_COLORS,
    MEDAL_COLORS,
    MEDAL_ORDER,
    NEG_COLOR,
    PALETTE,
    POS_COLOR,
    SCALE_BLUE,
    SCALE_INTENSITY,
    SCALE_RECORD,
    SCALE_VENUE,
    TIER_COLORS,
    style_plotly_chart,
)


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a ``#RRGGBB`` colour to an ``rgba(...)`` string with given alpha."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def empty_figure(title: str, message: str = "No data for the current filters."):
    """Create a styled placeholder figure for empty filtered states."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=15, color="#64748B"),
    )
    fig.update_layout(title=title, xaxis_visible=False, yaxis_visible=False)
    return style_plotly_chart(fig, height=360)


def create_world_medal_map(country_stats: pd.DataFrame):
    """World choropleth of Paris 2024 total medals by NOC."""
    df = country_stats.dropna(subset=["iso_alpha"]).copy()
    df = df[df["total"] > 0]
    if df.empty:
        return empty_figure("Global medal geography")

    fig = px.choropleth(
        df,
        locations="iso_alpha",
        color="total",
        hover_name="country",
        hover_data={
            "code": True,
            "athlete_count": ":,",
            "gold": ":.0f",
            "silver": ":.0f",
            "bronze": ":.0f",
            "total": ":.0f",
            "iso_alpha": False,
        },
        color_continuous_scale=SCALE_INTENSITY,
        title="Global medal distribution by National Olympic Committee",
        labels={"total": "Total medals"},
        projection="natural earth",
    )
    fig.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#CBD5E1")
    fig.update_layout(coloraxis_colorbar=dict(title="Medals"))
    return style_plotly_chart(fig, height=520)


def create_stacked_medal_bar(countries: pd.DataFrame, top_n: int = 15, sort_by: str = "total"):
    """Stacked medal-count bars for the leading countries."""
    df = countries[countries["total"] > 0].copy()
    if df.empty:
        return empty_figure("Medal composition")

    sort_by = sort_by if sort_by in ["gold", "silver", "bronze", "total"] else "total"
    df = df.sort_values([sort_by, "gold", "silver", "bronze"], ascending=False).head(top_n)
    df = df.sort_values(sort_by, ascending=True)

    fig = go.Figure()
    for medal in MEDAL_ORDER:
        col = medal.lower()
        fig.add_trace(
            go.Bar(
                name=medal,
                x=df[col],
                y=df["code"],
                orientation="h",
                marker_color=MEDAL_COLORS[medal],
                customdata=df[["country", "total"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    f"{medal}: %{{x:.0f}}<br>"
                    "Total: %{customdata[1]:.0f}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="stack",
        title=f"Medal composition for top {len(df)} NOCs",
        xaxis_title="Medals",
        yaxis_title="NOC",
    )
    return style_plotly_chart(fig, height=max(380, 24 * len(df) + 160))


def create_athletes_vs_medals(country_stats: pd.DataFrame):
    """Relationship between delegation size and medal output."""
    df = country_stats.copy()
    if df.empty:
        return empty_figure("Delegation size vs medal output")

    df["bubble_size"] = df["disciplines_entered"].clip(lower=1)
    fig = px.scatter(
        df,
        x="athlete_count",
        y="total",
        size="bubble_size",
        color="medal_tier",
        color_discrete_map=TIER_COLORS,
        hover_name="country",
        hover_data={
            "code": True,
            "athlete_count": ":,",
            "disciplines_entered": ":.0f",
            "gold": ":.0f",
            "silver": ":.0f",
            "bronze": ":.0f",
            "medals_per_100_athletes": ":.1f",
            "bubble_size": False,
        },
        title="Delegation size helps, but it does not explain everything",
        labels={
            "athlete_count": "Athletes in delegation",
            "total": "Total medals",
            "medal_tier": "Medal tier",
        },
        size_max=34,
    )
    return style_plotly_chart(fig, height=440)


def create_paris_tokyo_delta(countries: pd.DataFrame, top_n: int = 8):
    """Show largest country medal total changes from Tokyo to Paris."""
    df = countries[countries["total"] > 0].copy()
    if df.empty or "total_delta" not in df:
        return empty_figure("Paris vs Tokyo medal change")

    winners = df.nlargest(top_n, "total_delta")
    fallers = df.nsmallest(top_n, "total_delta")
    change = pd.concat([winners, fallers]).drop_duplicates("code")
    change = change.sort_values("total_delta", ascending=True)
    change["direction"] = change["total_delta"].map(lambda v: "Gained medals" if v >= 0 else "Lost medals")

    fig = px.bar(
        change,
        x="total_delta",
        y="code",
        orientation="h",
        color="direction",
        color_discrete_map={"Gained medals": POS_COLOR, "Lost medals": NEG_COLOR},
        hover_name="country",
        hover_data={"tokyo_total": ":.0f", "total": ":.0f", "total_delta": ":.0f", "direction": False},
        title="Who moved most between Tokyo 2020 and Paris 2024?",
        labels={"total_delta": "Change in total medals", "code": "NOC"},
    )
    fig.add_vline(x=0, line_width=1, line_color="#64748B")
    return style_plotly_chart(fig, height=max(380, 28 * len(change) + 140))


def create_discipline_medal_bar(medals: pd.DataFrame, top_n: int = 15):
    """Stacked discipline medal records by medal color."""
    if medals.empty:
        return empty_figure("Disciplines with the most athlete-medal records")

    counts = (
        medals.groupby(["discipline", "medal"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    top_disciplines = (
        counts.groupby("discipline")["count"].sum().nlargest(top_n).index.tolist()
    )
    counts = counts[counts["discipline"].isin(top_disciplines)]

    fig = px.bar(
        counts,
        x="count",
        y="discipline",
        color="medal",
        category_orders={"medal": MEDAL_ORDER},
        color_discrete_map=MEDAL_COLORS,
        orientation="h",
        title="Medal records cluster in team-heavy disciplines",
        labels={"count": "Athlete-medal records", "discipline": "Discipline"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, barmode="stack")
    return style_plotly_chart(fig, height=max(420, 25 * len(top_disciplines) + 160))


def create_country_discipline_heatmap(
    medals: pd.DataFrame,
    top_countries: int = 12,
    top_disciplines: int = 14,
):
    """Heatmap of medal records by country and discipline."""
    if medals.empty:
        return empty_figure("Country by discipline heatmap")

    top_codes = medals["code"].value_counts().head(top_countries).index
    top_sports = medals["discipline"].value_counts().head(top_disciplines).index
    pivot = (
        medals[medals["code"].isin(top_codes) & medals["discipline"].isin(top_sports)]
        .pivot_table(index="code", columns="discipline", values="name", aggfunc="count", fill_value=0)
        .loc[list(top_codes)]
    )
    if pivot.empty:
        return empty_figure("Country by discipline heatmap")

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=SCALE_BLUE,
        title="Specialization pattern: which NOCs win in which disciplines?",
        labels=dict(x="Discipline", y="NOC", color="Medal records"),
        text_auto=True,
    )
    fig.update_xaxes(side="bottom", tickangle=-35)
    return style_plotly_chart(fig, height=max(460, 26 * len(pivot) + 170))


def create_medal_treemap(medals: pd.DataFrame, top_disciplines: int = 12):
    """Treemap of medal records by discipline and country."""
    if medals.empty:
        return empty_figure("Medal hierarchy treemap")

    top_sports = medals["discipline"].value_counts().head(top_disciplines).index
    grouped = (
        medals[medals["discipline"].isin(top_sports)]
        .groupby(["discipline", "country"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    fig = px.treemap(
        grouped,
        path=["discipline", "country"],
        values="count",
        color="count",
        color_continuous_scale=SCALE_BLUE,
        title="Medal records as a hierarchy: discipline to country",
        labels={"count": "Records"},
    )
    # Tile area encodes record count; colour now reinforces magnitude (darker =
    # more records) instead of merely repeating the discipline grouping.
    fig.update_traces(textinfo="label+value")
    fig.update_layout(coloraxis_colorbar=dict(title="Records"))
    return style_plotly_chart(fig, height=520)


def create_medal_flow_sankey(medals: pd.DataFrame, top_countries: int = 7, top_disciplines: int = 8):
    """Bipartite flow graph from NOC to discipline (athlete-medal records).

    The medal-colour layer is intentionally omitted: each event awards a near-fixed
    gold/silver/bronze ratio, so a discipline -> colour layer carries almost no
    information and only clutters the view. The insight -- which nation dominates
    which sport -- lives entirely in the NOC -> discipline flow.
    """
    if medals.empty:
        return empty_figure("NOC to discipline flow")

    top_codes = medals["code"].value_counts().head(top_countries).index.tolist()
    top_sports = medals["discipline"].value_counts().head(top_disciplines).index.tolist()
    df = medals[medals["code"].isin(top_codes) & medals["discipline"].isin(top_sports)].copy()
    if df.empty:
        return empty_figure("NOC to discipline flow")

    country_nodes = top_codes
    sport_nodes = top_sports
    labels = country_nodes + sport_nodes
    node_index = {label: idx for idx, label in enumerate(labels)}

    country_sport = (
        df.groupby(["code", "discipline"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    # One colour per source country so a nation's ribbons can be traced to the
    # disciplines where its medals come from.
    country_color = {code: PALETTE[i % len(PALETTE)] for i, code in enumerate(country_nodes)}

    sources = []
    targets = []
    values = []
    link_colors = []
    for _, row in country_sport.iterrows():
        sources.append(node_index[row["code"]])
        targets.append(node_index[row["discipline"]])
        values.append(row["count"])
        link_colors.append(_hex_to_rgba(country_color[row["code"]], 0.40))

    node_colors = [country_color[code] for code in country_nodes] + ["#9AA7B4"] * len(sport_nodes)
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(label=labels, pad=18, thickness=15, color=node_colors),
                link=dict(source=sources, target=targets, value=values, color=link_colors),
            )
        ]
    )
    fig.update_layout(title="NOC to discipline: where each nation's medals come from")
    return style_plotly_chart(fig, height=560)


def create_age_histogram(athletes: pd.DataFrame):
    """Age distribution by gender."""
    df = athletes.dropna(subset=["age"])
    if df.empty:
        return empty_figure("Age distribution")

    fig = px.histogram(
        df,
        x="age",
        color="gender",
        nbins=35,
        barmode="overlay",
        category_orders={"gender": ["Male", "Female"]},
        color_discrete_map=GENDER_COLORS,
        title="Athlete age distribution: prime years and long tails",
        labels={"age": "Age", "count": "Athletes"},
    )
    # Male (blue) is drawn first, Female (gold) over it -- both as translucent
    # fills with a solid same-colour outline. Gold over blue blends to a readable
    # green in the overlap (not a muddy grey), and each gender's silhouette stays
    # legible via its outline. Trace opacity stays 1 so outlines read crisply --
    # the transparency lives in the rgba fill, not the whole trace.
    for tr in fig.data:
        base = GENDER_COLORS.get(tr.name, "#888888")
        tr.marker.color = _hex_to_rgba(base, 0.50)
        tr.marker.line.color = base
        tr.marker.line.width = 1.2
    fig.update_layout(bargap=0.06)
    return style_plotly_chart(fig, height=420)


def create_age_boxplot_by_discipline(athletes: pd.DataFrame, top_n: int = 15):
    """Box plots for age by discipline."""
    df = athletes.dropna(subset=["age", "discipline"]).copy()
    if df.empty:
        return empty_figure("Age by discipline")

    top = df["discipline"].value_counts().head(top_n).index
    df = df[df["discipline"].isin(top)]
    fig = px.box(
        df,
        x="age",
        y="discipline",
        color="discipline",
        color_discrete_sequence=PALETTE,
        points="outliers",
        title="Age profiles differ sharply by discipline",
        labels={"age": "Age", "discipline": "Discipline"},
    )
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
    return style_plotly_chart(fig, height=max(430, 25 * len(top) + 170))


def create_gender_balance_by_discipline(athletes: pd.DataFrame, top_n: int = 15):
    """100 percent stacked bar for gender balance in major disciplines."""
    df = athletes.dropna(subset=["gender", "discipline"]).copy()
    if df.empty:
        return empty_figure("Gender balance by discipline")

    top = df["discipline"].value_counts().head(top_n).index
    grouped = (
        df[df["discipline"].isin(top)]
        .groupby(["discipline", "gender"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    totals = grouped.groupby("discipline")["count"].transform("sum")
    grouped["share"] = grouped["count"] / totals * 100

    fig = px.bar(
        grouped,
        x="share",
        y="discipline",
        color="gender",
        color_discrete_map=GENDER_COLORS,
        orientation="h",
        title="Gender balance by discipline",
        labels={"share": "Share of athletes (%)", "discipline": "Discipline"},
        hover_data={"count": True, "share": ":.1f", "gender": True},
    )
    fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
    return style_plotly_chart(fig, height=max(430, 25 * len(top) + 170))


def create_competition_load_scatter(athletes: pd.DataFrame):
    """Aggregated athlete workload: one bubble per (events, days) cell.

    Events entered and competition days are both discrete, so an individual
    scatter overplots badly (every athlete lands on the same grid points). We
    aggregate athletes into workload cells instead: bubble area is the number of
    athletes in the cell and colour is that cell's medalist rate.
    """
    df = athletes.dropna(subset=["events_count", "competition_days"]).copy()
    if df.empty:
        return empty_figure("Competition load and medals")

    cells = (
        df.groupby(["events_count", "competition_days"], as_index=False)
        .agg(
            athletes=("name", "count"),
            medalists=("medal_status", lambda s: (s == "Medalist").sum()),
            medals=("medal_total", "sum"),
        )
    )
    cells["medalist_rate"] = (cells["medalists"] / cells["athletes"] * 100).round(1)

    fig = px.scatter(
        cells,
        x="events_count",
        y="competition_days",
        size="athletes",
        color="medalist_rate",
        color_continuous_scale="Tealgrn",
        hover_data={
            "events_count": True,
            "competition_days": True,
            "athletes": ":,",
            "medalists": ":,",
            "medalist_rate": ":.1f",
            "medals": ":,",
        },
        title="Competition load: athlete density and medalist rate by workload",
        labels={
            "events_count": "Events entered",
            "competition_days": "Competition days",
            "athletes": "Athletes in cell",
            "medalists": "Medalists",
            "medalist_rate": "Medalist rate (%)",
            "medals": "Medals",
        },
        size_max=46,
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Medalist<br>rate (%)"))
    return style_plotly_chart(fig, height=460)


def create_venue_map(venue_summary: pd.DataFrame):
    """Map Paris 2024 venues by athlete count and medal/record activity."""
    df = venue_summary.dropna(subset=["latitude", "longitude"]).copy()
    if df.empty:
        return empty_figure("Paris venue geography")

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="athletes",
        color="medal_total",
        color_continuous_scale=SCALE_VENUE,
        hover_name="venue",
        hover_data={
            "athletes": ":,",
            "disciplines": ":.0f",
            "medal_total": ":.0f",
            "records": ":.0f",
            "latitude": False,
            "longitude": False,
        },
        zoom=4.2,
        center={"lat": 46.9, "lon": 2.4},
        title="Venue geography: where athletes competed across France",
        labels={"medal_total": "Athlete medals"},
    )
    fig.update_layout(mapbox_style="carto-positron")
    return style_plotly_chart(fig, height=560)


def create_record_bar(athletes: pd.DataFrame, top_n: int = 12):
    """Records by discipline."""
    df = athletes[athletes["record_flag"]].copy()
    if df.empty:
        return empty_figure("Record-setting disciplines")

    grouped = (
        df.groupby("discipline", as_index=False)
        .size()
        .rename(columns={"size": "records"})
        .sort_values("records", ascending=False)
        .head(top_n)
        .sort_values("records", ascending=True)
    )
    fig = px.bar(
        grouped,
        x="records",
        y="discipline",
        orientation="h",
        color="records",
        color_continuous_scale=SCALE_RECORD,
        title="Where records were set",
        labels={"records": "Record-setting athletes", "discipline": "Discipline"},
    )
    return style_plotly_chart(fig, height=max(360, 25 * len(grouped) + 150))


def create_efficiency_bar(country_stats: pd.DataFrame, top_n: int = 12, min_athletes: int = 30):
    """Medal efficiency: medals per 100 athletes among sizeable delegations.

    A counterpoint to raw totals — it surfaces nations that punch above their
    delegation size, the analytical pay-off of the size-vs-medals scatter.
    """
    df = country_stats[
        (country_stats["total"] > 0) & (country_stats["athlete_count"] >= min_athletes)
    ].copy()
    if df.empty:
        return empty_figure("Medal efficiency")

    df = (
        df.sort_values("medals_per_100_athletes", ascending=False)
        .head(top_n)
        .sort_values("medals_per_100_athletes", ascending=True)
    )
    fig = px.bar(
        df,
        x="medals_per_100_athletes",
        y="code",
        orientation="h",
        color="medals_per_100_athletes",
        color_continuous_scale="Tealgrn",
        hover_name="country",
        hover_data={"athlete_count": ":,", "total": ":.0f", "medals_per_100_athletes": ":.1f"},
        title=f"Punching above their weight: medals per 100 athletes (≥{min_athletes} athletes)",
        labels={"medals_per_100_athletes": "Medals per 100 athletes", "code": "NOC"},
    )
    fig.update_layout(coloraxis_showscale=False)
    return style_plotly_chart(fig, height=max(360, 26 * len(df) + 150))


def create_daily_medal_chart(athletes: pd.DataFrame):
    """Daily medal rhythm: athlete-medals awarded per Games day, by colour.

    A medal is decided on an athlete's final competition day, so we aggregate the
    per-athlete gold/silver/bronze counts by ``end_date`` to read the rhythm of
    the Games -- the trend/change-over-time view the medal race otherwise lacks.
    """
    df = athletes[athletes["medal_total"] > 0].dropna(subset=["end_date"]).copy()
    if df.empty:
        return empty_figure("The medal race, day by day")

    df["day"] = df["end_date"].dt.normalize()
    daily = df.groupby("day")[["gold", "silver", "bronze"]].sum().reset_index()
    long = daily.melt(id_vars="day", value_vars=["gold", "silver", "bronze"],
                      var_name="medal", value_name="count")
    long["medal"] = long["medal"].str.capitalize()

    fig = px.bar(
        long,
        x="day",
        y="count",
        color="medal",
        category_orders={"medal": MEDAL_ORDER},
        color_discrete_map=MEDAL_COLORS,
        title="The medal race, day by day: the final weekend delivered the most",
        labels={"day": "Medal-decision day", "count": "Athlete-medals awarded", "medal": "Medal"},
    )
    fig.update_layout(barmode="stack", bargap=0.18)
    fig.update_xaxes(dtick="D2", tickformat="%b %d")
    return style_plotly_chart(fig, height=440)


def create_medal_race_animation(athletes: pd.DataFrame, top_n: int = 10):
    """Animated bar-chart race: cumulative athlete-medals by discipline over days.

    ``animation_frame`` steps through the Games day by day; each discipline's bar
    grows with its cumulative medal haul. This is the dashboard's one use of
    animation (course Chapter 8.4): motion is meaningful here because the variable
    is genuinely time-ordered.
    """
    df = athletes[athletes["medal_total"] > 0].dropna(subset=["end_date", "discipline"]).copy()
    if df.empty:
        return empty_figure("Cumulative medal race")

    df["day"] = df["end_date"].dt.normalize()
    top = df.groupby("discipline")["medal_total"].sum().nlargest(top_n).index.tolist()
    df = df[df["discipline"].isin(top)]
    days = sorted(df["day"].unique())

    # Cumulative medals per (day, discipline), carried forward across every day.
    per = (
        df.groupby(["day", "discipline"])["medal_total"].sum()
        .unstack(fill_value=0)
        .reindex(columns=top, fill_value=0)
        .reindex(days, fill_value=0)
        .cumsum()
    )
    rows = []
    for day in days:
        label = pd.Timestamp(day).strftime("%b %d")
        for disc in top:
            rows.append({"day": label, "discipline": disc, "cum": int(per.loc[day, disc])})
    frame_df = pd.DataFrame(rows)
    x_max = int(per.to_numpy().max()) * 1.12 if per.size else 1

    fig = px.bar(
        frame_df,
        x="cum",
        y="discipline",
        color="discipline",
        animation_frame="day",
        orientation="h",
        color_discrete_sequence=PALETTE,
        range_x=[0, x_max],
        title="Cumulative medal race by discipline — press play",
        labels={"cum": "Cumulative athlete-medals", "discipline": "Discipline", "day": "Day"},
    )
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
    # Smooth, brisk playback.
    if fig.layout.updatemenus:
        btn = fig.layout.updatemenus[0].buttons[0]
        btn.args[1]["frame"]["duration"] = 650
        btn.args[1]["transition"]["duration"] = 300
    return style_plotly_chart(fig, height=480)
