import os
import re
import hashlib
import sqlite3
import time
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from google_trends import get_trend_score

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Market Trend Predictor",
    page_icon="MT",
    layout="wide"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

.stApp{
    color:#0f172a;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,.14), transparent 30rem),
        radial-gradient(circle at top right, rgba(20,184,166,.12), transparent 26rem),
        linear-gradient(180deg,#f8fafc 0%,#eef4ff 48%,#f8fafc 100%);
}

.block-container{
    max-width:1160px;
    padding-top:2.4rem;
    padding-bottom:3rem;
    animation:fadeIn .55s ease both;
}

@keyframes fadeIn{
    from{opacity:0;transform:translateY(14px);}
    to{opacity:1;transform:translateY(0);}
}

@keyframes floatIn{
    from{opacity:0;transform:translateY(18px) scale(.98);}
    to{opacity:1;transform:translateY(0) scale(1);}
}

@keyframes gradientMove{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
}

.hero{
    min-height:430px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    border:1px solid rgba(148,163,184,.25);
    border-radius:28px;
    background:
        linear-gradient(135deg,rgba(255,255,255,.90),rgba(239,246,255,.78)),
        url("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1800&q=80");
    background-size:cover;
    background-position:center;
    background-blend-mode:screen;
    box-shadow:0 24px 70px rgba(15,23,42,.12);
    padding:4rem 2rem;
    overflow:hidden;
    position:relative;
}

.hero:after{
    content:"";
    position:absolute;
    inset:auto 9% 0 9%;
    height:5px;
    border-radius:999px;
    background:linear-gradient(90deg,#2563eb,#14b8a6,#7c3aed,#2563eb);
    background-size:260% 260%;
    animation:gradientMove 7s ease infinite;
}

.hero-title{
    margin:0;
    max-width:900px;
    font-size:clamp(2.8rem,7vw,5.6rem);
    line-height:.96;
    font-weight:800;
    text-align:center;
    letter-spacing:0;
    background:linear-gradient(110deg,#0f172a,#2563eb,#0f766e);
    background-size:240% 240%;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:gradientMove 8s ease infinite;
}

.hero-subtitle{
    max-width:690px;
    text-align:center;
    color:#334155;
    font-size:1.1rem;
    line-height:1.7;
    margin:1.25rem 0 0;
}

.feature-card,.report-panel{
    animation:floatIn .5s ease both;
}

.feature-card{
    min-height:150px;
    background:rgba(255,255,255,.82);
    border-radius:8px;
    padding:1.25rem;
    border:1px solid #dbe4ef;
    box-shadow:0 14px 32px rgba(15,23,42,.08);
    transition:transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.feature-card:hover{
    transform:translateY(-6px);
    box-shadow:0 20px 44px rgba(37,99,235,.14);
    border-color:rgba(37,99,235,.45);
}

.feature-card h3{
    margin:0 0 .55rem;
    font-size:1.05rem;
}

.feature-card p{
    margin:0;
    color:#64748b;
    line-height:1.55;
}

.section-title{
    font-size:clamp(2rem,4vw,3.2rem);
    font-weight:800;
    line-height:1;
    margin:.15rem 0 .4rem;
}

.section-subtitle{
    color:#64748b;
    margin-bottom:1.5rem;
}

.report-panel{
    border:1px solid #dbe4ef;
    border-radius:8px;
    background:rgba(255,255,255,.86);
    box-shadow:0 16px 38px rgba(15,23,42,.08);
    padding:1.3rem;
    margin-bottom:1rem;
}

.report-heading{
    margin:0 0 .25rem;
    font-size:1.1rem;
    font-weight:700;
}

.report-note{
    color:#64748b;
    margin:0;
}

.stButton > button,
.stDownloadButton > button{
    border:0;
    border-radius:8px;
    color:#fff;
    font-weight:700;
    background:linear-gradient(135deg,#2563eb,#14b8a6);
    box-shadow:0 10px 24px rgba(37,99,235,.24);
    transition:transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover{
    transform:translateY(-2px);
    filter:brightness(1.02);
    box-shadow:0 14px 32px rgba(37,99,235,.30);
}

.stTextInput input{
    border-radius:8px;
    border:1px solid #dbe4ef;
    min-height:3.25rem;
}

[data-testid="stMetric"]{
    border:1px solid #dbe4ef;
    border-radius:8px;
    background:rgba(255,255,255,.86);
    padding:1rem 1.1rem;
    box-shadow:0 12px 26px rgba(15,23,42,.06);
}

[data-testid="stMetricValue"]{
    color:#1d4ed8;
    font-weight:800;
}

.stProgress > div > div > div > div{
    background:linear-gradient(90deg,#2563eb,#14b8a6);
}

@media(max-width:760px){
    .hero{
        min-height:360px;
        padding:3rem 1.1rem;
        border-radius:18px;
    }
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "last_report" not in st.session_state:
    st.session_state.last_report = ""

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "last_trend_score" not in st.session_state:
    st.session_state.last_trend_score = 50

if "last_report_source" not in st.session_state:
    st.session_state.last_report_source = ""

if "last_analysis_time" not in st.session_state:
    st.session_state.last_analysis_time = 0.0

is_dark = st.session_state.theme == "Dark"
theme = {
    "app_bg": "#07111f" if is_dark else "#eef5ff",
    "surface": "rgba(15,23,42,.82)" if is_dark else "rgba(255,255,255,.94)",
    "surface_soft": "rgba(15,23,42,.58)" if is_dark else "rgba(248,250,252,.86)",
    "text": "#e5efff" if is_dark else "#0b1220",
    "muted": "#a7b6cc" if is_dark else "#475569",
    "line": "rgba(148,163,184,.26)" if is_dark else "rgba(37,99,235,.16)",
    "input": "#151a28" if is_dark else "#ffffff",
    "shadow": "rgba(0,0,0,.34)" if is_dark else "rgba(37,99,235,.14)",
    "app_glow_a": "rgba(37,99,235,.22)" if is_dark else "rgba(37,99,235,.18)",
    "app_glow_b": "rgba(20,184,166,.20)" if is_dark else "rgba(6,182,212,.16)",
    "app_glow_c": "rgba(124,58,237,.14)" if is_dark else "rgba(99,102,241,.10)",
    "hero_overlay": "rgba(37,99,235,.10)" if is_dark else "rgba(255,255,255,.72)",
    "hero_blue": "rgba(37,99,235,.42)" if is_dark else "rgba(37,99,235,.24)",
    "hero_teal": "rgba(20,184,166,.36)" if is_dark else "rgba(6,182,212,.22)",
    "grid": "rgba(148,163,184,.13)" if is_dark else "rgba(37,99,235,.12)",
    "title_gradient": "linear-gradient(110deg,#ffffff,#facc15,#38bdf8,#a78bfa,#ffffff)" if is_dark else "linear-gradient(110deg,#0f172a,#1d4ed8,#0891b2,#7c3aed,#0f172a)",
    "title_shadow": "rgba(15,23,42,.40)" if is_dark else "rgba(37,99,235,.18)",
    "title_filter": "rgba(0,0,0,.20)" if is_dark else "rgba(255,255,255,.48)",
}

st.markdown(f"""
<style>
[data-testid="stHeader"]{{
    background:transparent;
    height:0;
}}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer{{
    visibility:hidden;
    height:0;
}}

.stApp{{
    color:{theme["text"]};
    background:
        radial-gradient(circle at 12% 5%, {theme["app_glow_a"]}, transparent 26rem),
        radial-gradient(circle at 84% 16%, {theme["app_glow_b"]}, transparent 28rem),
        radial-gradient(circle at 50% 90%, {theme["app_glow_c"]}, transparent 30rem),
        linear-gradient(180deg,{theme["app_bg"]} 0%,{theme["app_bg"]} 100%);
}}

.block-container{{
    padding-top:1.05rem;
}}

.theme-label{{
    text-align:right;
    color:{theme["muted"]};
    font-weight:700;
    letter-spacing:.04em;
    text-transform:uppercase;
    font-size:.78rem;
    margin-top:.2rem;
}}

.hero{{
    border-color:{theme["line"]};
    background:
        linear-gradient(135deg,{theme["surface"]},{theme["hero_overlay"]}),
        radial-gradient(circle at 22% 28%, {theme["hero_blue"]}, transparent 18rem),
        radial-gradient(circle at 78% 22%, {theme["hero_teal"]}, transparent 17rem),
        linear-gradient(90deg, {theme["grid"]} 1px, transparent 1px),
        linear-gradient(0deg, {theme["grid"]} 1px, transparent 1px);
    background-size:auto, auto, auto, 56px 56px, 56px 56px;
    box-shadow:0 26px 80px {theme["shadow"]};
}}

.hero:before{{
    content:"";
    position:absolute;
    width:320px;
    height:320px;
    border:1px solid rgba(37,99,235,.25);
    border-radius:50%;
    background:
        radial-gradient(circle, rgba(20,184,166,.18), transparent 58%),
        conic-gradient(from 120deg, transparent, rgba(37,99,235,.55), transparent, rgba(20,184,166,.5), transparent);
    animation:spinGlow 14s linear infinite;
}}

@keyframes spinGlow{{
    from{{transform:rotate(0deg) scale(1);}}
    to{{transform:rotate(360deg) scale(1);}}
}}

.hero-title,
.hero-subtitle{{
    position:relative;
    z-index:1;
}}

.hero-title{{
    background:{theme["title_gradient"]};
    background-size:240% 240%;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    text-shadow:0 10px 34px {theme["title_shadow"]};
    filter:drop-shadow(0 2px 8px {theme["title_filter"]});
}}

.hero-subtitle,
.feature-card p,
.section-subtitle,
.report-note{{
    color:{theme["muted"]};
}}

.feature-card,
.report-panel,
[data-testid="stMetric"]{{
    color:{theme["text"]};
    background:{theme["surface"]};
    border-color:{theme["line"]};
}}

.stTextInput input{{
    color:{theme["text"]};
    background:{theme["input"]};
    border-color:{theme["line"]};
}}

.stTextInput input::placeholder{{
    color:{theme["muted"]};
}}

[data-testid="stMetricLabel"],
[data-testid="stMarkdownContainer"],
label,
p,
h1,
h2,
h3{{
    color:inherit;
}}

[data-testid="stMetric"]{{
    box-shadow:0 14px 34px {theme["shadow"]};
}}

.report-panel{{
    box-shadow:0 18px 42px {theme["shadow"]};
}}

.feature-card:hover{{
    box-shadow:0 22px 46px {theme["shadow"]};
}}

[role="radiogroup"] label{{
    color:{theme["text"]};
    font-weight:600;
}}

.stProgress > div > div > div > div{{
    background:linear-gradient(90deg,#2563eb,#06b6d4,#14b8a6);
}}
</style>
""", unsafe_allow_html=True)

# ==================================================
# ENV
# ==================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
        GROQ_MODEL = st.secrets.get("GROQ_MODEL", GROQ_MODEL)
    except Exception:
        GROQ_API_KEY = None

groq_client = OpenAI(
    api_key=GROQ_API_KEY or "missing-key",
    base_url="https://api.groq.com/openai/v1",
)

# ==================================================
# MODELS
# ==================================================

@st.cache_resource
def load_embedder():
    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

@st.cache_resource
def load_qdrant():
    return QdrantClient(
        path="vector_db"
    )

embedder = load_embedder()
client = load_qdrant()

# ==================================================
# HELPERS
# ==================================================

def market_interest(score):
    if score >= 70:
        return "High"
    if score >= 40:
        return "Moderate"
    return "Low"


def normalized_query(query):
    return re.sub(r"\s+", " ", query.strip().lower())


def cache_key(query):
    return hashlib.sha256(normalized_query(query).encode("utf-8")).hexdigest()


def init_cache():
    with sqlite3.connect("report_cache.db") as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                cache_key TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                trend_score INTEGER NOT NULL,
                report TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def get_cached_report(query):
    with sqlite3.connect("report_cache.db") as conn:
        row = conn.execute(
            """
            SELECT trend_score, report, source, created_at
            FROM reports
            WHERE cache_key = ?
            """,
            (cache_key(query),),
        ).fetchone()

    if not row:
        return None

    return {
        "trend_score": row[0],
        "report": row[1],
        "source": row[2],
        "created_at": row[3],
    }


def save_cached_report(query, trend_score, report, source):
    with sqlite3.connect("report_cache.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO reports
            (cache_key, query, trend_score, report, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                cache_key(query),
                normalized_query(query),
                trend_score,
                report,
                source,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def fallback_report(query, trend_score, context):
    interest = market_interest(trend_score)
    recommendation = "Test First"

    if trend_score >= 70:
        recommendation = "Launch"
    elif trend_score < 35:
        recommendation = "Avoid"

    evidence_note = "Relevant stored market data was found." if context else "No strong matching stored market data was found."

    return f"""## Demand Score
{trend_score}/100 - Search demand looks {interest.lower()}, so validate positioning before spending heavily.

## Key Insights
- Google Trends interest is currently {interest.lower()}.
- {evidence_note}
- Start with a small landing page, waitlist, or survey before building full inventory.

## Target Audience
- Early adopters already searching for this category.
- Buyers with a clear problem, budget, and repeat purchase potential.

## Risks
- Demand may be too broad or seasonal.
- Competitors may already own the strongest keywords.
- Free API quota was unavailable, so this is a rule-based fallback report.

## Launch Recommendation
{recommendation}
- Use a low-cost test campaign first.
- Re-run AI analysis later when model quota is available.
"""


def generate_groq_report(prompt):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to .env or Streamlit secrets.")

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a concise, practical market analyst.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.35,
        max_tokens=650,
    )

    return response.choices[0].message.content.strip()


init_cache()


def build_context(points):
    snippets = []

    for point in points[:5]:
        source = point.payload.get("source", "unknown")
        text = point.payload.get("text", "").strip()

        if text:
            snippets.append(f"SOURCE: {source}\nTEXT: {text[:850]}")

    return "\n\n---\n\n".join(snippets)


def report_filename(query):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", query.strip().lower()).strip("-")
    slug = slug or "market-trend"
    date = datetime.now().strftime("%Y%m%d")
    return f"{slug}-report-{date}.pdf"


def report_download_text(query, trend_score, report):
    created_at = datetime.now().strftime("%d %b %Y, %I:%M %p")

    return f"""# Market Trend Report

Product idea: {query}
Generated: {created_at}
Google Trends score: {trend_score}/100
Market interest: {market_interest(trend_score)}

{report}
"""


def plain_report_text(markdown_text):
    text = re.sub(r"^#+\s*", "", markdown_text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = text.replace("`", "")
    return text


def report_pdf_bytes(markdown_text):
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=16,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=8,
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Market Trend Report",
    )

    story = []
    lines = plain_report_text(markdown_text).splitlines()

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            story.append(Spacer(1, 0.08 * inch))
            continue

        if clean_line == "Market Trend Report":
            story.append(Paragraph(escape(clean_line), title_style))
        else:
            story.append(Paragraph(escape(clean_line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


_, theme_col = st.columns([5.5, 1.4])
with theme_col:
    st.markdown('<div class="theme-label">Theme</div>', unsafe_allow_html=True)
    st.radio(
        "Theme",
        ["Light", "Dark"],
        key="theme",
        horizontal=True,
        label_visibility="collapsed"
    )

# ==================================================
# HOME PAGE
# ==================================================

if st.session_state.page == "home":

    st.markdown("""
    <section class="hero">
        <h1 class="hero-title">Market Trend Predictor</h1>
        <p class="hero-subtitle">
        Validate product ideas with live search demand, retrieved consumer signals,
        and a concise AI launch recommendation.
        </p>
    </section>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>Google Trends</h3>
        <p>Measures demand momentum from recent search interest.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>Consumer Signals</h3>
        <p>Finds relevant market clues from your vector database.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>Short Report</h3>
        <p>Returns only the key decision points and a downloadable summary.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.7, 1, 1.7])

    with c2:

        if st.button(
            "Start Analysis",
            use_container_width=True
        ):
            st.session_state.page = "analyze"
            st.rerun()

# ==================================================
# ANALYSIS PAGE
# ==================================================

elif st.session_state.page == "analyze":

    col1, col2 = st.columns([1,8])

    with col1:

        if st.button("Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    with col2:

        st.markdown("""
        <div class="section-title">
        Product Analysis
        </div>
        <div class="section-subtitle">
        Enter one idea and get a focused market read in under a page.
        </div>
        """, unsafe_allow_html=True)

    query = st.text_input(
        "Product idea",
        placeholder="Example: AI study planner for college students",
        label_visibility="collapsed"
    )

    analyze = st.button(
        "Analyze Market",
        use_container_width=True
    )

    if analyze:

        clean_query = query.strip()

        if clean_query == "":
            st.warning(
                "Please enter a product idea."
            )

        else:
            st.session_state.last_query = clean_query
            cached = get_cached_report(clean_query)

            if cached:
                st.session_state.last_report = report_download_text(
                    clean_query,
                    cached["trend_score"],
                    cached["report"]
                )
                st.session_state.last_trend_score = cached["trend_score"]
                st.session_state.last_report_source = "Cache"
                st.success("Loaded from cache. No API call used.")

            elif time.time() - st.session_state.last_analysis_time < 10:
                st.warning("Please wait a few seconds before running another new analysis.")

            else:
                st.session_state.last_analysis_time = time.time()

                with st.status(
                    "Analyzing market data...",
                    expanded=True
                ) as status_box:

                    st.write("Fetching Google Trends score...")

                    trend_score = get_trend_score(
                        clean_query
                    )

                    st.write("Searching vector database...")

                    query_vector = embedder.encode(
                        clean_query
                    ).tolist()

                    results = client.query_points(
                        collection_name="market_data",
                        query=query_vector,
                        limit=5
                    )

                    context = build_context(results.points)

                    st.write("Writing concise Groq report...")

                    prompt = f"""
You are an expert market analyst. Write a compact, practical market report.

Rules:
- Keep the full report under 350 words.
- Use short bullet points, not long paragraphs.
- Do not repeat the retrieved data verbatim.
- Be specific and decision-oriented.

Product idea: {clean_query}
Google Trends score: {trend_score}/100

Retrieved market data:
{context}

Return exactly these sections:
## Demand Score
One line with score out of 100 and a 1-sentence reason.

## Key Insights
3 bullets only.

## Target Audience
2 bullets only.

## Risks
3 bullets only.

## Launch Recommendation
One clear recommendation: Launch, Test First, or Avoid. Add 2 bullets explaining why.
"""

                    try:
                        report = generate_groq_report(prompt)
                        report_source = "Groq"
                        save_cached_report(
                            clean_query,
                            trend_score,
                            report,
                            report_source
                        )
                        status_box.update(
                            label="Analysis complete",
                            state="complete"
                        )

                    except Exception as e:
                        report = fallback_report(
                            clean_query,
                            trend_score,
                            context
                        )
                        report_source = "Fallback"
                        st.write(f"Groq unavailable: {str(e)}")
                        status_box.update(
                            label="Fallback report generated",
                            state="complete"
                        )

                st.session_state.last_report = report_download_text(
                    clean_query,
                    trend_score,
                    report
                )
                st.session_state.last_trend_score = trend_score
                st.session_state.last_report_source = report_source

                st.success(
                    "Analysis complete"
                )

    if st.session_state.last_report:

        trend_score = st.session_state.last_trend_score
        interest = market_interest(trend_score)

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Trend Score",
                f"{trend_score}/100"
            )

        with col2:

            st.metric(
                "Market Interest",
                interest
            )

        with col3:

            st.metric(
                "Retrieved Docs",
                "5"
            )

        st.progress(
            trend_score / 100
        )

        st.markdown("<br>", unsafe_allow_html=True)

        left, right = st.columns([2, 1])

        with left:

            st.markdown("""
            <div class="report-panel">
            <p class="report-heading">Market Analysis Report</p>
            <p class="report-note">Short, decision-ready, and ready to download.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                st.session_state.last_report
            )

        with right:

            st.download_button(
                "Download PDF Report",
                data=report_pdf_bytes(st.session_state.last_report),
                file_name=report_filename(st.session_state.last_query),
                mime="application/pdf",
                use_container_width=True
            )
