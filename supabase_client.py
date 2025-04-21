from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL == None or SUPABASE_KEY == None:
    raise ValueError("Supabase URL or Key not set in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Connected to Supabase successfully")
