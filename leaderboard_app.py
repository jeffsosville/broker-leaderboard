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

# ✅ Sort by listings_count descending
df = df.sort_values(by='listings_count', ascending=False).head(100)

# --- UI config ---
st.set_page_config(page_title="The Glengarry 100", layout="wide")

# --- CSS styling ---
st.markdown("""
<style>
body { background: #f9f9f9; font-family: system-ui, sans-serif; color: #222; }
h1 { color: orange; }
.leaderboard-item { padding: 8px 0; border-bottom: 1px solid #eee; }
.company-link { font-weight: bold; color: #0077cc; text-decoration: none; }
.company-link:hover { text-decoration: underline; }
.listings-link { font-weight: bold; color: #FF6600; text-decoration: none; }
.rank-number { font-weight: bold; color: orange; margin-right: 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏆 The Glengarry 100</h1>", unsafe_allow_html=True)

# --- Display leaderboard ---
for idx, (_, row) in enumerate(df.iterrows(), start=1):
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"{idx}.")

    # ✅ Company link
    company_link = (
        f'<a class="company-link" href="{row.get("companyurl", "")}" target="_blank">{row.get("companyname", "Unknown Company")}</a>'
        if pd.notnull(row.get("companyurl")) and row.get("companyurl").strip()
        else row.get("companyname", "Unknown Company")
    )

    # ✅ Listings link
    listings_link = (
        f'<a class="listings-link" href="{row.get("listings_url", "")}" target="_blank">View Listings</a>'
        if pd.notnull(row.get("listings_url")) and row.get("listings_url").strip()
        else ""
    )

    # ✅ Display each broker
    st.markdown(f"""
    <div class="leaderboard-item">
        <span class="rank-number">{medal}</span> {company_link} — {listings_link}<br>
        <strong>Broker:</strong> {row.get("name", "N/A")}<br>
        <strong>Active Listings:</strong> {row.get("listings_count", 0)}
    </div>
    """, unsafe_allow_html=True)
