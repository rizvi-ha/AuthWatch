import dash
from dash import html, dcc
from flask import Flask
from supabase_client import supabase

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Sample Supabase fetch (rn theres no actual tables so this is just a placeholder)
def fetch_data():
    response = supabase.table("logins").select("*").execute()
    return response.data

app.layout = html.Div([
    html.H1("Security Dashboard"),
    dcc.Graph(
        id="example-graph",
        figure={
            "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar"}],
            "layout": {"title": "Dummy Data"}
        }
    )
])

if __name__ == "__main__":
    app.run(debug=True)
