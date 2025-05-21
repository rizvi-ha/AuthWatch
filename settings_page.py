import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output

def layout():
    return dbc.Container(
        [
            html.H4("Settings"),
            dbc.Form(
                [
                    dbc.Switch(
                        id="vpn-mode",
                        label="VPN-friendly mode (disables distance & location alerts)",
                        value=False,
                    ),
                    dbc.Switch(id="dark-mode", label="Dark mode (beta)", value=False),
                ],
                className="mt-3",
            ),
            html.Div(id="settings-toast"),
        ],
        fluid=True,
        className="pt-3",
    )

# simple demo callback -----------------------------------------------------
@callback(
    Output("settings-toast", "children"),
    Input("vpn-mode", "value"),
    Input("dark-mode", "value"),
)
def save_settings(vpn_mode, dark_mode):
    # TODO: persist to DB or config file
    return html.Small(f"Saved – VPN mode={vpn_mode}, dark mode={dark_mode}")
