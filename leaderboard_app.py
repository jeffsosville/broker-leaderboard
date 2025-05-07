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
params = st.experimental_get_query_params()
broker_id = params.get('broker_id', [None])[0]


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
.company-title {
    white-space: nowrap;
    display: inline-flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: 4px;
}
@media (max-width: 600px) {
    .company-title {
        display: inline-flex;
        white-space: nowrap;
        align-items: center;
        gap: 2px;            
        font-size: 12px;     
    }
}
@media (max-width: 600px) {
    .company-title .company-link {
        display: inline;  /* ✅ force inline on mobile */
    }
}

</style>
""", unsafe_allow_html=True)

if broker_id is None:
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

        company_link = ...
        listings_link = ...
        city = ...
        ...

        st.markdown(f"""
        <div class="leaderboard-item">
        ...
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

