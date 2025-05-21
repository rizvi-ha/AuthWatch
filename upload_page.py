import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import io, base64

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
# TODO: yucheng replace with ur real code
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
        _, b64 = content.split(",")
        decoded = base64.b64decode(b64)
        # crude format detection – revise for your needs
        if name.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode()))
        else:
            df = pd.read_json(io.StringIO(decoded.decode()))
        messages.append(f"✅ {name}: {len(df):,} rows imported")
    return [html.Div(m) for m in messages]
