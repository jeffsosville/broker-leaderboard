import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Supabase Setup ---
SUPABASE_URL = "https://rxbaimgjakefhxsaksdl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ4YmFpbWdqYWtlZmh4c2Frc2RsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjYyNjQ0OSwiZXhwIjoyMDYyMjAyNDQ5fQ.aFgdVDkCCjYLX8b6y03Cz85SGiq2FYB8auF4hgLimUs"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Streamlit Setup ---
st.set_page_config(page_title="The Glengarry 100 Preview", layout="wide")
st.title("\U0001F3C6 The Glengarry 100 Preview")

# --- Sidebar Filters ---
st.sidebar.header("Search & Filter")
search_term = st.sidebar.text_input("Search broker or company name")

# Get unique states for dropdown
state_list = supabase.table("all brokers").select("state").execute().data
unique_states = sorted({r['state'].upper() for r in state_list if r['state']})
state_filter = st.sidebar.selectbox("Filter by state", options=["All"] + unique_states)

# Option to show all or just featured
show_all = st.sidebar.checkbox("Show all brokers (not just Top 100)", value=False)

# --- Fetch Broker Data ---
query = supabase.table("all brokers").select("*")
if not show_all:
    query = query.eq("is_featured", True)
data = query.execute().data

df = pd.DataFrame(data)
if df.empty:
    st.warning("No broker data found.")
    st.stop()

# --- Apply Filters ---
if search_term:
    df = df[df.apply(lambda row: search_term.lower() in str(row.get('broker_name', '')).lower() or search_term.lower() in str(row.get('company_name', '')).lower(), axis=1)]

if state_filter != "All":
    df = df[df['state'].str.upper() == state_filter]

# --- Sort by Score ---
df = df.sort_values(by='leaderboard_score', ascending=False, na_position='last').reset_index(drop=True)


# --- Display Results ---
for i, row in df.iterrows():
    rank = i + 1
    name = (row.get('company_name') or 'Unknown').title()
    broker = row.get('broker_name', '').title()
    location = f"{row.get('city', '').title()}, {row.get('state', '').upper()}"
    phone = row.get('phone', '')
    active = row.get('active_listings', 0)
    sold = row.get('sold_listings', 0)
    score = row.get('leaderboard_score', 0)
    url = row.get('listings_url') or row.get('companyurl') or row.get('companyUrl') or "#"


    medal = ""
    if rank == 1:
        medal = "🥇"
    elif rank == 2:
        medal = "🥈"
    elif rank == 3:
        medal = "🥉"

    st.markdown(f"""
    <div style='border:1px solid #333; padding:10px; border-radius:5px; margin-bottom:10px;'>
        <b>{medal} {rank}. <a href='{url}' target='_blank'>{name}</a></b> | {location} | {phone}<br>
        Active: {active} | Sold: {sold} | Score: {score} | <a href='{url}' target='_blank'>View Listings</a>
    </div>
    """, unsafe_allow_html=True)

if df.empty:
    st.info("No matching brokers found.")
