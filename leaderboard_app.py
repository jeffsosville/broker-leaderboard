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
st.sidebar.header("🔎 Filter Brokers")
region_filter = st.sidebar.selectbox("Region", options=["All"] + sorted(df['region'].unique()))
all_tags = sorted(set(tag for sublist in df['expertise_tags'] for tag in sublist))
expertise_filter = st.sidebar.multiselect("Expertise Tags", options=all_tags)

# --- Apply Filters ---
filtered_df = df.copy()
if region_filter != "All":
    filtered_df = filtered_df[filtered_df['region'] == region_filter]
if expertise_filter:
    filtered_df = filtered_df[filtered_df['expertise_tags'].apply(lambda tags: any(tag in tags for tag in expertise_filter))]

# --- Display Leaderboard ---
st.title("🏆 Broker Leaderboard")
st.write(f"Showing {len(filtered_df)} brokers")

st.dataframe(
    filtered_df.sort_values(by='leaderboard_score', ascending=False)[
        ['broker_name', 'company_name', 'region', 'expertise_tags', 
         'active_listings', 'sold_last_6_months', 'response_score', 'leaderboard_score']
    ]
)

