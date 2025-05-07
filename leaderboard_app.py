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
    response = supabase.table('brokers_leaderboard').select("*").execute()
    df = pd.DataFrame(response.data)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("🎛️ Search & Sort")
search_query = st.sidebar.text_input("🔍 Search Broker or Company")
sort_option = st.sidebar.selectbox("📊 Sort By", options=["Leaderboard Score", "Active Listings"])

# --- Apply Filters ---
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['broker_name'].str.contains(search_query, case=False, na=False) |
        filtered_df['company_name'].str.contains(search_query, case=False, na=False)
    ]

# --- Sorting ---
if sort_option == "Leaderboard Score" and 'leaderboard_score' in filtered_df.columns:
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

    # ✅ Company name with link
    company_link = f'<a href="{row["companyurl"]}" target="_blank">{row["company_name"]}</a>' if pd.notnull(row["companyurl"]) and row["companyurl"].strip() else row["company_name"]

    # ✅ Listings link
    listings_link = f'(<a href="{row["listings_url"]}" target="_blank">listings</a>)' if pd.notnull(row["listings_url"]) and row["listings_url"].strip() else ""

    # ✅ Broker name
    broker_name = row["broker_name"]

    # ✅ Active listings
    active_listings = row["active_listings"]

    # --- Render card ---
    st.markdown(f"""
<div style='padding:10px; border:1px solid #444; border-radius:6px; margin-bottom:12px; font-size:14px; line-height:1.5'>
<b>{medal} {company_link} {listings_link}</b><br>
<strong>{broker_name}</strong><br>
Active Listings: <b>{active_listings}</b>
</div>
""", unsafe_allow_html=True)
