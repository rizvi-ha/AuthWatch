from supabase_client import supabase

# Sample Supabase insert (rn theres no actual tables so this is just a placeholder)
def upload_to_supabase(data):
    # Assuming data is a DataFrame
    for index, row in data.iterrows():
        supabase.table("logins").insert(row.to_dict()).execute()