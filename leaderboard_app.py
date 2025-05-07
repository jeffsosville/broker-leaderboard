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
filtered_df = df

# Sort by leaderboard_score descending
df = df.sort_values(by='leaderboard_score', ascending=False).head(100)

st.set_page_config(page_title="The Glengarry 100", layout="wide")
st.markdown("""
<style>
.leaderboard-item {
    background: #111;
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 6px;
    border: 1px solid #333;
    color: #ddd;
    font-size: 14px;
    line-height: 1.4;
}

.company-link { 
    font-weight: bold; 
    color: #3399ff; 
    text-decoration: none; 
}

.company-link:hover { 
    text-decoration: underline; 
}

.listings-link { 
    font-weight: bold; 
    color: #FF6600; 
    text-decoration: none; 
}

.rank-number { 
    font-weight: bold; 
    color: orange; 
    margin-right: 4px; 
}

@media (max-width: 600px) {
    .leaderboard-item {
        font-size: 13px;
        padding: 10px;
    }
    .company-link, .listings-link {
        display: block;
        margin-top: 4px;
    }
}

</style>
""", unsafe_allow_html=True)


st.markdown("<h1>🏆 The Glengarry 100</h1>", unsafe_allow_html=True)

for idx, (_, row) in enumerate(filtered_df.iterrows(), start=1):
    # Medal emoji
    if idx == 1:
        medal = "🥇"
    elif idx == 2:
        medal = "🥈"
    elif idx == 3:
        medal = "🥉"
    else:
        medal = f"{idx}."

    # Safe fallbacks
    company_link = f'<a class="company-link" href="{row["companyurl"]}" target="_blank">{row["company_name"]}</a>'
    listings_link = f'<a class="listings-link" href="{row["listings_url"]}" target="_blank">View Listings</a>'
    city = row.get("city", "N/A")
    state = row.get("state", "N/A")
    phone = row.get("phone", "N/A")
    email = row.get("email", "N/A")

    st.markdown(f"""
<div class="leaderboard-item">
<b>{medal} {company_link}</b> — {city}, {state} | {phone} | {email}<br>
Active: {row["active_listings"]} | Sold: {row["sold_listings"]} | Score: {row["leaderboard_score"]} | {listings_link}
</div>
""", unsafe_allow_html=True)

