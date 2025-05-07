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

# --- Sort by leaderboard_score or active_listings ---
if 'leaderboard_score' in df.columns:
    df = df.sort_values(by='leaderboard_score', ascending=False)
else:
    df = df.sort_values(by='active_listings', ascending=False)

df = df.head(100)

# --- Display leaderboard ---
st.set_page_config(page_title="The Glengarry 100", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #f9f9f9;
    }
    .rank { color: orange; font-weight: bold; }
    .card {
        padding: 10px;
        margin-bottom: 12px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 15px;
        line-height: 1.6;
    }
    .company-link { font-weight: bold; color: #0056b3; text-decoration: none; }
    .company-link:hover { text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: orange;'>🏆 The Glengarry 100</h1>", unsafe_allow_html=True)

for idx, (_, row) in enumerate(df.iterrows(), start=1):
    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
    
    company_link = f'<a class="company-link" href="{row["companyurl"]}" target="_blank">{row["company_name"]}</a>' if pd.notnull(row["companyurl"]) and row["companyurl"].strip() else row["company_name"]
    
    city_state = f"({row['city']}, {row['state']})" if pd.notnull(row['city']) and pd.notnull(row['state']) else ""
    
    total_listings = int(row['active_listings']) + int(row['sold_listings']) if pd.notnull(row['active_listings']) and pd.notnull(row['sold_listings']) else row['active_listings']
    
    st.markdown(f"""
    <div class="card">
        <span class="rank">{medal}</span> {company_link} — {row['broker_name']} {city_state}<br>
        <span style="color: #666;">[ Active: {row['active_listings']} | Sold: {row['sold_listings']} | Total: {total_listings} ]</span>
    </div>
    """, unsafe_allow_html=True)
