import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
import datetime

from ts_data_parser_slug import data_parser
from daily_report import get_daily_report_table, export_daily_report

# -------- Parameters --------
MARKET_SLUG = "us-recession-in-2025"
REFRESH_INTERVAL_SECONDS = 300  # 5 minutes
DAILY_REPORT_PATH = f"db/market_{MARKET_SLUG}_daily_report.csv"

# -------- Global variable to track daily update --------
LAST_DAILY_UPDATE_DATE = None

# -------- Load Data --------
def load_data():
    df = data_parser(MARKET_SLUG)
    df = df.sort_values("timestamp")
    return df

# -------- Export Daily Report --------
def update_and_export_daily_report(df):
    export_daily_report(df, DAILY_REPORT_PATH)

# -------- Create Dash app --------
app = dash.Dash(__name__)
app.title = f"Polymarket Dashboard - {MARKET_SLUG}"

# -------- Layout --------
app.layout = html.Div(style={
    "fontFamily": "Segoe UI, sans-serif",
    "padding": "2rem",
    "background": "linear-gradient(145deg, #e4ebf5, #f9fbfe)",
    "minHeight": "100vh"
}, children=[
    html.H1(id="market-title", style={
        "textAlign": "center",
        "color": "#1d3557",
        "fontSize": "2rem",
        "marginBottom": "1.5rem",
        "textShadow": "0 1px 0 rgba(255,255,255,0.8)"
    }),

    dcc.Interval(id="interval-component", interval=REFRESH_INTERVAL_SECONDS * 1000, n_intervals=0),

    html.Div(id="refresh-timer", style={
        "textAlign": "center",
        "fontSize": "0.9rem",
        "color": "#4f4f4f",
        "marginBottom": "1.5rem"
    }),

    html.Div([
        html.Div([
            html.Label("Time Range", style={"fontWeight": "600", "marginBottom": "0.3rem", "display": "block"}),
            dcc.Dropdown(
                id="time-range-selector",
                options=[
                    {"label": "All", "value": "all"},
                    {"label": "7D", "value": "7d"},
                    {"label": "30D", "value": "30d"},
                    {"label": "90D", "value": "90d"},
                ],
                value="all",
                clearable=False,
                style={"width": "130px"}
            )
        ], style={"display": "inline-block", "marginRight": "2rem"}),

        html.Div([
            html.Label("Metrics", style={"fontWeight": "600", "marginBottom": "0.3rem", "display": "block"}),
            dcc.Dropdown(
                id="metric-selector",
                options=[],
                value=[],
                multi=True,
                placeholder="Select metrics...",
                style={"width": "400px"}
            )
        ], style={"display": "inline-block", "marginRight": "2rem"}),

        html.Div([
            dcc.Checklist(
                id='ma-checklist',
                options=[{'label': 'Show 7-Day MA', 'value': 'MA7'}],
                value=[],
                labelStyle={'display': 'inline-block', 'fontWeight': '500', 'marginTop': '1.8rem'}
            )
        ], style={'display': 'inline-block'})
    ], style={
        "backgroundColor": "rgba(255,255,255,0.85)",
        "padding": "1.2rem",
        "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
        "marginBottom": "2rem",
        "textAlign": "center",
        "transition": "box-shadow 0.3s ease-in-out"
    }),

    # GRAPHIQUE : pleine largeur
    html.Div(id="metrics-and-graphs", style={
        "width": "100%",
        "display": "block",
        "padding": "1rem",
        "backgroundColor": "rgba(255,255,255,0.9)",
        "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
        "marginBottom": "2rem",
        "transition": "box-shadow 0.3s ease-in-out"
    }),

    # Dernière ligne : market health, pricer, daily report
    html.Div([
        html.Div(id="market-health-table", style={
            "display": "inline-block",
            "width": "32%",
            "verticalAlign": "top",
            "marginRight": "2%",
            "backgroundColor": "rgba(255,255,255,0.9)",
            "padding": "1rem",
            "borderRadius": "12px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "transition": "box-shadow 0.3s ease-in-out"
        }),

        html.Div([
            html.H3("Option Expected Value", style={
                "textAlign": "center",
                "color": "#1d3557",
                "fontSize": "1.1rem",
                "marginTop": "0",
                "marginBottom": "1rem"
            }),
            html.Div([
                html.Label("Strike (0-1):", style={"marginRight": "0.5rem"}),
                dcc.Input(
                    id="strike-price-input",
                    type="number",
                    placeholder="0.5",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.01,
                    style={"width": "80px", "border": "1px solid #ccc", "padding": "4px", "borderRadius": "6px"}
                ),
            ], style={"textAlign": "center", "marginBottom": "1rem"}),

            html.Div([
                html.Div(id="call-option-price-output", style={
                    "fontWeight": "bold",
                    "fontSize": "1rem",
                    "minHeight": "1.1em",
                    "marginBottom": "0.3rem"
                }),
                html.Div(id="put-option-price-output", style={
                    "fontWeight": "bold",
                    "fontSize": "1rem",
                    "minHeight": "1.1em"
                }),
            ], style={
                "textAlign": "center",
                "backgroundColor": "#f4f6f8",
                "padding": "0.8rem",
                "borderRadius": "8px"
            })
        ], style={
            "display": "inline-block",
            "width": "32%",
            "verticalAlign": "top",
            "marginRight": "2%",
            "backgroundColor": "rgba(255,255,255,0.9)",
            "padding": "1rem",
            "borderRadius": "12px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "transition": "box-shadow 0.3s ease-in-out"
        }),

        html.Div(id="daily-report-table", style={
            "display": "inline-block",
            "width": "32%",
            "verticalAlign": "top",
            "backgroundColor": "rgba(255,255,255,0.9)",
            "padding": "1rem",
            "borderRadius": "12px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "transition": "box-shadow 0.3s ease-in-out"
        }),
    ])
])

# -------- Refresh Timer Callback --------
@app.callback(
    Output("refresh-timer", "children"),
    Input("interval-component", "n_intervals")
)
def update_timer(n):
    now = datetime.datetime.now(datetime.timezone.utc)
    next_refresh = now + datetime.timedelta(seconds=REFRESH_INTERVAL_SECONDS)
    return f"Next refresh scheduled at: {next_refresh.strftime('%Y-%m-%d %H:%M:%S UTC')}"

# -------- Main Update Callback --------
@app.callback(
    Output("market-title", "children"),
    Output("metric-selector", "options"),
    Output("metric-selector", "value"),
    Output("metrics-and-graphs", "children"),
    Output("market-health-table", "children"),
    Output("daily-report-table", "children"),
    Output("call-option-price-output", "children"),
    Output("put-option-price-output", "children"),
    Input("interval-component", "n_intervals"),
    Input("time-range-selector", "value"),
    Input("metric-selector", "value"),
    Input("strike-price-input", "value"),
    Input("ma-checklist", "value")
)
def update_layout(n, time_range, selected_metrics_input, strike_price, ma_checklist):
    global LAST_DAILY_UPDATE_DATE

    df = load_data()
    if df.empty:
        return (
            f"Polymarket Dashboard - {MARKET_SLUG} (No data)", [], [],
            html.Div("No data available."), html.Div(), html.Div(), "N/A", ""
        )

    if time_range != "all":
        days = int(time_range.replace("d", ""))
        cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
        df = df[df["timestamp"] >= cutoff]

    latest = df.iloc[-1]
    metrics_available = [
    col for col in df.columns
    if col.startswith("data_")
    and pd.api.types.is_numeric_dtype(df[col])
    and not df[col].dropna().nunique() <= 1  # ignore constant columns
    ]
    metrics_options = [{"label": col.replace("data_", ""), "value": col} for col in metrics_available]
    default_metrics = [col for col in ["data_lastTradePrice", "data_bestBid", "data_bestAsk"] if col in metrics_available]
    selected_metrics = [m for m in selected_metrics_input if m in metrics_available] if selected_metrics_input else default_metrics

    now = datetime.datetime.now(datetime.timezone.utc)
    if now.time() >= datetime.time(hour=19, minute=57):
        if LAST_DAILY_UPDATE_DATE != now.date():
            update_and_export_daily_report(df)
            LAST_DAILY_UPDATE_DATE = now.date()

    show_ma = 'MA7' in ma_checklist
    df_proc = df.copy()
    if show_ma:
        df_proc = df_proc.set_index("timestamp")
        for m in selected_metrics:
            df_proc[f"{m}_MA7"] = df_proc[m].rolling(window='7D').mean()
        df_proc = df_proc.reset_index()

    metrics_text = [html.P(f"{m.replace('data_', '')}: {latest[m]:.4f}" if pd.notna(latest[m]) else f"{m}: N/A") for m in selected_metrics]
    metrics_block = html.Div([
        html.H3("Current Metrics", style={"marginBottom": "1rem", "color": "#2c3e50"}),
        html.P(f"Last Update: {latest['timestamp']}")
    ] + metrics_text)

    traces = []
    for m in selected_metrics:
        traces.append(go.Scatter(x=df_proc["timestamp"], y=df_proc[m], mode="lines", name=m.replace("data_", "")))
        if show_ma and f"{m}_MA7" in df_proc:
            traces.append(go.Scatter(x=df_proc["timestamp"], y=df_proc[f"{m}_MA7"], mode="lines", name=f"{m.replace('data_', '')} MA7", line=dict(dash='dash')))

    graph = dcc.Graph(
        config={"displayModeBar": False},
        figure=go.Figure(
            data=traces,
            layout=go.Layout(
                margin=dict(l=40, r=30, t=20, b=40),
                plot_bgcolor="#ffffff",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    title=dict(text="Timestamp", font=dict(size=12, color="#4f4f4f")),
                    tickfont=dict(size=10, color="#4f4f4f"),
                    gridcolor="#e1e5eb",
                    linecolor="#d1d1d1",
                    zeroline=False
                ),
                yaxis=dict(
                    title=dict(text="Value", font=dict(size=12, color="#4f4f4f")),
                    tickfont=dict(size=10, color="#4f4f4f"),
                    gridcolor="#e1e5eb",
                    linecolor="#d1d1d1",
                    zeroline=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11)
                ),
                hovermode="x unified"
            )
        )
    )

    metrics_graphs_content = html.Div([metrics_block, graph])

    health_info = [(k.replace("data_", ""), str(latest.get(k, "N/A"))) for k in ["data_question", "data_startDate", "data_endDate", "data_resolutionSource", "data_restricted", "data_archived", "data_acceptingOrders", "data_closed", "data_active"]]
    health_table = html.Table([
        html.Tr([html.Th("Field"), html.Th("Value")])
    ] + [html.Tr([html.Td(k), html.Td(v)]) for k, v in health_info])

    daily_table = get_daily_report_table(df)

    call_output = "N/A"
    put_output = ""
    if strike_price is not None and 0 <= strike_price <= 1:
        P = latest.get("data_lastTradePrice", None)
        if P is not None:
            call_output = f"Call Exp. Value: ${P * max(0, 1 - strike_price):.4f}"
            put_output = f"Put Exp. Value: ${(1 - P) * max(0, strike_price):.4f}"

    return (
        f"Polymarket Market - {latest.get('data_question', MARKET_SLUG)}",
        metrics_options,
        selected_metrics,
        metrics_graphs_content,
        html.Div([html.H3("Market Health Info"), health_table]),
        html.Div(daily_table),
        call_output,
        put_output
    )

# -------- Run server --------
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
