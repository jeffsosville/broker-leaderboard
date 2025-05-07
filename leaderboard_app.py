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

# --- Sort leaderboard ---
if 'leaderboard_score' in df.columns:
    df = df.sort_values(by='leaderboard_score', ascending=False)
else:
    df = df.sort_values(by='active_listings', ascending=False)

df = df.head(100)

# --- Set Streamlit page config ---
st.set_page_config(page_title="The Glengarry 100", layout="wide")

# --- Custom CSS for Hacker News style ---
st.markdown("""
    <style>
    body {
        background-color: #fff;
        color: #222;
        font-family: system-ui, sans-serif;
    }
    .rank {
        color: orange;
        font-weight: bold;
        margin-right: 6px;
    }
    .leaderboard-item {
        padding: 8px 0;
        border-bottom: 1px solid #eee;
        font-size: 16px;
        line-height: 1.6;
    }
    .company-link {
        font-weight: bold;
        color: #0077cc;
        text-decoration: none;
    }
    .company-link:hover {
        text-decoration: underline;
    }
    .meta {
        font-size: 14px;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 style='color: orange;'>🏆 The Glengarry 100</h1>", unsafe_allow_html=True)

# --- Display leaderboard ---
for idx, (_, row) in enumerate(df.iterrows(), start=1):
    # Medal for top 3, else number
    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
    
    # Company link
    company_link = (
        f'<a class="company-link" href="{row["companyurl"]}" target="_blank">{row["companyname"]}</a>'
        if pd.notnull(row["companyurl"]) and row["companyurl"].strip()
        else row["companyname"]
    )
    
    # City, State
    location = ""
    if pd.notnull(row.get('city')) and pd.notnull(row.get('state')):
        location = f"({row['city']}, {row['state']})"

    # Total listings
    total_listings = 0
    if pd.notnull(row.get('active_listings')) and pd.notnull(row.get('sold_listings')):
        total_listings = int(row['active_listings']) + int(row['sold_listings'])
    elif pd.notnull(row.get('active_listings')):
        total_listings = int(row['active_listings'])

    # Render
    st.markdown(f"""
    <div class="leaderboard-item">
        <span class="rank">{medal}</span>
        {company_link} — {row['name']} {location}<br>
        <span class="meta">[ Active: {row['active_listings']} | Sold: {row.get('sold_listings', 0)} | Total: {total_listings} ]</span>
    </div>
    """, unsafe_allow_html=True)
