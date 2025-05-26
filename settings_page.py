import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate

def layout():
    return dbc.Container(
        [
            html.H4("Settings"),
            dbc.Form(
                [
                    dbc.Switch(
                        id="vpn-mode",
                        label="VPN-friendly mode (disables distance & location alerts)",
                    ),
                    dbc.Switch(id="dark-mode", label="Dark mode (beta)"),
                    html.Br(),
                    dbc.Label("Allowed Country (default: Taiwan)"),
                    dcc.Dropdown(
                        id="country-select",
                        options=[
                            {"label": "Taiwan", "value": "Taiwan"},
                            {"label": "USA", "value": "USA"},
                            {"label": "UK", "value": "UK"},
                            {"label": "Germany", "value": "Germany"},
                            {"label": "France", "value": "France"},
                            {"label": "Japan", "value": "Japan"},
                        ],
                        clearable=False,
                    ),
                ],
                className="mt-3",
            ),
            html.Div(id="settings-toast"),
        ],
        fluid=True,
        className="pt-3",
    )

@callback(
    Output("vpn-mode", "value"),
    Output("dark-mode", "value"),
    Output("country-select", "value"),
    Input("url", "pathname"),       
    State("settings-store", "data"),
)
def load_settings(pathname, store):
    if pathname != "/settings":
        raise PreventUpdate


    if not store:
        return False, False, "Taiwan"
    return (
        store.get("vpn_mode", False),
        store.get("dark_mode", False),
        store.get("country", "Taiwan"),
    )
@callback(
    Output("settings-store", "data"),
    Output("settings-toast", "children"),
    Input("vpn-mode", "value"),
    Input("dark-mode", "value"),
    Input("country-select", "value"),
    State("settings-store", "data"),
    prevent_initial_call=True,
)
def save_settings(vpn_val, dark_val, country_val, store):
    updated = {
        "vpn_mode": vpn_val,
        "dark_mode": dark_val,
        "country": country_val,
    }
    toast = html.Small(f"Saved – VPN={vpn_val}, Dark={dark_val}, Country={country_val}")
    return updated, toast

