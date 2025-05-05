import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# --- Load env vars ---
load_dotenv()
SUPABASE_URL = f"https://{os.getenv('SUPABASE_HOST')}"
SUPABASE_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Load Data ---
@st.cache_data
def load_data():
    response = supabase.table('brokers').select("*").execute()
    df = pd.DataFrame(response.data)

    # ❌ Block all Cagnettas (case-insensitive)
    df = df[~df['broker_name'].str.lower().str.contains("cagnetta", na=False)]

    # ✅ Deduplicate by broker + company
    df = df.drop_duplicates(subset=['broker_name', 'company_name'])

    return df


df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("🎛️ Filters & Search")
region_filter = st.sidebar.selectbox("🌎 Region", options=["All"] + sorted(df['region'].dropna().unique()))
all_tags = sorted(set(tag for tags in df['expertise_tags'].dropna() if isinstance(tags, list) for tag in tags))
expertise_filter = st.sidebar.multiselect("🏷️ Expertise Tags", options=all_tags)
search_query = st.sidebar.text_input("🔍 Search Broker or Company")
sort_option = st.sidebar.selectbox("📊 Sort By", options=["Leaderboard Score", "Active Listings"])

# --- Apply Filters ---
filtered_df = df.copy()
if region_filter != "All":
    filtered_df = filtered_df[filtered_df['region'] == region_filter]
if expertise_filter:
    filtered_df = filtered_df[filtered_df['expertise_tags'].apply(
        lambda tags: isinstance(tags, list) and any(tag in tags for tag in expertise_filter)
    )]
if search_query:
    filtered_df = filtered_df[
        filtered_df['broker_name'].str.contains(search_query, case=False, na=False) |
        filtered_df['company_name'].str.contains(search_query, case=False, na=False)
    ]

# --- Sorting ---
if sort_option == "Leaderboard Score":
    filtered_df = filtered_df.sort_values(by='leaderboard_score', ascending=False)
elif sort_option == "Active Listings":
    filtered_df = filtered_df.sort_values(by='active_listings', ascending=False)

# ✅ Limit to Top 100
filtered_df = filtered_df.head(100)

# --- Display Leaderboard ---
st.title("🏆 Glengarry Top 100")
st.markdown(f"### Showing Top {len(filtered_df)} Brokers")

for idx, (_, row) in enumerate(filtered_df.iterrows(), start=1):
    # 🥇 Medal Icons
    if idx == 1:
        medal = "🥇"
    elif idx == 2:
        medal = "🥈"
    elif idx == 3:
        medal = "🥉"
    else:
        medal = f"{idx}."

    # ✅ Safe tag formatting
    tags = row.get('expertise_tags', [])
    if not isinstance(tags, list):
        tags = []
    tags_formatted = " ".join([f"<code>{tag}</code>" for tag in tags])

    # 🔗 Broker name with optional link
    url = row.get("companyUrl", "")
    name = row["broker_name"]
    if pd.notnull(url) and url.strip():
        broker_display = f'<b>{medal} <a href="{url}" target="_blank">{name}</a></b>'
    else:
        broker_display = f'<b>{medal} {name}</b>'

    # 💬 Render card
    st.markdown(f"""
<div style='padding:10px; border:1px solid #444; border-radius:6px; margin-bottom:12px; font-size:14px; line-height:1.5'>
{broker_display} <i>({row["region"]})</i> — <b>{row["leaderboard_score"]} pts</b><br>
<span style='color:#aaa;'>{tags_formatted}</span><br>
<strong>Active:</strong> {row["active_listings"]} &nbsp; | &nbsp;
<strong>Sold (6mo):</strong> {row["sold_last_6_months"]} &nbsp; | &nbsp;
<strong>Response:</strong> {row["response_score"]}%
</div>
""", unsafe_allow_html=True)
