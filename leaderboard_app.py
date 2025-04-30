import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = f"https://{os.getenv('SUPABASE_HOST')}"
SUPABASE_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Load Data ---
@st.cache_data
def load_data():
    response = supabase.table('brokers').select("*").execute()
    df = pd.DataFrame(response.data)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("🎛️ Filters & Search")
region_filter = st.sidebar.selectbox("🌎 Region", options=["All"] + sorted(df['region'].unique()))
all_tags = sorted(set(tag for sublist in df['expertise_tags'] for tag in sublist))
expertise_filter = st.sidebar.multiselect("🏷️ Expertise Tags", options=all_tags)

search_query = st.sidebar.text_input("🔍 Search Broker or Company")

sort_option = st.sidebar.selectbox("📊 Sort By", options=["Leaderboard Score", "Active Listings"])

# --- Apply Filters ---
filtered_df = df.copy()
if region_filter != "All":
    filtered_df = filtered_df[filtered_df['region'] == region_filter]
if expertise_filter:
    filtered_df = filtered_df[filtered_df['expertise_tags'].apply(lambda tags: any(tag in tags for tag in expertise_filter))]
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

# --- Display Leaderboard ---
st.title("🏆 Glengarry Top 100")

for idx, row in enumerate(filtered_df.itertuples(), start=1):
    # Medal for Top 3
    if idx == 1:
        medal = "🥇"
    elif idx == 2:
        medal = "🥈"
    elif idx == 3:
        medal = "🥉"
    else:
        medal = f"{idx}."

    tags_formatted = " ".join([f"<code>{tag}</code>" for tag in row.expertise_tags])

    st.markdown(f"""
<div style='padding:10px; border:1px solid #444; border-radius:6px; margin-bottom:12px; font-size:14px; line-height:1.5'>
<b>{medal} {row.broker_name}</b> <i>({row.region})</i> — <b>{row.leaderboard_score} pts</b><br>
<span style='color:#aaa;'>{tags_formatted}</span><br>
<strong>Active:</strong> {row.active_listings} &nbsp; | &nbsp; <strong>Sold (6mo):</strong> {row.sold_last_6_months} &nbsp; | &nbsp; <strong>Response:</strong> {row.response_score}%
</div>
""", unsafe_allow_html=True)
