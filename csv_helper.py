from supabase_client import supabase
import pandas as pd

# Sample Supabase insert (rn theres no actual tables so this is just a placeholder)
def upload_to_supabase(data):
    # Assuming data is a DataFrame
    for index, row in data.iterrows():
        supabase.table("login_logs").insert(row.to_dict()).execute()
        
# Return login logs as a DataFrame
def get_login_logs():
    """Return login logs as a DataFrame."""
    data = supabase.table("login_logs").select("*").execute()
    df = pd.DataFrame(data.data)
    
    if "uid" in df.columns:
        df["uid"] = df["uid"].astype(int)
    
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    return df