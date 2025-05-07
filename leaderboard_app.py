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

    # Rename to normalized keys
    df = df.rename(columns={
        'name': 'broker_name',
        'company_name': 'company_name',
        'listings_count': 'active_listings'
        'companyurl': 'companyurl',
        'listings_url': 'listings_url'
    })

    # Fill missing optional fields
    df['region'] = 'N/A'
    df['sold_last_6_months'] = 0
    df['response_score'] = 0
    df['leaderboard_score'] = df['active_listings']

    return df

df = load_data()

# ✅ No sidebar for now
st.set_page_config(page_title="Glengarry 100", layout="wide")
st.markdown("""
<style>
body { background-color: #f5f5f5; color: #222; font-family: sans-serif; }
h1 { color: #FF6600; }
.broker-card { background: white; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.company-link { color: #007BFF; font-weight: bold; text-decoration: none; }
.company-link:hover { text-decoration: underline; }
.listings-link { color: #FF6600; font-weight: bold; text-decoration: none; }
.listings-link:hover { text-decoration: underline; }
.rank-number { font-weight: bold; margin-right: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🏆 The Glengarry 100")

# Sort by leaderboard_score
filtered_df = df.sort_values(by='leaderboard_score', ascending=False).head(100)

# --- Display Leaderboard ---
for idx, (_, row) in enumerate(filtered_df.iterrows(), start=1):
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"{idx}.")
    
    company_link = (
        f'<a class="company-link" href="{row.get("companyurl", "")}" target="_blank">{row.get("company_name", "Unknown Company")}</a>'
        if pd.notnull(row.get("companyurl")) and row.get("companyurl").strip()
        else row.get("company_name", "Unknown Company")
    )
    
    listings_link = (
        f'<a class="listings-link" href="{row.get("listings_url", "")}" target="_blank">View Listings</a>'
        if pd.notnull(row.get("listings_url")) and row.get("listings_url").strip()
        else ""
    )
    
    broker_display = f'<span class="rank-number">{medal}</span> {company_link} — {listings_link}'

    st.markdown(f"""
<div class='broker-card'>
{broker_display}<br>
<strong>Broker:</strong> {row.get("broker_name", "N/A")}<br>
<strong>Active Listings:</strong> {row["active_listings"]}
</div>
""", unsafe_allow_html=True)
