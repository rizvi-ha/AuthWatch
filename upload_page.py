import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import io, base64
from csv_helper import upload_to_supabase

def layout():
    return dbc.Container(
        [
            html.H4("Upload Log Files"),
            dcc.Upload(
                id="upload-data",
                children=html.Div(["📥  Drag & drop or click to select JSON / CSV"]),
                multiple=True,
                className="border border-secondary rounded p-5 text-center",
            ),
            html.Div(id="upload-status"),
        ],
        fluid=True,
        className="pt-3",
    )

# Example callback that just counts rows and echoes a message -------------
# TODO: yucheng replace with ur real code   -> Left Supabase uploaded 
@callback(
    Output("upload-status", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def handle_upload(list_of_contents, list_of_names):
    if not list_of_contents:
        return ""
    messages = []
    for content, name in zip(list_of_contents, list_of_names):
        if content is not None:
            content_type, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            if "csv" in name:
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif "json" in name:
                df = pd.read_json(io.StringIO(decoded.decode("utf-8")))
            else:
                return "Unsupported file type"
            
            # Upload to Supabase
            # upload_to_supabase(df)
            
            messages.append(f"Uploaded {name} with {len(df)} rows.")
            
    return html.Div(messages)