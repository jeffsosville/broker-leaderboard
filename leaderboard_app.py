import streamlit as st
import pandas as pd
import ast
from supabase import create_client, Client

# --- Supabase Setup ---
SUPABASE_URL = "https://rxbaimgjakefhxsaksdl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ4YmFpbWdqYWtlZmh4c2Frc2RsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjYyNjQ0OSwiZXhwIjoyMDYyMjAyNDQ5fQ.aFgdVDkCCjYLX8b6y03Cz85SGiq2FYB8auF4hgLimUs"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Streamlit Setup ---
st.set_page_config(page_title="The Glengarry 100", layout="wide")
st.title("\U0001F3C6 The Glengarry 100")

# --- Utility: Fetch in Chunks ---
def fetch_all_brokers(table_name: str, total_rows: int = 7500, chunk_size: int = 1000):
    brokers = []
    for start in range(0, total_rows, chunk_size):
        end = start + chunk_size - 1
        response = supabase.table(table_name).select("*").range(start, end).execute()
        brokers.extend(response.data or [])
    return brokers

# --- Sidebar Filters (defined early to detect use) ---
st.sidebar.header("Search & Filter")
search_term = st.sidebar.text_input("Search all brokers (by name or company)")
city_filter = st.sidebar.multiselect("Filter by city", options=[])
state_filter = st.sidebar.multiselect("Filter by state", options=[])
industry_filter = st.sidebar.multiselect("Filter by industry/niche", options=[])

# --- Conditional Data Fetching ---
if search_term or city_filter or state_filter or industry_filter:
    data = fetch_all_brokers("all brokers", total_rows=7500)
else:
    data = supabase.table("all brokers").select("*").range(0, 99).execute().data

# --- DataFrame Setup ---
df = pd.DataFrame(data)
if df.empty:
    st.warning("No broker data found.")
    st.stop()

# --- Sort & Rank ---
df = df.sort_values(by='leaderboard_score', ascending=False, na_position='last').reset_index(drop=True)
df['rank'] = df.index + 1

# --- Parse expertise_tags field ---
if 'expertise_tags' in df.columns:
    df['expertise_tags'] = df['expertise_tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else [])
    all_tags = sorted(set(tag for sublist in df['expertise_tags'] for tag in sublist))
else:
    all_tags = []

# --- Update Filter Dropdowns with Data ---
city_filter = st.sidebar.multiselect("Filter by city", options=sorted(df['city'].dropna().unique()), default=city_filter)
state_filter = st.sidebar.multiselect("Filter by state", options=sorted(df['state'].dropna().str.upper().unique()), default=state_filter)
industry_filter = st.sidebar.multiselect("Filter by industry/niche", options=all_tags, default=industry_filter)

# --- Apply Filters ---
df_filtered = df.copy()

if search_term:
    df_filtered = df_filtered[df_filtered.apply(
        lambda row: search_term.lower() in str(row.get('broker_name', '')).lower() or
                    search_term.lower() in str(row.get('company_name', '')).lower(), axis=1)]

if city_filter:
    df_filtered = df_filtered[df_filtered['city'].isin(city_filter)]

if state_filter:
    df_filtered = df_filtered[df_filtered['state'].str.upper().isin(state_filter)]

if industry_filter:
    df_filtered = df_filtered[df_filtered['expertise_tags'].apply(lambda tags: any(tag in tags for tag in industry_filter))]

# --- Limit to Top 100 by Default ---
if not search_term and not city_filter and not state_filter and not industry_filter:
    df_filtered = df_filtered.head(100)

# --- Display Brokers ---
for i, row in df_filtered.iterrows():
    rank = row['rank']
    name = (row.get('company_name') or 'Unknown').title()
    broker = row.get('broker_name', '').title()
    location = f"{row.get('city', '').title()}, {row.get('state', '').upper()}"
    phone = row.get('phone', '')
    active = row.get('active_listings', 0)
    sold = row.get('sold_listings', 0)
    score = row.get('leaderboard_score', 0)
    url = row.get('listings_url') or row.get('companyurl') or row.get('companyUrl') or "#"

    medal = ""
    if rank == 1:
        medal = "🥇"
    elif rank == 2:
        medal = "🥈"
    elif rank == 3:
        medal = "🥉"

    st.markdown(f"""
    <div style='border:1px solid #333; padding:10px; border-radius:5px; margin-bottom:10px;'>
        <b>{medal} {rank}. <a href='{url}' target='_blank'>{name}</a></b> | {location} | {phone}<br>
        Active: {active} | Sold: {sold} | Score: {score} | <a href='{url}' target='_blank'>View Listings</a>
    </div>
    """, unsafe_allow_html=True)

if df_filtered.empty:
    st.info("No matching brokers found.")
