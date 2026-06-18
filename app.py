"""Paris 2024 Olympic Data Story -- IT5425 storytelling dashboard.

Interaction model: this is a data-visualization story, not an ML tool, so there
is no sidebar. Navigation is inline tabs and every control lives in the page,
next to the chart it drives -- you interact with the data directly.

Design (informed by *The Big Book of Dashboards*, Wexler/Shaffer/Cotgreave):
  * Lead each view with animated headline KPI cards, not data tables.
  * Detail is on demand in tooltips; the page shows the data, never dumps it.
  * Colour is colourblind-safe (Okabe--Ito) and carries meaning only.
  * Dense, multi-column chart grids; every title states a takeaway.
The data/chart layers (``src/``) are unchanged; this is the presentation layer.
"""

from __future__ import annotations

import itertools
from pathlib import Path

import streamlit.components.v1 as components
import pandas as pd
import streamlit as st

from src.data_loader import check_data_availability, load_data
from src.data_processing import (
    apply_athlete_filters,
    apply_country_filter,
    apply_medal_filters,
    prepare_datasets,
    summarize_venues,
)
from src.utils import (
    ACCENT,
    MEDAL_COLORS,
    OKABE,
    country_label,
    format_number,
    format_percent,
    parse_country_codes,
)
from src import visualizations as viz

# Olympic rings logo (local SVG asset) inlined into the hero banner.
try:
    _RINGS_SVG = (Path(__file__).parent / "assets" / "olympic_rings.svg").read_text(encoding="utf-8")
except OSError:
    _RINGS_SVG = ""

st.set_page_config(
    page_title="Paris 2024 Olympic Data Story",
    page_icon="\U0001F3C5",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CHART_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d", "toggleSpikelines"],
    "responsive": True,
}


# ---------------------------------------------------------------------------
#  Design system (CSS)
# ---------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter','Segoe UI',Arial,sans-serif; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="collapsedControl"], [data-testid="stHeader"] { visibility: hidden; }
.stApp { background:
    radial-gradient(1200px 480px at 80% -8%, #EAF1F8 0%, rgba(234,241,248,0) 60%), #F4F6FA; }
.block-container { padding-top: 2.0rem; padding-bottom: 3rem; max-width: 1360px; }

/* ---- Hero ---- */
.hero { display:flex; align-items:center; gap:18px; padding: 16px 22px;
    background: linear-gradient(110deg,#10243B 0%,#163A5F 55%,#0E6E86 100%);
    border-radius: 16px; color:#fff; box-shadow: 0 12px 30px rgba(16,36,59,.22); margin-bottom: 10px; }
.hero-logo { background:#fff; border-radius:14px; padding:9px 13px; display:flex; align-items:center;
    box-shadow:0 4px 14px rgba(0,0,0,.20); flex:0 0 auto; }
.hero-logo svg { display:block; width:86px; height:auto; }
.hero-kicker { font-size:.72rem; letter-spacing:.22em; text-transform:uppercase; color:#9FD3E6; font-weight:600; }
.hero-title { font-size:1.6rem; font-weight:800; margin:1px 0 0; line-height:1.1; letter-spacing:-.01em; }
.hero-sub { margin:4px 0 0; color:#CFE0EC; font-size:.9rem; max-width: 80ch; }

/* ---- Tabs as primary nav ---- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #E2E8F0; }
.stTabs [data-baseweb="tab"] { height: 44px; padding: 0 16px; border-radius: 10px 10px 0 0;
    background: #FFFFFF; border: 1px solid #E7EBF1; border-bottom: none; color:#5B6675;
    font-weight: 600; font-size: .92rem; }
.stTabs [aria-selected="true"] { background: #0E6E86 !important; color:#fff !important;
    border-color:#0E6E86 !important; box-shadow:0 6px 14px rgba(14,110,134,.22); }

/* ---- Section header ---- */
.sec { margin: 12px 0 2px; }
.sec-kicker { font-size:.72rem; letter-spacing:.2em; text-transform:uppercase; color:#0E6E86; font-weight:700; }
.sec-title { font-size:1.38rem; font-weight:800; color:#10243B; margin:2px 0 2px; letter-spacing:-.01em; }
.sec-sub { color:#5B6675; font-size:.93rem; margin:0; max-width: 92ch; }
.sec-rule { height:3px; width:60px; border-radius:3px; margin-top:7px; background: linear-gradient(90deg,#E69F00,#0E6E86); }

/* ---- Inline control bar (toolbar) ---- */
[data-testid="stVerticalBlockBorderWrapper"]:has(.ctrlmark) {
    background:#FFFFFF; border:1px solid #E7EBF1 !important; border-radius:12px; }
.ctrl-label { font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; color:#0E6E86;
    font-weight:700; margin:-2px 0 2px; }

/* ---- Story note / spotlight ---- */
.note { background:#fff; border:1px solid #E7EBF1; border-left:4px solid #0E6E86; border-radius:10px;
    padding:10px 14px; margin: 6px 0 10px; color:#3C4757; font-size:.9rem; box-shadow:0 1px 2px rgba(16,36,59,.04); }
.note b { color:#10243B; }
.spotlight { background: linear-gradient(180deg,#FFF8EC,#FFFFFF); border:1px solid #F2E2BF;
    border-left:4px solid #E69F00; border-radius:10px; padding:10px 14px; color:#5b4a25; font-size:.9rem; margin:6px 0; }
.spotlight b { color:#8a6a12; }
.fine { color:#8A94A2; font-size:.82rem; }

/* ---- Podium ---- */
.podium { display:flex; align-items:flex-end; justify-content:center; gap:14px; margin: 8px 0 14px; }
.pod { width: 156px; border-radius:14px 14px 0 0; color:#10243B; text-align:center;
    display:flex; flex-direction:column; justify-content:flex-end; overflow:hidden;
    padding:12px 8px 14px; box-shadow: 0 8px 18px rgba(16,36,59,.10); border:1px solid rgba(0,0,0,.04); }
.pod .rank { font-size:.78rem; font-weight:700; opacity:.85; }
.pod .code { font-size:1.25rem; font-weight:800; margin:3px 0 1px; }
.pod .country { font-size:.72rem; color:#33485e; min-height:2.0em; line-height:1.05; margin-bottom:4px; }
.pod .tot { font-size:1.55rem; font-weight:800; line-height:1; }
.pod .brk { font-size:.72rem; color:#33485e; margin-top:2px; }

/* charts sit on white cards */
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #E7EBF1; border-radius:14px;
    padding:6px 8px 2px; box-shadow:0 1px 2px rgba(16,36,59,.04); }
[data-testid="stPlotlyChart"] > div { margin: 0 auto; }
</style>
""",
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-logo">{_RINGS_SVG}</div>
  <div>
    <div class="hero-kicker">Paris 2024 &middot; Olympic Data Story</div>
    <div class="hero-title">Beyond the medal table</div>
    <p class="hero-sub">Four chapters — the global field and where it played out, the medal
    race, sport specialization, and the athletes behind the numbers. Switch chapters with the
    tabs; every control sits next to the chart it drives.</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="sec"><div class="sec-kicker">{kicker}</div>'
        f'<div class="sec-title">{title}</div>'
        f'<p class="sec-sub">{subtitle}</p><div class="sec-rule"></div></div>',
        unsafe_allow_html=True,
    )


def animated_kpis(cards: list[dict], height: int = 126) -> None:
    """Animated count-up KPI cards rendered as one self-contained component.

    Each card is either numeric ({value, prefix, suffix, decimals}) -- which
    counts up on render -- or textual ({text}) for label-style headline values.
    """
    ncols = len(cards)
    divs = ""
    for c in cards:
        accent = c.get("accent", ACCENT)
        if "text" in c:
            inner = f'<div class="kv">{c["text"]}</div>'
        else:
            dec = int(c.get("decimals", 0))
            pre, suf = c.get("prefix", ""), c.get("suffix", "")
            init = "0" if dec == 0 else "0." + "0" * dec
            inner = (f'<div class="kv" data-target="{c["value"]}" data-prefix="{pre}" '
                     f'data-suffix="{suf}" data-decimals="{dec}">{pre}{init}{suf}</div>')
        divs += (f'<div class="card" style="border-top:3px solid {accent}">'
                 f'<div class="kvwrap" style="color:{accent}">{inner}</div>'
                 f'<div class="kl">{c["label"]}</div><div class="ks">{c.get("sub","")}</div></div>')

    html = f"""
<!DOCTYPE html><html><head><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter','Segoe UI',Arial,sans-serif;background:transparent;}}
.grid{{display:grid;grid-template-columns:repeat({ncols},1fr);gap:12px;padding:2px;}}
.card{{background:#fff;border:1px solid #E7EBF1;border-radius:14px;padding:13px 14px 12px;
  box-shadow:0 1px 2px rgba(16,36,59,.05);min-height:96px;transition:box-shadow .25s,transform .25s;}}
.card:hover{{box-shadow:0 8px 22px rgba(16,36,59,.10);transform:translateY(-2px);}}
.kvwrap .kv{{font-size:1.7rem;font-weight:800;letter-spacing:-.02em;line-height:1.05;
  font-variant-numeric:tabular-nums;color:#10243B;}}
.kvwrap{{color:#10243B;}}
.kl{{color:#64748B;font-size:.71rem;margin-top:5px;text-transform:uppercase;letter-spacing:.07em;font-weight:600;}}
.ks{{color:#7A8794;font-size:.78rem;margin-top:3px;}}
</style></head><body>
<div class="grid">{divs}</div>
<script>
document.querySelectorAll('.kv[data-target]').forEach(function(el){{
  var pre=el.getAttribute('data-prefix')||'',suf=el.getAttribute('data-suffix')||'',
      dec=parseInt(el.getAttribute('data-decimals')||'0'),tgt=parseFloat(el.getAttribute('data-target')),
      dur=820,t0=performance.now();
  function step(now){{var p=Math.min((now-t0)/dur,1),e=1-Math.pow(1-p,3),v=tgt*e;
    el.textContent=pre+(dec>0?v.toFixed(dec):Math.round(v).toLocaleString())+suf;
    if(p<1)requestAnimationFrame(step);}}
  requestAnimationFrame(step);
}});
</script></body></html>"""
    components.html(html, height=height, scrolling=False)


def note(html: str, kind: str = "note") -> None:
    st.markdown(f'<div class="{kind}">{html}</div>', unsafe_allow_html=True)


# Stable, unique key per chart. The script reruns top-to-bottom in a fixed
# order, so this also keeps keys stable across reruns. Without explicit keys,
# charts that collapse to identical empty placeholders collide on auto-IDs.
_CHART_SEQ = itertools.count()


def chart(fig) -> None:
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=f"chart_{next(_CHART_SEQ)}")


def control_bar():
    """A bordered inline toolbar container (replaces the sidebar)."""
    box = st.container(border=True)
    box.markdown('<span class="ctrlmark"></span>', unsafe_allow_html=True)
    return box


def podium(table: pd.DataFrame) -> None:
    top = table.sort_values(["gold", "total", "silver"], ascending=False).head(3)
    if len(top) < 3:
        return
    rows = list(top.itertuples())
    order = [(rows[1], 184, "#9AA6B2", "2"), (rows[0], 212, "#E3A81B", "1"), (rows[2], 166, "#B5713B", "3")]
    blocks = ""
    for r, h, color, rank in order:
        blocks += (
            f'<div class="pod" style="height:{h}px;background:linear-gradient(180deg,{color}2E,{color}14);'
            f'border-top:4px solid {color}">'
            f'<div class="rank">#{rank}</div><div class="code">{r.code}</div>'
            f'<div class="country">{r.country}</div><div class="tot">{int(r.total)}</div>'
            f'<div class="brk">{int(r.gold)}G &middot; {int(r.silver)}S &middot; {int(r.bronze)}B</div></div>'
        )
    st.markdown(f'<div class="podium">{blocks}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
#  Data
# ---------------------------------------------------------------------------
inject_css()

data_ready, missing_files = check_data_availability()
if not data_ready:
    st.error("Missing required data files: " + ", ".join(missing_files))
    st.stop()

frames = prepare_datasets(load_data())
countries = frames["country_stats"]
medals = frames["medals"]
enriched = frames["enriched_athletes"]
athletes = frames["athletes"]

COUNTRY_OPTIONS = [
    country_label(row)
    for _, row in countries.sort_values(["total", "athlete_count"], ascending=False).iterrows()
]
DISCIPLINE_OPTIONS = sorted(
    set(medals["discipline"].dropna().unique()).union(set(enriched["discipline"].dropna().unique()))
)
AGE_MIN, AGE_MAX = int(enriched["age"].min()), int(enriched["age"].max())

# Global facts
female_share = (athletes["gender"] == "Female").mean()
records_total = int(enriched["record_flag"].sum())

hero()
tab1, tab2, tab3, tab4 = st.tabs([
    "Opening Lens", "Medal Race", "Specialization", "Athlete Lens",
])


# ===========================================================================
#  TAB 1 -- Opening Lens
# ===========================================================================
with tab1:
    section_header(
        "Chapter 1 — the global field",
        "How big, and how spread out, was Paris 2024?",
        "Start with the whole field before narrowing in. The medal table is one slice; "
        "participation and geography set the scene.")

    with control_bar():
        cc1, cc2 = st.columns([1, 2])
        top_n1 = cc1.slider("Ranked items", 5, 30, 15, key="t1_topn")
        focus1 = cc2.multiselect("Trace nations (optional)", COUNTRY_OPTIONS, default=[],
                                 key="t1_focus", help="Leave empty to show every NOC.")
    codes1 = parse_country_codes(focus1)
    cview = apply_country_filter(countries, codes1, "code")

    medaling = int((cview["total"] > 0).sum())
    animated_kpis([
        {"label": "Athletes", "value": len(athletes), "accent": OKABE["blue"],
         "sub": f"{format_percent(female_share)} female"},
        {"label": "NOCs", "value": int(countries["code"].nunique()), "accent": OKABE["green"],
         "sub": f"{medaling} won a medal"},
        {"label": "Disciplines", "value": int(medals["discipline"].nunique()), "accent": OKABE["orange"],
         "sub": "normalized"},
        {"label": "Medal records", "value": len(medals), "accent": OKABE["purple"],
         "sub": "athlete–medal"},
        {"label": "Records set", "value": records_total, "accent": OKABE["vermillion"],
         "sub": "Olympic / world"},
    ])

    chart(viz.create_world_medal_map(cview))
    note("<b>Reading the map.</b> Colour intensity encodes total medals per NOC; the United "
         "States and China separate from the field before you read a single label.")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(viz.create_stacked_medal_bar(cview, top_n=top_n1, sort_by="total"))
        note("Bar <b>length</b> encodes medal count; medal <b>hue</b> stays consistent across "
             "every page.")
    with c2:
        chart(viz.create_athletes_vs_medals(cview))
        note("<b>Position</b> relates delegation size to medals; bubble <b>area</b> adds "
             "disciplines entered — a big team helps but does not guarantee medals.")

    chart(viz.create_venue_map(summarize_venues(enriched)))
    note("<b>Where it physically happened.</b> Each venue sits at its latitude/longitude; "
         "bubble <b>size</b> is athlete volume and <b>colour</b> medal activity — a dense Paris "
         "core reaching out to sailing in Marseille and surfing overseas.")


# ===========================================================================
#  TAB 2 -- Medal Race
# ===========================================================================
with tab2:
    section_header(
        "Chapter 2 — the leaders and the movers",
        "Who led Paris 2024, and who changed most since Tokyo?",
        "The ranking is familiar; the story is in the gold-vs-total split at the top, the "
        "swing against Tokyo 2020, and who was most efficient per athlete.")

    with control_bar():
        cc1, cc2, cc3 = st.columns([1.1, 1, 2])
        top_n2 = cc1.slider("Ranked items", 5, 30, 15, key="t2_topn")
        sort_by = cc2.segmented_control("Rank by", ["total", "gold", "silver", "bronze"],
                                        default="total", key="t2_sort") or "total"
        focus2 = cc3.multiselect("Trace nations (optional)", COUNTRY_OPTIONS, default=[], key="t2_focus")
    codes2 = parse_country_codes(focus2)
    cview = apply_country_filter(countries, codes2, "code")
    won = cview[cview["total"] > 0]

    ld = won.sort_values(["gold", "total"], ascending=False).head(1)
    gn = won.sort_values("total_delta", ascending=False).head(1)
    fl = won.sort_values("total_delta", ascending=True).head(1)
    top_gold = int(won["gold"].max()) if len(won) else 0
    gold_leaders = ", ".join(won[won["gold"] == top_gold]["code"].head(3)) if len(won) else "—"
    ld = ld.iloc[0] if len(ld) else None
    gn = gn.iloc[0] if len(gn) else None
    fl = fl.iloc[0] if len(fl) else None
    animated_kpis([
        {"label": "Most total medals", "text": (f"{ld.code} · {int(ld.total)}" if ld is not None else "—"),
         "accent": OKABE["blue"], "sub": (ld.country[:22] if ld is not None else "")},
        {"label": "Most golds", "value": top_gold, "accent": MEDAL_COLORS["Gold"], "sub": f"shared by {gold_leaders}"},
        {"label": "Biggest gain vs Tokyo", "text": (f"{gn.code} {int(gn.total_delta):+d}" if gn is not None else "—"),
         "accent": OKABE["green"], "sub": (f"{int(gn.tokyo_total)} → {int(gn.total)}" if gn is not None else "")},
        {"label": "Biggest drop vs Tokyo", "text": (f"{fl.code} {int(fl.total_delta):+d}" if fl is not None else "—"),
         "accent": OKABE["vermillion"], "sub": (f"{int(fl.tokyo_total)} → {int(fl.total)}" if fl is not None else "")},
    ], height=120)

    if len(won) >= 3:
        podium(won)
        st.markdown('<p class="fine" style="text-align:center">Podium ranks by golds, then total '
                    'medals — the Olympic tie-break order.</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(viz.create_stacked_medal_bar(cview, top_n=top_n2, sort_by=sort_by))
        note("Medal <b>composition</b> by NOC: bar length is the total, segments split "
             "gold/silver/bronze. Re-rank with the control above.")
    with c2:
        chart(viz.create_paris_tokyo_delta(cview, top_n=min(10, top_n2)))
        note("<b>Change vs Tokyo 2020.</b> A diverging bar around zero — gains to the right, "
             "losses to the left; direction is labelled so colour is never the only cue.")

    chart(viz.create_efficiency_bar(cview, top_n=min(12, top_n2)))
    note("<b>Efficiency, not just size.</b> Medals per 100 athletes rewards small, sharp "
         "delegations — a different leaderboard from the raw totals above.")

    host = countries[countries["code"] == "FRA"]
    if len(host):
        h = host.iloc[0]
        note(f"<b>Host-nation spotlight — France.</b> A home Games lifted France from "
             f"{int(h.tokyo_total)} medals in Tokyo to <b>{int(h.total)}</b> in Paris "
             f"(<b>{int(h.total_delta):+d}</b>), the largest swing of any NOC.", kind="spotlight")

    st.markdown('<div class="sec" style="margin-top:18px"><div class="sec-kicker">'
                'The race over time</div><div class="sec-title" style="font-size:1.1rem">'
                'When were the medals won?</div><div class="sec-rule"></div></div>',
                unsafe_allow_html=True)
    with control_bar():
        time_view = st.segmented_control(
            "Time view", ["Daily rhythm", "Cumulative race (animated)"],
            default="Daily rhythm", key="t2_timeview") or "Daily rhythm"
    if time_view == "Daily rhythm":
        chart(viz.create_daily_medal_chart(enriched))
        note("<b>Rhythm of the Games.</b> Athlete-medals decided on each athlete's final "
             "competition day. The tally builds slowly, then surges across the closing "
             "weekend (athletics and team finals). Counts are athlete-medals, not the "
             "official table.")
    else:
        chart(viz.create_medal_race_animation(enriched))
        note("<b>Press play.</b> Each discipline's bar grows with its cumulative medals as "
             "the Games progress — animation is used here because the variable is genuinely "
             "time-ordered.")


# ===========================================================================
#  TAB 3 -- Sport Specialization
# ===========================================================================
with tab3:
    section_header(
        "Chapter 3 — strengths, not totals",
        "Which nation owns which sport?",
        "Olympic power is uneven: a country can dominate one discipline and barely appear in "
        "another. Heatmaps and a flow graph expose that structure.")

    with control_bar():
        cc1, cc2, cc3 = st.columns([1, 2, 1.4])
        top_n3 = cc1.slider("Ranked items", 5, 30, 15, key="t3_topn")
        disc3 = cc2.multiselect("Focus disciplines (optional)", DISCIPLINE_OPTIONS, default=[], key="t3_disc")
        medal3 = cc3.segmented_control("Medal colours", ["Gold", "Silver", "Bronze"],
                                       selection_mode="multi", default=["Gold", "Silver", "Bronze"], key="t3_med")
    mview = apply_medal_filters(medals, selected_disciplines=disc3, selected_medals=list(medal3 or []))

    if not mview.empty:
        dcounts = mview["discipline"].value_counts()
        pair = mview.groupby(["code", "discipline"]).size().sort_values(ascending=False)
        pc, pd_, pv = (*pair.index[0], int(pair.iloc[0]))
        animated_kpis([
            {"label": "Disciplines in view", "value": int(mview["discipline"].nunique()), "accent": OKABE["orange"]},
            {"label": "NOCs in view", "value": int(mview["code"].nunique()), "accent": OKABE["green"]},
            {"label": "Most decorated sport", "text": dcounts.index[0], "accent": OKABE["blue"],
             "sub": f"{int(dcounts.iloc[0])} records"},
            {"label": "Strongest pairing", "text": f"{pc} · {pd_}", "accent": OKABE["purple"],
             "sub": f"{pv} records"},
        ], height=120)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(viz.create_discipline_medal_bar(mview, top_n=top_n3))
        note("<b>Medal records per discipline.</b> Bar length ranks the busiest sports. Unit: the "
             "athlete–medal record — each medalling athlete counts once, so a team gold adds "
             "several records (these run higher than the official country table).")
    with c2:
        chart(viz.create_country_discipline_heatmap(mview, top_countries=min(14, top_n3), top_disciplines=min(16, top_n3)))
        note("<b>How to read the heatmap.</b> Dark cells pop pre-attentively; the printed number "
             "gives the exact count where colour alone is imprecise.")

    chart(viz.create_medal_flow_sankey(mview, top_countries=min(8, top_n3), top_disciplines=min(9, top_n3)))
    note("<b>Who owns which sport.</b> A bipartite flow, NOC → discipline, ribbon width set by "
         "record volume; the widest ribbons are the strongest nation–sport pairings. (The "
         "medal-colour layer is deliberately left out — it carries no real information.)")
    chart(viz.create_medal_treemap(mview, top_disciplines=min(14, top_n3)))
    note("<b>Nested share.</b> Tile <b>area</b> is proportional to records, nested discipline → "
         "country; labels give exact counts to offset the lower accuracy of area judgements.")


# ===========================================================================
#  TAB 4 -- Athlete Lens
# ===========================================================================
with tab4:
    section_header(
        "Chapter 4 — the people behind the medals",
        "Who competes, and how does that vary by sport?",
        "Age, gender balance, and workload humanize the medal table. Every card and chart "
        "below responds live to these controls.")

    with control_bar():
        cc1, cc2, cc3, cc4 = st.columns([1, 1.1, 1.1, 2])
        top_n4 = cc1.slider("Ranked items", 5, 30, 15, key="t4_topn")
        gender4 = cc2.segmented_control("Gender", ["All", "Female", "Male"], default="All", key="t4_gender") or "All"
        status4 = cc3.segmented_control("Medal status", ["All", "Medalist", "No medal"], default="All", key="t4_status") or "All"
        disc4 = cc4.multiselect("Focus disciplines (optional)", DISCIPLINE_OPTIONS, default=[], key="t4_disc")
        age4 = st.slider("Age range", AGE_MIN, AGE_MAX, (AGE_MIN, AGE_MAX), key="t4_age")
    aview = apply_athlete_filters(enriched, selected_disciplines=disc4, gender=gender4,
                                  age_range=age4, medal_status=status4)

    n = len(aview)
    fem = (aview["gender"] == "Female").mean() if n else None
    animated_kpis([
        {"label": "Athletes in view", "value": n, "accent": OKABE["blue"], "sub": "after filters"},
        {"label": "Median age", "value": (float(aview["age"].median()) if n else 0), "decimals": 0,
         "accent": OKABE["orange"], "sub": "years"},
        {"label": "Female share", "value": (round(fem * 100, 1) if fem is not None else 0), "suffix": "%",
         "decimals": 1, "accent": OKABE["purple"]},
        {"label": "Medalists", "value": int((aview["medal_status"] == "Medalist").sum()), "accent": OKABE["green"]},
        {"label": "Records", "value": int(aview["record_flag"].sum()), "accent": OKABE["vermillion"]},
    ])

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart(viz.create_age_histogram(aview))
        note(f"<b>Age distribution by gender.</b> These views use the {format_number(len(enriched))} "
             f"athletes with enriched profiles ({format_percent(len(enriched) / len(athletes))} of "
             "the roster), so the count sits just below the Opening Lens headline.")
    with c2:
        chart(viz.create_gender_balance_by_discipline(aview, top_n=top_n4))
        note("<b>Gender balance by discipline.</b> A 100% stacked bar reads <b>share</b>, not raw "
             "counts — many sports sit near parity, a few remain skewed.")

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        chart(viz.create_age_boxplot_by_discipline(aview, top_n=top_n4))
        note("<b>Age spread by sport.</b> Medians run from the early-20s (skateboarding, "
             "gymnastics) to the late-30s (equestrian); whiskers show range, not sampling error.")
    with c4:
        chart(viz.create_competition_load_scatter(aview))
        note("<b>Workload relationship.</b> Events entered vs active days; bubble <b>area</b> is "
             "medals, <b>colour</b> is medal status. Detail on hover, never in a table.")

    chart(viz.create_record_bar(aview, top_n=top_n4))
    note("<b>Where records fell.</b> Olympic and world records by discipline — swimming and "
         "athletics lead the record book; the ranking responds to the filters above.")


# ---------------------------------------------------------------------------
#  Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    '<p class="fine">Sources: official Paris 2024 CSVs (Kaggle &ldquo;Paris 2024 Olympic Summer Games&rdquo;) '
    'and the data.gouv.fr enriched athlete table (ODbL), both findable via Google Dataset Search. '
    'Built with Streamlit + Plotly &middot; colourblind-safe Okabe–Ito palette &middot; '
    'interact with the charts directly.</p>',
    unsafe_allow_html=True,
)
