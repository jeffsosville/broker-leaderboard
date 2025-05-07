import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# --- Load environment variables ---
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

# Sort by leaderboard_score descending
df = df.sort_values(by='leaderboard_score', ascending=False).head(100)

st.set_page_config(page_title="The Glengarry 100", layout="wide")
st.markdown("""
<style>
body { background: #f9f9f9; font-family: system-ui, sans-serif; color: #222; }
h1 { color: orange; }
.leaderboard-item { background:#fff; padding:15px; margin-bottom:12px; border-radius:8px; border:1px solid #ddd; }
.company-link { font-weight: bold; color: #0077cc; text-decoration: none; }
.company-link:hover { text-decoration: underline; }
.listings-link { font-weight: bold; color: #FF6600; text-decoration: none; }
.rank-number { font-weight: bold; color: orange; margin-right: 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏆 The Glengarry 100</h1>", unsafe_allow_html=True)

for idx, row in df.iterrows():
    medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(idx, f"{idx+1}.")

    company_link = f'<a class="company-link" href="{row["companyurl"]}" target="_blank">{row["company_name"]}</a>' if pd.notnull(row["companyurl"]) else row["company_name"]
    listings_link = f'<a class="listings-link" href="{row["listings_url"]}" target="_blank">View Listings</a>' if pd.notnull(row["listings_url"]) else "No Listings Link"

    st.markdown(f"""
    <div class="leaderboard-item">
        <span class="rank-number">{medal}</span> {company_link} — {listings_link}<br>
        <strong>Broker:</strong> {row.get("broker_name", "N/A")}<br>
        <strong>City:</strong> {row.get("city", "N/A")} &nbsp; | &nbsp; <strong>State:</strong> {row.get("state", "N/A")}<br>
        <strong>Active Listings:</strong> {int(row.get("active_listings", 0))} &nbsp; | &nbsp;
        <strong>Sold Listings:</strong> {int(row.get("sold_listings", 0))}<br>
        <strong>Email:</strong> {row.get("email", "N/A")} &nbsp; | &nbsp; <strong>Phone:</strong> {row.get("phone", "N/A")}<br>
        <strong>Leaderboard Score:</strong> {row.get("leaderboard_score", "N/A")}<br>
        <strong>Alternative URL:</strong> {row.get("alternative_url", "N/A")}
    </div>
    """, unsafe_allow_html=True)
