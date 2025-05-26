import random
from datetime import datetime, timedelta
from datetime import timezone

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



# Use raw data from Supabase
RAW_DF = get_login_logs()

###############################################################################
# Helper functions (plug in real queries later) 
###############################################################################
def count_suspicious(df: pd.DataFrame, vpn_mode=False, allowed_country="Taiwan") -> int:
    suspicious_set = set()

    #Repeated failed attempts by IP
    ip_failures = df[~df["login_result"]]["ip_address"].value_counts()
    for ip, count in ip_failures.items():
        if count >= 3:
            suspicious_set.add(f"IP::{ip}")

    #Repeated failed attempts by UID
    uid_failures = df[~df["login_result"]]["uid"].value_counts()
    for uid, count in uid_failures.items():
        if count >= 3:
            suspicious_set.add(f"UID::{uid}")

    # Foreign logins (only if VPN is off)
    if not vpn_mode:
        ip_to_country = {
            "66.206.89.11": "USA",
            "38.183.48.25": "UK",
            "53.120.67.248": "Taiwan",
            "134.20.151.217": "Taiwan",
            "124.132.128.69": "Taiwan",
            "218.90.33.123": "Japan",
            "218.70.250.234": "Taiwan",
            "134.63.156.154": "Taiwan",
            "222.55.201.154": "Taiwan",
            "144.31.231.185": "Taiwan",
            "214.127.233.122": "Australia",
            "161.94.93.133": "Taiwan",
            "129.141.34.136": "Taiwan",
            "220.109.170.18": "Taiwan",
            "63.204.126.213": "USA",
            "74.131.146.207": "Taiwan",
            "186.174.57.125": "Taiwan",
            "196.189.205.50": "Taiwan",
            "216.35.142.90": "Taiwan",
            "197.8.132.138": "Taiwan",
            "113.157.136.109": "USA",
            "182.129.37.16": "Taiwan",
            "182.187.77.223": "Taiwan",
            "63.165.105.39": "Taiwan",
            "154.51.61.158": "Taiwan",
            "222.109.65.48": "Taiwan",
            "207.183.200.174": "Taiwan",
            "199.49.137.13": "Taiwan",
            "205.234.56.25": "Taiwan",
            "206.87.134.148": "Taiwan",
            "209.114.171.210": "Taiwan",
            "151.214.48.121": "Taiwan",
            "213.38.155.206": "Taiwan",
            "169.71.188.61": "Taiwan",
            "119.74.140.99": "Taiwan",
            "207.117.37.207": "Taiwan",
            "2.202.141.118": "Germany",
            "22.79.23.82": "Taiwan",
            "204.176.42.106": "Taiwan",
            "194.99.174.220": "Taiwan",
            "187.7.179.156": "Taiwan",
            "143.223.218.51": "Taiwan",
            "205.12.121.36": "Taiwan",
            "165.242.48.249": "Taiwan",
            "170.58.33.145": "Taiwan",
            "102.157.160.161": "Taiwan",
            "214.120.11.119": "Taiwan",
            "138.69.32.232": "Taiwan",
            "214.177.197.177": "Taiwan",
            "212.45.91.169": "Taiwan",
            "180.152.194.206": "Taiwan",
            "54.132.245.5": "Taiwan",
            "175.117.240.148": "Taiwan",
            "135.66.7.200": "Taiwan",
            "89.165.121.13": "Taiwan",
            "222.138.190.221": "Taiwan",
            "108.106.201.32": "Taiwan",
            "222.34.249.236": "Taiwan",
            "193.48.128.119": "Taiwan",
            "101.212.115.144": "Taiwan",
            "159.120.131.226": "Taiwan",
            "211.105.73.112": "Taiwan",
            "152.214.72.16": "Taiwan",
            "200.64.249.114": "Taiwan",
            "155.239.201.150": "Taiwan",
            "134.1.221.45": "Taiwan",
            "212.208.124.166": "Taiwan",
            "217.47.246.14": "Taiwan",
            "204.49.253.9": "Taiwan",
            "92.7.26.105": "Taiwan",
            "220.67.34.89": "Taiwan",
            "190.96.106.62": "Taiwan",
            "24.223.136.35": "Taiwan",
            "7.138.242.237": "Taiwan",
            "198.141.131.108": "Taiwan",
            "220.23.112.183": "Taiwan",
            "98.58.11.86": "Taiwan",
            "131.170.51.108": "Taiwan",
            "58.21.91.2": "Taiwan",
            "203.67.31.48": "Taiwan",
            "143.168.248.20": "Taiwan",
            "223.147.68.70": "Taiwan",
            "195.58.232.124": "Taiwan",
            "215.156.15.130": "Taiwan",
            "190.110.93.192": "Taiwan",
            "132.246.226.129": "Taiwan",
            "131.70.84.166": "Taiwan",
            "216.230.231.83": "Taiwan",
            "217.85.190.144": "Taiwan",
            "115.232.39.161": "Taiwan",
            "74.60.80.187": "Taiwan",
            "198.179.120.6": "Taiwan",
            "141.60.189.30": "Taiwan",
            "213.175.2.8": "Taiwan",
            "148.55.94.6": "Taiwan",
            "15.72.245.47": "Taiwan",
            "214.176.22.37": "Taiwan",
        }
        for _, row in df.iterrows():
            ip = row["ip_address"]
            country = ip_to_country.get(ip, "Taiwan")
            if country != allowed_country:
                suspicious_set.add(f"Foreign::{ip}")

    return len(suspicious_set)


def get_kpis(df: pd.DataFrame, vpn_mode=False, allowed_country="Taiwan") -> dict:
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    total_users = df["uid"].nunique()
    failed = (~df["login_result"]).sum()

    active_sessions = df[
        (df["login_result"] == True) &
        (df["timestamp"] >= one_hour_ago)
    ]["uid"].nunique()

    suspicious = count_suspicious(df, vpn_mode=vpn_mode, allowed_country=allowed_country)

    return dict(
        total_users=total_users,
        failed=failed,
        suspicious=suspicious,
        active_sessions=active_sessions,
    )




###############################################################################
# UI components 
###############################################################################
def kpi_card(title: str, value: str, subtitle: str, icon: str, dark_mode: bool = False) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(className=f"{icon} fs-3" + (" text-light" if dark_mode else " text-secondary")),
                html.H4(f"{value:,}", className="card-title mt-2" + (" text-light" if dark_mode else "")),
                html.Small(title, className="text-muted fw-semibold"),
                html.Br(),
                html.Small(subtitle, className="text-success"),
            ]
        ),
        className="border-0 shadow-sm text-center " + ("bg-secondary" if dark_mode else "")
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

def build_dashboard(vpn_mode=False, allowed_country="Taiwan", dark_mode=False):

    kpis = get_kpis(RAW_DF, vpn_mode=vpn_mode, allowed_country=allowed_country)


    #  Login volume line chart
    volume_df = (
        RAW_DF.assign(day=lambda d: pd.to_datetime(d["timestamp"]).dt.date)
        .groupby("day")
        .size()
        .reset_index(name="logins")
    )
    volume_fig = px.line(volume_df, x="day", y="logins", title="Login Volume Trends")
    volume_fig.update_layout(template="plotly_dark" if dark_mode else "plotly")


    #  Success rate pie
    success_fig = px.pie(
        RAW_DF,
        names="login_result",
        title="Login Success Rate",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    success_fig.update_layout(template="plotly_dark" if dark_mode else "plotly")


    #  Geographic distribution 
    from collections import defaultdict

    # IP ➝ country mapping
    ip_to_country = {
       "66.206.89.11": "USA",
        "38.183.48.25": "UK",
        "53.120.67.248": "Taiwan",
        "134.20.151.217": "Taiwan",
        "124.132.128.69": "Taiwan",
        "218.90.33.123": "Japan",
        "218.70.250.234": "Taiwan",
        "134.63.156.154": "Taiwan",
        "222.55.201.154": "Taiwan",
        "144.31.231.185": "Taiwan",
        "214.127.233.122": "Australia",
        "161.94.93.133": "Taiwan",
        "129.141.34.136": "Taiwan",
        "220.109.170.18": "Taiwan",
        "63.204.126.213": "USA",
        "74.131.146.207": "Taiwan",
        "186.174.57.125": "Taiwan",
        "196.189.205.50": "Taiwan",
        "216.35.142.90": "Taiwan",
        "197.8.132.138": "Taiwan",
        "113.157.136.109": "USA",
        "182.129.37.16": "Taiwan",
        "182.187.77.223": "Taiwan",
        "63.165.105.39": "Taiwan",
        "154.51.61.158": "Taiwan",
        "222.109.65.48": "Taiwan",
        "207.183.200.174": "Taiwan",
        "199.49.137.13": "Taiwan",
        "205.234.56.25": "Taiwan",
        "206.87.134.148": "Taiwan",
        "209.114.171.210": "Taiwan",
        "151.214.48.121": "Taiwan",
        "213.38.155.206": "Taiwan",
        "169.71.188.61": "Taiwan",
        "119.74.140.99": "Taiwan",
        "207.117.37.207": "Taiwan",
        "2.202.141.118": "Germany",
        "22.79.23.82": "Taiwan",
        "204.176.42.106": "Taiwan",
        "194.99.174.220": "Taiwan",
        "187.7.179.156": "Taiwan",
        "143.223.218.51": "Taiwan",
        "205.12.121.36": "Taiwan",
        "165.242.48.249": "Taiwan",
        "170.58.33.145": "Taiwan",
        "102.157.160.161": "Taiwan",
        "214.120.11.119": "Taiwan",
        "138.69.32.232": "Taiwan",
        "214.177.197.177": "Taiwan",
        "212.45.91.169": "Taiwan",
        "180.152.194.206": "Taiwan",
        "54.132.245.5": "Taiwan",
        "175.117.240.148": "Taiwan",
        "135.66.7.200": "Taiwan",
        "89.165.121.13": "Taiwan",
        "222.138.190.221": "Taiwan",
        "108.106.201.32": "Taiwan",
        "222.34.249.236": "Taiwan",
        "193.48.128.119": "Taiwan",
        "101.212.115.144": "Taiwan",
        "159.120.131.226": "Taiwan",
        "211.105.73.112": "Taiwan",
        "152.214.72.16": "Taiwan",
        "200.64.249.114": "Taiwan",
        "155.239.201.150": "Taiwan",
        "134.1.221.45": "Taiwan",
        "212.208.124.166": "Taiwan",
        "217.47.246.14": "Taiwan",
        "204.49.253.9": "Taiwan",
        "92.7.26.105": "Taiwan",
        "220.67.34.89": "Taiwan",
        "190.96.106.62": "Taiwan",
        "24.223.136.35": "Taiwan",
        "7.138.242.237": "Taiwan",
        "198.141.131.108": "Taiwan",
        "220.23.112.183": "Taiwan",
        "98.58.11.86": "Taiwan",
        "131.170.51.108": "Taiwan",
        "58.21.91.2": "Taiwan",
        "203.67.31.48": "Taiwan",
        "143.168.248.20": "Taiwan",
        "223.147.68.70": "Taiwan",
        "195.58.232.124": "Taiwan",
        "215.156.15.130": "Taiwan",
        "190.110.93.192": "Taiwan",
        "132.246.226.129": "Taiwan",
        "131.70.84.166": "Taiwan",
        "216.230.231.83": "Taiwan",
        "217.85.190.144": "Taiwan",
        "115.232.39.161": "Taiwan",
        "74.60.80.187": "Taiwan",
        "198.179.120.6": "Taiwan",
        "141.60.189.30": "Taiwan",
        "213.175.2.8": "Taiwan",
        "148.55.94.6": "Taiwan",
        "15.72.245.47": "Taiwan",
        "214.176.22.37": "Taiwan",
    }

    # Country ➝ coordinates (for plot)
    country_to_coords = {
        "Taiwan": {"lat": 25.0330, "lon": 121.5654},
        "USA": {"lat": 38.89511, "lon": -77.03637},
        "UK": {"lat": 51.5074, "lon": -0.1278},
        "Japan": {"lat": 35.6895, "lon": 139.6917},
        "Germany": {"lat": 52.52, "lon": 13.4050},
        "Australia": {"lat": -33.8688, "lon": 151.2093},
    }

    # Aggregate IP ➝ country ➝ login count
    ip_counts = RAW_DF.groupby("ip_address").size().reset_index(name="logins")
    country_logins = defaultdict(int)

    for _, row in ip_counts.iterrows():
        ip = row["ip_address"]
        count = row["logins"]
        country = ip_to_country.get(ip, "Taiwan")
        country_logins[country] += count

    geo_data = []
    for country, count in country_logins.items():
        coords = country_to_coords.get(country)
        if coords:
            geo_data.append({
                "country": country,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "logins": count,
            })

    geo_df = pd.DataFrame(geo_data)

    geo_fig = px.scatter_geo(
    geo_df,
    lat="lat",
    lon="lon",
    size="logins",
    hover_name="country",
    projection="natural earth",
    title="Geographic Distribution of Logins",
    size_max=40,
    )

    geo_fig.update_traces(
        marker=dict(sizemode="area", sizeref=1, sizemin=6, line=dict(width=0.5, color="white"))
    )
    
    geo_fig.update_layout(template="plotly_dark" if dark_mode else "plotly")




    #  Alert list
    alerts = get_recent_alerts(vpn_mode=vpn_mode, allowed_country=allowed_country)
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

    navbar = dbc.NavbarSimple(
    brand="Login Monitoring Dashboard",
    color="dark" if dark_mode else "white",
    dark=dark_mode,
    className="shadow-sm mb-3",
    sticky="top",
    )


    return dbc.Container(
        [
            #  KPI row
            dbc.Row(
                [
                    navbar,
                    dbc.Col(kpi_card("Total Users", kpis["total_users"], "+2.5 % from yesterday", "bi bi-people-fill", dark_mode), md=3),
                    dbc.Col(kpi_card("Failed Logins", kpis["failed"], "Last 24 hours", "bi bi-exclamation-triangle-fill", dark_mode), md=3),
                    dbc.Col(kpi_card("Suspicious Activity", kpis["suspicious"], "Detected today", "bi bi-shield-fill", dark_mode), md=3),
                    dbc.Col(kpi_card("Active Sessions", kpis["active_sessions"], "Currently active", "bi bi-person-badge-fill", dark_mode), md=3),

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
        className="pt-4 " + ("bg-dark text-light" if dark_mode else ""),
    )

###############################################################################
# Overall layout  
###############################################################################
app.layout = dbc.Row(
    [
        dbc.Col(sidebar, width=2, className="bg-light vh-100 position-fixed"),
        dbc.Col(
            [

                dcc.Location(id="url"),
                dcc.Store(id="settings-store", storage_type="session"),
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

@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("settings-store", "data"),
)
def render_page(pathname: str, settings):

    vpn_mode = settings.get("vpn_mode", False) if settings else False
    allowed_country = settings.get("country", "Taiwan") if settings else "Taiwan"
    dark_mode = settings.get("dark_mode", False) if settings else False

    if pathname == "/alerts":
        return alerts_page.layout()
    elif pathname == "/upload":
        return upload_page.layout()
    elif pathname == "/settings":
        return settings_page.layout()
    return build_dashboard(vpn_mode=vpn_mode, allowed_country=allowed_country, dark_mode=dark_mode)



###############################################################################
#  Run server
###############################################################################
if __name__ == "__main__":
    app.run(debug=True, port=8080)
