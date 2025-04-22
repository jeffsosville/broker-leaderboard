from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = f"https://{os.getenv('SUPABASE_HOST')}"
SUPABASE_KEY = os.getenv('SUPABASE_API_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch first 5 brokers
response = supabase.table('brokers').select("*").limit(5).execute()

print(response.data)

