import dash
from dash import html, dcc
from flask import Flask, request, jsonify
from supabase_client import supabase
import pandas as pd
import base64

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Sample Supabase fetch (rn theres no actual tables so this is just a placeholder)
def fetch_data():
    response = supabase.table("logins").select("*").execute()
    return response.data

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

app.layout = html.Div([
    html.H1("Security Dashboard"),
    dcc.Graph(
        id="example-graph",
        figure={
            "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar"}],
            "layout": {"title": "Dummy Data"}
        }
    ), 
    html.Div(id="data-output"),
    html.Hr(),
    html.H2("Upload CSV"),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV'),
        multiple=False
    ),
    html.Div(id='upload-status')
])

@app.callback(
    dash.dependencies.Output('upload-status', 'children'),
    [dash.dependencies.Input('upload-data', 'contents')],
    [dash.dependencies.State('upload-data', 'filename')]
)
def handle_file_upload(contents, filename):
    if contents is not None and filename.endswith('.csv'):
        # Process the CSV file
        process_csv(filename)
        # Process the uploaded CSV file
        return f"File {filename} uploaded successfully."
    elif contents is not None:
        return "Invalid file type. Please upload a CSV file."
    return ""

if __name__ == "__main__":
    app.run(debug=True)
