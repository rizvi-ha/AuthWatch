import pandas as pd
from supabase_client import supabase

# Sample Supabase insert (rn theres no actual tables so this is just a placeholder)
def upload_to_supabase(data):
    # Assuming data is a DataFrame
    for index, row in data.iterrows():
        supabase.table("logins").insert(row.to_dict()).execute()

def process_csv(file):
    df = pd.read_csv(file)
    print(f"Read CSV file: {file}")
    print(df.head())  # For demonstration, print the first few rows
    
    # Upload to Supabase
    # upload_to_supabase(df)    # Uncomment this line to upload to Supabase
    return df