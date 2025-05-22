import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from flask import Flask

import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
from helper import get_recent_alerts

import alerts_page
import upload_page
import settings_page

from csv_helper import get_login_logs

###############################################################################
#  Flask + Dash bootstrap
###############################################################################
server = Flask(__name__)
app: Dash = Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,  # we’ll use pages later
    title="Login Monitoring Dashboard",
)

###############################################################################
# DATA (fake for now)
###############################################################################
N_USERS = 25_000
NOW = datetime.utcnow()

def _random_ip() -> str:
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

def _random_login_dataframe(days: int = 7, rows: int = 5_000) -> pd.DataFrame:
    rng = np.random.default_rng()
    df = pd.DataFrame(
        {
            "uid": rng.integers(1, N_USERS, rows),
            "timestamp": [
                (NOW - timedelta(hours=rng.uniform(0, 24 * days))).isoformat()
                for _ in range(rows)
            ],
            "ip_address": [_random_ip() for _ in range(rows)],
            "browser": rng.choice(["Chrome", "Edge", "Firefox", "Safari"], rows),
            "os": rng.choice(["Windows", "macOS", "Linux", "Android", "iOS"], rows),
            "device": rng.choice(["Desktop", "Laptop", "Mobile", "Tablet"], rows),
            "login_result": rng.choice([True, False], rows, p=[0.97, 0.03]),
        }
    )
    return df

#  Fake raw data we’ll visualise
# RAW_DF = _random_login_dataframe()

# Use raw data from Supabase
RAW_DF = get_login_logs()

###############################################################################
# Helper functions (plug in real queries later) 
###############################################################################
def get_kpis(df: pd.DataFrame) -> dict:
    """Return the numbers for the four KPI cards."""

    # TODO: replace with real queries
    total_users = df["uid"].nunique()
    failed = (~df["login_result"]).sum()
    suspicious = random.randint(10, 30)  # placeholder rule
    active_sessions = random.randint(1_000, 2_000)  # placeholder

    return dict(
        total_users=total_users,
        failed=failed,
        suspicious=suspicious,
        active_sessions=active_sessions,
    )


###############################################################################
# UI components 
###############################################################################
def kpi_card(title: str, value: str, subtitle: str, icon: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(className=f"{icon} fs-3 text-secondary"),
                html.H4(f"{value:,}", className="card-title mt-2"),
                html.Small(title, className="text-muted fw-semibold"),
                html.Br(),
                html.Small(subtitle, className="text-success"),
            ]
        ),
        className="border-0 shadow-sm text-center",
    )

sidebar = dbc.Nav(
    [
        dbc.NavLink([html.I(className="bi bi-speedometer2 me-2"), "Dashboard"], href="/", active="exact"),
        dbc.NavLink([html.I(className="bi bi-bell-fill me-2"), "Alerts"], href="/alerts", active="exact"),
        dbc.NavLink([html.I(className="bi bi-upload me-2"), "Upload Logs"], href="/upload", active="exact"),
        dbc.NavLink([html.I(className="bi bi-gear-fill me-2"), "Settings"], href="/settings", active="exact"),
    ],
    vertical=True,
    pills=True,
    className="mt-4",
)

def build_dashboard():
    kpis = get_kpis(RAW_DF)

    #  Login volume line chart
    volume_df = (
        RAW_DF.assign(day=lambda d: pd.to_datetime(d["timestamp"]).dt.date)
        .groupby("day")
        .size()
        .reset_index(name="logins")
    )
    volume_fig = px.line(volume_df, x="day", y="logins", title="Login Volume Trends")

    #  Success rate pie
    success_fig = px.pie(
        RAW_DF,
        names="login_result",
        title="Login Success Rate",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.G10,
    )

    #  Geographic distribution (fake geo scatter)
    # TODO: replace with real geo data *calculated* from IP addresses
    geo_df = pd.DataFrame(
        dict(
            city=["New York", "London", "Tokyo", "Sydney"],
            lat=[40.7, 51.5, 35.7, -33.9],
            lon=[-74.0, -0.1, 139.7, 151.2],
            logins=[500, 350, 420, 120],
        )
    )
    geo_fig = px.scatter_geo(
        geo_df,
        lat="lat",
        lon="lon",
        size="logins",
        hover_name="city",
        projection="natural earth",
        title="Geographic Distribution",
    )

    #  Alert list
    alerts = get_recent_alerts()
    alert_list = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                [
                    html.I(className=f"{a['icon']} me-2 text-danger"),
                    html.Strong(a["title"]),
                    html.Br(),
                    html.Span(a["body"], className="text-muted small"),
                    html.Span(a["ts"], className="float-end text-muted small"),
                ]
            )
            for a in alerts
        ]
    )

    return dbc.Container(
        [
            #  KPI row
            dbc.Row(
                [
                    dbc.Col(kpi_card("Total Users", kpis["total_users"], "+2.5 % from yesterday", "bi bi-people-fill"), md=3),
                    dbc.Col(kpi_card("Failed Logins", kpis["failed"], "Last 24 hours", "bi bi-exclamation-triangle-fill"), md=3),
                    dbc.Col(kpi_card("Suspicious Activity", kpis["suspicious"], "Detected today", "bi bi-shield-fill"), md=3),
                    dbc.Col(kpi_card("Active Sessions", kpis["active_sessions"], "Currently active", "bi bi-person-badge-fill"), md=3),
                ],
                className="gy-4",
            ),
            html.Hr(),
            #  Charts
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=volume_fig, config={"displayModeBar": False}), md=6),
                    dbc.Col(dcc.Graph(figure=success_fig, config={"displayModeBar": False}), md=6),
                ],
                className="gy-4",
            ),
            dbc.Row(
                dbc.Col(dcc.Graph(figure=geo_fig, config={"displayModeBar": False}), md=12),
                className="gy-4",
            ),
            #  Alerts
            html.H5("Recent Alerts"),
            dbc.Row(dbc.Col(alert_list, md=12), className="gy-4"),
            html.Br(),
        ],
        fluid=True,
        className="pt-4",
    )

###############################################################################
# Overall layout  
###############################################################################
app.layout = dbc.Row(
    [
        dbc.Col(sidebar, width=2, className="bg-light vh-100 position-fixed"),
        dbc.Col(
            [
                dbc.NavbarSimple(
                    brand="Login Monitoring Dashboard",
                    color="white",
                    className="shadow-sm mb-3",
                    sticky="top",
                ),
                dcc.Location(id="url"),
                html.Div(id="page-content"),
            ],
            width={"size": 10, "offset": 2},
        ),
    ],
    className="g-0",
)

###############################################################################
#  Callbacks
###############################################################################

@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname: str):
    """Swap centre column based on URL path."""
    if pathname == "/alerts":
        return alerts_page.layout()
    elif pathname == "/upload":
        return upload_page.layout()
    elif pathname == "/settings":
        return settings_page.layout()
    # default → dashboard
    return build_dashboard()

###############################################################################
#  Run server
###############################################################################
if __name__ == "__main__":
    app.run(debug=True, port=8080)
