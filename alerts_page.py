import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
from helper import get_recent_alerts  # reuse existing helper

def layout():
    alerts = get_recent_alerts(limit=20)
    return dbc.Container(
        [
            html.H4("Alerts"),
            dbc.ListGroup(
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
            ),
        ],
        fluid=True,
        className="pt-3",
    )

# page-specific callbacks can live down here
# @callback(...)
# def alert_filter(...):
#     ...
