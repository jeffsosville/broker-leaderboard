import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# ✅ Must be first Streamlit command
st.set_page_config(page_title="The Glengarry 100", layout="wide")

# --- Load environment variables ---
load_dotenv()
SUPABASE_URL = f"https://{os.getenv('SUPABASE_HOST')}"
SUPABASE_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Query param detection
params = st.query_params
broker_id = params.get('broker_id', [None])[0]

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

# CSS
st.markdown("""
<style>
[YOUR EXISTING CSS HERE]
</style>
""", unsafe_allow_html=True)

# ✅ MAIN LOGIC
if broker_id is None:
    st.markdown("<h1>🏆 The Glengarry 100</h1>", unsafe_allow_html=True)
    
st.write("Columns in dataframe:", filtered_df.columns.tolist())

for idx, (_, row) in enumerate(filtered_df.iterrows(), start=1):
        if idx == 1:
            medal = "🥇"
        elif idx == 2:
            medal = "🥈"
        elif idx == 3:
            medal = "🥉"
        else:
            medal = f"{idx}."

        company_link = f'<a class="company-link" href="{row["companyurl"]}" target="_blank">{row["company_name"]}</a>'
        listings_link = f'<a class="listings-link" href="?broker_id={row["id"]}">View Listings</a>'
        city = row.get("city", "N/A")
        state = row.get("state", "N/A")
        phone = row.get("phone", "N/A")

        st.markdown(f"""
        <div class="leaderboard-item">
        <span class="company-title"><b>{medal} {company_link}</b></span>
        | {city}, {state} | {phone}<br>
        Active: {row["active_listings"]} | Sold: {row["sold_listings"]} | Score: {row["leaderboard_score"]} | {listings_link}
        </div>
        """, unsafe_allow_html=True)

else:
    broker = supabase.table('brokers_leaderboard').select('*').eq('id', broker_id).single().execute().data
    st.title(f"📂 Listings for {broker['broker_name']}")

    listings = supabase.table('listings').select('*').eq('broker_id', broker_id).execute().data
    df_listings = pd.DataFrame(listings)

    if df_listings.empty:
        st.info("No listings available yet for this broker.")
    else:
        st.table(df_listings[['title', 'price', 'net_income', 'location', 'listing_url']])

    st.markdown("[⬅️ Back to Leaderboard](/)")
