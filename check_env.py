import os
from dotenv import load_dotenv

load_dotenv()

print("SUPABASE_API_KEY:", os.getenv('SUPABASE_API_KEY'))

