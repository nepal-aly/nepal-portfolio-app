import base64
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

base_dir = Path(__file__).parent
data_dir = base_dir / "data"
github = "https://github.com/nepal-aly"
linkedin = "https://www.linkedin.com/in/nepal-aly-data"
sentiment_app = "https://nepal-flight-sentiment.streamlit.app"

# ---------------- Colors ----------------
# Change these five colors to restyle the whole app
colors = {
    "DARK": "#162a2f",     # sidebar, hero start, titles
    "ACCENT": "#2fa58e",   # buttons, links, charts, hero end
    "TAGBG": "#dff3ee",    # tag background
    "TAGTEXT": "#1b6b5c",  # tag text
    "LIGHT": "#f4faf8",    # number boxes and notes background
}
navy = colors["DARK"]
blue = colors["ACCENT"]

st.set_page_config(page_title="Nepal Adel Ali | Data Engineer", layout="wide")

# ---------------- Style ----------------
css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stMarkdown, .stText, p, li, h1, h2, h3, h4 { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 3.5rem; max-width: 1150px; }
    section[data-testid="stSidebar"] { background: DARK; }
    section[data-testid="stSidebar"] * { color: #e6eef8 !important; }
    section[data-testid="stSidebar"] a { color: TAGBG !important; }
    section[data-testid="stSidebar"] [data-baseweb="select"] *, section[data-testid="stSidebar"] input { color: #0f172a !important; }
    section[data-testid="stSidebar"] [data-baseweb="tag"] * { color: #ffffff !important; }

    .hero { background: linear-gradient(135deg, DARK 0%, ACCENT 100%); border-radius: 18px;
            padding: 42px 44px; color: #ffffff; margin-bottom: 28px; }
    .hero-photo { display: flex; justify-content: space-between; align-items: flex-end; gap: 24px;
                  padding-bottom: 0; overflow: hidden; }
    .hero-photo .hero-text { padding-bottom: 42px; flex: 1; min-width: 0; }
    .hero-photo img { height: 340px; display: block; flex-shrink: 0; } @media (max-width: 1200px) { .hero-photo img { height: 260px; } }
    @media (max-width: 800px) { .hero-photo img { display: none; } .hero-photo .hero-text { padding-bottom: 0; } }
    .hero h1 { color: #ffffff; font-size: 2.6rem; font-weight: 800; margin: 0 0 6px 0; padding: 0; }
    .hero .role { font-size: 1.2rem; font-weight: 600; color: #cfe0f5; margin-bottom: 16px; }
    .hero p { color: #e6eef8; font-size: 1.02rem; line-height: 1.65; max-width: 760px; }
    .badge { display: inline-block; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.35);
             border-radius: 999px; padding: 5px 14px; font-size: 0.85rem; font-weight: 600; margin: 6px 0 18px 0; }
    .btn { display: inline-block; padding: 9px 20px; border-radius: 10px; font-weight: 600; font-size: 0.92rem;
           text-decoration: none !important; margin: 8px 10px 0 0; }
    .btn-light { background: #ffffff; color: DARK !important; }
    .btn-outline { border: 1px solid #ffffff; color: #ffffff !important; }

    .block-container a { color: ACCENT; }
    .section-title { font-size: 1.45rem; font-weight: 700; color: DARK; margin: 30px 0 4px 0; }
    .section-sub { color: #64748b; margin-bottom: 16px; }

    .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 22px 22px 18px 22px;
            height: 100%; box-shadow: 0 1px 3px rgba(15, 42, 74, 0.06); margin-bottom: 18px; }
    .card .label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; color: ACCENT; text-transform: uppercase; }
    .card h3 { font-size: 1.15rem; font-weight: 700; color: DARK; margin: 6px 0 8px 0; padding: 0; }
    .card p { color: #475569; font-size: 0.93rem; line-height: 1.6; margin-bottom: 10px; }
    .card a { color: ACCENT; font-weight: 600; text-decoration: none; margin-right: 14px; font-size: 0.9rem; }

    .pill { display: inline-block; background: TAGBG; color: TAGTEXT; border-radius: 999px; padding: 3px 11px;
            font-size: 0.78rem; font-weight: 600; margin: 0 6px 6px 0; }

    .stat { min-height: 118px; background: LIGHT; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 20px; margin-bottom: 14px; }
    .stat .value { font-size: 1.7rem; font-weight: 800; color: DARK; }
    .stat .name { font-size: 0.85rem; color: #64748b; }

    .note { background: LIGHT; border-left: 4px solid ACCENT; border-radius: 8px; padding: 14px 18px;
            color: #334155; font-size: 0.95rem; line-height: 1.6; margin: 10px 0 18px 0; }
    </style>
    """
for name, value in colors.items():
    css = css.replace(name, value)
st.markdown(css, unsafe_allow_html=True)


def paint(text):
    for name, value in colors.items():
        text = text.replace(name, value)
    return text


def pills(items):
    return "".join(f'<span class="pill">{item}</span>' for item in items)


def stat_box(value, name):
    return f'<div class="stat"><div class="value">{value}</div><div class="name">{name}</div></div>'


def section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def style_chart(fig):
    fig.update_layout(
        font_family="Inter",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=16,
        title_font_color=navy,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#eef2f7")
    return fig


@st.cache_data
def load_photo():
    data = (data_dir / "nepal_photo.webp").read_bytes()
    return base64.b64encode(data).decode()


@st.cache_data
def load_phones():
    return pd.read_csv(data_dir / "jumia_clean_2026-10-24.csv")


@st.cache_data
def load_beauty():
    con = sqlite3.connect(data_dir / "beauty_products.db")
    makeup = pd.read_sql("SELECT * FROM makeup_products", con)
    tags = pd.read_sql("SELECT * FROM makeup_tags", con)
    con.close()
    return makeup, tags


# ---------------- Sidebar ----------------
st.sidebar.markdown("## Nepal Adel Ali")
st.sidebar.markdown("Data Engineer")
page = st.sidebar.radio(
    "Pages",
    ["Home", "Smartphone Price Tracker", "Beauty Products Pipeline", "Python Games", "Contact"],
)
st.sidebar.markdown("---")
st.sidebar.markdown(f"[GitHub]({github})  \n[LinkedIn]({linkedin})  \n[Hugging Face](https://huggingface.co/NepalAdel)")


# ---------------- Home ----------------
if page == "Home":
    st.markdown(
        f"""
        <div class="hero hero-photo">
            <div class="hero-text">
                <h1>Nepal Adel Ali</h1>
                <div class="role">Data Engineer | Python, SQL, PySpark</div>
                <span class="badge">Open to entry-level Data Engineering roles and freelance work</span>
                <p>I build data pipelines that collect, clean and model data, then load it into databases and
                reports that people can use. I am currently in the DEPI program (Round 5, Microsoft Data Engineer track).</p>
                <a class="btn btn-light" href="{github}" target="_blank">GitHub</a>
                <a class="btn btn-outline" href="{linkedin}" target="_blank">LinkedIn</a>
            </div>
            <img src="data:image/webp;base64,{load_photo()}" alt="Nepal Adel Ali">
        </div>
        """,
        unsafe_allow_html=True,
    )

    phones = load_phones()
    makeup, tags = load_beauty()
    col_1, col_2, col_3, col_4 = st.columns(4)
    col_1.markdown(stat_box("1,848", "Smartphones scraped from Jumia"), unsafe_allow_html=True)
    col_2.markdown(stat_box(f"{len(phones):,}", "Smartphones after cleaning"), unsafe_allow_html=True)
    col_3.markdown(stat_box("7,856", "Beauty records loaded into SQLite"), unsafe_allow_html=True)
    col_4.markdown(stat_box("12", "Languages in my sentiment app"), unsafe_allow_html=True)

    section("Featured Projects", "Open a project from the menu on the left to explore it with its real data.")
    projects = [
        (
            "ETL · Web scraping",
            "Egypt Smartphone Price Tracker",
            "Scrapes 1,848 smartphones from Jumia Egypt, cleans prices, brands, storage and RAM, "
            "and keeps 1,829 clean phones ready for price tracking.",
            ["Python", "requests", "BeautifulSoup", "Pandas", "SQLite"],
            [("Repository", f"{github}/egypt-smartphone-price-tracker"), ("Dataset", "https://huggingface.co/datasets/NepalAdel/egypt-smartphone-prices-jumia")],
        ),
        (
            "ETL · APIs",
            "Beauty Products Pipeline",
            "Extracts makeup and perfume data from two public APIs, cleans 8,079 rows down to 7,856 "
            "and loads them into SQLite and Excel.",
            ["Python", "REST APIs", "Pandas", "SQL", "SQLite"],
            [("Repository", f"{github}/beauty-products-pipeline")],
        ),
        (
            "NLP · Web app",
            "Flight Review Sentiment",
            "A multilingual Hugging Face model that labels flight reviews in Arabic, English and more "
            "as positive, neutral or negative, one review or many at once.",
            ["Python", "Hugging Face", "Streamlit"],
            [("Live app", sentiment_app), ("Repository", f"{github}/hf-sentiment-app")],
        ),
    ]
    cols = st.columns(3)
    for i, (label, title, text, tools, links) in enumerate(projects):
        col = cols[i % 3]
        link_html = "".join(f'<a href="{url}" target="_blank">{name} &rarr;</a>' for name, url in links)
        col.markdown(
            f"""
            <div class="card">
                <div class="label">{label}</div>
                <h3>{title}</h3>
                <p>{text}</p>
                <div>{pills(tools)}</div>
                <div style="margin-top:8px">{link_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section("Skills")
    skills = [
        ("Languages", ["Python", "SQL"]),
        ("Data processing", ["Pandas", "PySpark", "Delta Lake"]),
        ("Data collection", ["Web scraping", "requests", "BeautifulSoup", "Selenium", "REST APIs"]),
        ("Databases", ["PostgreSQL", "SQLite", "MySQL"]),
        ("Data modeling", ["Star schema", "Medallion architecture", "Data quality checks"]),
        ("Reporting", ["Power BI", "Excel", "Streamlit"]),
        ("Workflow", ["Git", "GitHub", "Docker", "Jupyter Notebook", "pytest"]),
    ]
    col_1, col_2 = st.columns(2)
    for i, (area, items) in enumerate(skills):
        col = col_1 if i % 2 == 0 else col_2
        col.markdown(f"**{area}**<br>{pills(items)}", unsafe_allow_html=True)

    section("Education and Certificates")
    col_1, col_2 = st.columns(2)
    col_1.markdown(
        """
        <div class="card">
            <div class="label">Education</div>
            <h3>Bachelor of Commerce, Accounting</h3>
            <p>Faculty of Commerce, Damanhur University · Graduated 2026</p>
            <p>My accounting background helps me understand business data, reports and the numbers behind them.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_2.markdown(
        """
        <div class="card">
            <div class="label">Training and certificates</div>
            <h3>DEPI · Microsoft Data Engineer track</h3>
            <p>Digital Egypt Pioneers Initiative, Round 5 · Since June 2026 (in progress)</p>
            <p><b>Database Fundamentals</b> · ITI Mahara-Tech · September 2026<br>
            <b>AI for You</b> · Oracle · August 2026</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Smartphone Price Tracker ----------------
elif page == "Smartphone Price Tracker":
    st.title("Egypt Smartphone Price Tracker")
    st.write(
        "Smartphone listings scraped from Jumia Egypt on 2026-10-24 and cleaned with Pandas: "
        "text prices turned into numbers, non-phone products removed, brand names unified, "
        "and storage and RAM extracted from the product names."
    )
    st.markdown(f"[Repository]({github}/egypt-smartphone-price-tracker) · [Dataset on Hugging Face](https://huggingface.co/datasets/NepalAdel/egypt-smartphone-prices-jumia)")

    phones = load_phones()

    brands = sorted(phones["brand"].dropna().unique())
    top_brands = phones["brand"].value_counts().head(5).index.tolist()
    chosen_brands = st.sidebar.multiselect("Brand", brands, default=top_brands)
    storage_options = sorted(phones["storage_gb"].dropna().astype(int).unique())
    chosen_storage = st.sidebar.multiselect("Storage (GB)", storage_options)
    min_price = int(phones["price"].min())
    max_price = int(phones["price"].max())
    price_range = st.sidebar.slider("Price (EGP)", min_price, max_price, (min_price, max_price), step=500)
    hide_renewed = st.sidebar.checkbox("Hide renewed phones", value=False)

    df_1 = phones[phones["price"].between(price_range[0], price_range[1])]
    if chosen_brands:
        df_1 = df_1[df_1["brand"].isin(chosen_brands)]
    if chosen_storage:
        df_1 = df_1[df_1["storage_gb"].isin(chosen_storage)]
    if hide_renewed:
        df_1 = df_1[~df_1["is_renewed"].astype(bool)]

    if df_1.empty:
        st.warning("No phones match these filters. Try another brand or price range.")
    else:
        col_1, col_2, col_3, col_4 = st.columns(4)
        col_1.markdown(stat_box(f"{len(df_1):,}", "Phones"), unsafe_allow_html=True)
        col_2.markdown(stat_box(f"{df_1['price'].median():,.0f} EGP", "Median price"), unsafe_allow_html=True)
        col_3.markdown(stat_box(f"{df_1['discount'].mean():.0f}%", "Average discount"), unsafe_allow_html=True)
        col_4.markdown(stat_box(df_1["brand"].nunique(), "Brands"), unsafe_allow_html=True)

        brand_prices = (
            df_1.groupby("brand")["price"].median().sort_values(ascending=False).reset_index()
        )
        fig_1 = px.bar(brand_prices, x="brand", y="price", title="Median price by brand (EGP)")
        fig_1.update_traces(marker_color=blue)
        st.plotly_chart(style_chart(fig_1), width="stretch")

        storage_prices = df_1.dropna(subset=["storage_gb"]).copy()
        storage_prices["storage_gb"] = storage_prices["storage_gb"].astype(int).astype(str) + " GB"
        fig_2 = px.box(storage_prices, x="storage_gb", y="price", title="Price by storage size (EGP)",
                       category_orders={"storage_gb": [f"{s} GB" for s in storage_options]})
        fig_2.update_traces(marker_color=blue)
        st.plotly_chart(style_chart(fig_2), width="stretch")

        st.markdown("### Phones")
        table = df_1[["product_name", "brand", "storage_gb", "ram_gb", "price", "old_price",
                      "discount", "rating", "url"]].sort_values("price")
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={"url": st.column_config.LinkColumn("Link", display_text="Open")},
        )


# ---------------- Beauty Products Pipeline ----------------
elif page == "Beauty Products Pipeline":
    st.title("Beauty Products Data Pipeline")
    st.write(
        "Makeup data extracted from the Makeup API, cleaned with Pandas and loaded into SQLite. "
        "This page reads the same SQLite database the pipeline produces."
    )
    st.markdown(f"[Repository]({github}/beauty-products-pipeline)")

    makeup, tags = load_beauty()

    cleaning = pd.DataFrame(
        {
            "Table": ["makeup_products", "makeup_colors", "makeup_tags", "beauty_products", "Total"],
            "Rows before cleaning": [931, 5329, 419, 1400, 8079],
            "Rows after cleaning": [916, 5254, 378, 1308, 7856],
        }
    )
    st.dataframe(cleaning, hide_index=True, width="stretch")

    types = sorted(makeup["product_type"].dropna().unique())
    chosen_types = st.sidebar.multiselect("Product type", types)
    df_2 = makeup.copy()
    if chosen_types:
        df_2 = df_2[df_2["product_type"].isin(chosen_types)]

    top_brands = df_2["brand"].value_counts().head(10).reset_index()
    top_brands.columns = ["brand", "products"]
    fig_3 = px.bar(top_brands, x="products", y="brand", orientation="h",
                   title="Top 10 brands by number of products")
    fig_3.update_traces(marker_color=blue)
    fig_3.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_chart(fig_3), width="stretch")

    usd = df_2[df_2["currency"] == "USD"].dropna(subset=["price"])
    if not usd.empty:
        type_prices = usd.groupby("product_type")["price"].mean().sort_values(ascending=False).reset_index()
        fig_4 = px.bar(type_prices, x="product_type", y="price",
                       title="Average price by product type (USD prices only)")
        fig_4.update_traces(marker_color=blue)
        st.plotly_chart(style_chart(fig_4), width="stretch")

    df_3 = tags.merge(df_2[["product_id"]], on="product_id")
    tag_counts = df_3["tag"].value_counts().head(10).reset_index()
    tag_counts.columns = ["tag", "products"]
    if not tag_counts.empty:
        fig_5 = px.bar(tag_counts, x="tag", y="products", title="Most common product tags")
        fig_5.update_traces(marker_color=blue)
        st.plotly_chart(style_chart(fig_5), width="stretch")

    st.markdown("### Products")
    st.dataframe(
        df_2[["brand", "name", "product_type", "category", "price", "currency", "rating"]],
        hide_index=True,
        width="stretch",
    )


# ---------------- Python Games ----------------
elif page == "Python Games":
    st.title("Python Practice Projects")
    st.write("Object-oriented Python games built with Turtle graphics. They run on a desktop, so here are screenshots.")
    games = [
        ("Middle East Map Game", "middle-east-map-game", "A map quiz that reads country data from CSV with Pandas."),
        ("Snake Game", "snake-game-python", "Classic Snake with a saved high score."),
        ("Ping Pong", "ping-pong-python", "Two-player Ping Pong where the ball speeds up after each hit."),
        ("Shape Catcher", "shape-catcher-game", "Catch the falling shapes with a paddle to score."),
    ]
    col_1, col_2 = st.columns(2)
    for i, (title, repo, text) in enumerate(games):
        col = col_1 if i % 2 == 0 else col_2
        col.markdown(f"#### {title}")
        image_url = f"https://raw.githubusercontent.com/nepal-aly/{repo}/main/images/{repo}.png"
        col.image(image_url, width="stretch")
        col.write(text)
        col.markdown(f"[Repository]({github}/{repo})")


# ---------------- Contact ----------------
elif page == "Contact":
    st.markdown(
        f"""
        <div class="hero">
            <h1>Let's work together</h1>
            <span class="badge">Open to entry-level Data Engineering roles and freelance work</span>
            <p>I take freelance work in data cleaning, web scraping, ETL pipelines, Python, SQL and Excel reports.
            The fastest way to reach me is LinkedIn.</p>
            <a class="btn btn-light" href="{linkedin}" target="_blank">LinkedIn</a>
            <a class="btn btn-outline" href="{github}" target="_blank">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    platforms = [
        ("LinkedIn", "Professional profile", linkedin),
        ("GitHub", "All my code", github), ("Hugging Face", "Datasets", "https://huggingface.co/NepalAdel"),
        ("Upwork", "Freelance projects", "https://www.upwork.com/freelancers/~015bb0c3bd0f25915e"),
        ("Khamsat", "Freelance services", "https://khamsat.com/user/nepal_aly"),
        ("Mostaql", "Freelance projects", "https://mostaql.com/u/Nepal_Aly"),
        ("Nafezly", "Freelance projects", "https://nafezly.com/u/nepaladel"),
        ("Freelancer", "Freelance projects", "https://www.freelancer.com/u/nepalali"),
    ]
    cols = st.columns(4)
    for i, (name, text, url) in enumerate(platforms):
        cols[i % 4].markdown(
            f"""
            <div class="card">
                <h3>{name}</h3>
                <p>{text}</p>
                <a href="{url}" target="_blank">Open profile &rarr;</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("**Location:** Alexandria, Egypt  \n**Languages:** Arabic (native), English")
