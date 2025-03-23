import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
from ts_data_parser_slug import data_parser
from daily_report import get_daily_report_table, export_daily_report
import datetime

#--------------- TO BE REMOVED -----------------
import subprocess
#--------------- ^TO BE REMOVED^ -----------------


# -------- Parameters --------
MARKET_SLUG = "us-recession-in-2025"
REFRESH_INTERVAL_SECONDS = 60  # 5 minutes
DAILY_REPORT_PATH = f"db/market_{MARKET_SLUG}_daily_report.csv"

# -------- Global variable to track daily update --------
LAST_DAILY_UPDATE_DATE = None

# -------- Load data --------
def load_data():
    df = data_parser(MARKET_SLUG)
    df = df.sort_values("timestamp")
    return df

# -------- Export Daily Report --------
def update_and_export_daily_report(df):
    export_daily_report(df, DAILY_REPORT_PATH)

# -------- Initial load --------
df = load_data()

# -------- List of relevant numeric metrics for selection --------
RELEVANT_METRICS = ["data_lastTradePrice", "data_bestBid", "data_bestAsk", "data_volume", "data_volume24hr", "data_liquidity", "data_umaBond", "data_umaReward", "data_competitive", "data_rewardsMinSize", "data_rewardsMaxSpread", "data_spread", "data_oneDayPriceChange"]

# -------- Create Dash app --------
app = dash.Dash(__name__)
app.title = f"Polymarket Dashboard - {df['data_question'].iloc[0]}"

# -------- Layout --------
app.layout = html.Div(style={"fontFamily": "Arial", "padding": "2rem", "backgroundColor": "#f9f9f9"}, children=[
    html.H1(f"Polymarket Market - {df['data_question'].iloc[0]}", style={"textAlign": "center", "color": "#333"}),

    dcc.Interval(
        id="interval-component",
        interval=REFRESH_INTERVAL_SECONDS * 1000,
        n_intervals=0
    ),

    html.Div(id="refresh-timer", style={"textAlign": "center", "fontSize": "1rem", "color": "#666", "marginBottom": "1rem"}),

    html.Div([
        html.Label("Select Time Range:", style={"fontWeight": "bold", "marginRight": "1rem"}),
        dcc.Dropdown(
            id="time-range-selector",
            options=[
                {"label": "All Data", "value": "all"},
                {"label": "Last 7 Days", "value": "7d"},
                {"label": "Last 30 Days", "value": "30d"},
                {"label": "Last 90 Days", "value": "90d"},
            ],
            value="all",
            style={"width": "300px", "marginBottom": "2rem"}
        )
    ], style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Metrics to Display:", style={"fontWeight": "bold", "marginRight": "1rem"}),
        dcc.Dropdown(
            id="metric-selector",
            options=[{"label": col.replace("data_", ""), "value": col} for col in RELEVANT_METRICS if col in df.columns],
            value=[col for col in ["data_lastTradePrice", "data_bestBid", "data_bestAsk"] if col in df.columns],
            multi=True,
            style={"width": "500px", "marginBottom": "2rem"}
        )
    ], style={"textAlign": "center"}),

    html.Div(id="metrics-and-graphs"),
    html.Div(id="market-health-table", style={"marginTop": "3rem"}),
    html.Div(id="daily-report-table", style={"marginTop": "3rem"})
])

from dash.dependencies import Input, Output

@app.callback(
    Output("metrics-and-graphs", "children"),
    Output("market-health-table", "children"),
    Output("daily-report-table", "children"),
    Input("interval-component", "n_intervals"),
    Input("time-range-selector", "value"),
    Input("metric-selector", "value")
)
def update_layout(n, time_range, selected_metrics):
    global LAST_DAILY_UPDATE_DATE

    #---------------  TO BE REMOVED  -----------------
    subprocess.run(["bash", "polymkt_id_data_scrapper.sh", MARKET_SLUG])
    #--------------- ^TO BE REMOVED^ ---------------

    df = load_data()
    now = datetime.datetime.now(datetime.timezone.utc)
    current_time_utc = now.time()
    current_date = now.date()
    scheduled_time = datetime.time(hour=19, minute=0)

    if current_time_utc >= scheduled_time and (LAST_DAILY_UPDATE_DATE is None or LAST_DAILY_UPDATE_DATE != current_date):
        update_and_export_daily_report(df)
        LAST_DAILY_UPDATE_DATE = current_date

    if time_range != "all":
        days = int(time_range.replace("d", ""))
        df = df[df["timestamp"] >= (pd.Timestamp.utcnow() - pd.Timedelta(days=days))]

    latest = df.iloc[-1]

    metrics_block = html.Div([
        html.H3("Current Metrics", style={"marginBottom": "1rem", "color": "#2c3e50"}),
        html.P(f"Last Update: {latest['timestamp']}", style={"marginBottom": "0.5rem"}),
    ] + [
        html.P(f"{metric.replace('data_', '')}: {latest[metric]}" if metric in latest else f"{metric.replace('data_', '')}: N/A")
        for metric in selected_metrics
    ], style={
        "width": "30%",
        "display": "inline-block",
        "verticalAlign": "top",
        "padding": "1rem",
        "backgroundColor": "#ffffff",
        "borderRadius": "10px",
        "boxShadow": "0px 2px 8px rgba(0, 0, 0, 0.1)"
    })

    time_series_block = html.Div([
        html.H3("Selected Metrics Time Series", style={"color": "#2c3e50"}),
        dcc.Graph(
            figure={
                "data": [
                    go.Scatter(x=df["timestamp"], y=df[metric], mode="lines", name=metric.replace("data_", ""))
                    for metric in selected_metrics if metric in df.columns
                ],
                "layout": go.Layout(
                    xaxis={"title": "Timestamp"},
                    yaxis={"title": "Value"},
                    margin={"l": 40, "r": 10, "t": 20, "b": 40},
                    hovermode="closest",
                    plot_bgcolor="#f4f4f4",
                    paper_bgcolor="#f4f4f4"
                )
            }
        )
    ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top", "paddingLeft": "2rem"})

    health_info = [
        ("Market Question", latest.get("data_question", "N/A")),
        ("Condition ID", latest.get("data_conditionId", "N/A")),
        ("Start Date", latest.get("data_startDate", "N/A")),
        ("End Date", latest.get("data_endDate", "N/A")),
        ("Resolution Source", latest.get("data_resolutionSource", "N/A")),
        ("Restricted", str(latest.get("data_restricted", "N/A"))),
        ("Archived", str(latest.get("data_archived", "N/A"))),
        ("Accepting Orders", str(latest.get("data_acceptingOrders", "N/A"))),
        ("Closed", str(latest.get("data_closed", "N/A"))),
        ("Active", str(latest.get("data_active", "N/A")))
    ]

    health_table = html.Div([
        html.H3("Market Health Info", style={"textAlign": "center", "color": "#2c3e50", "marginTop": "2rem"}),
        html.Table([
            html.Tr([html.Th("Field"), html.Th("Value")])
        ] + [
            html.Tr([html.Td(k), html.Td(v)]) for k, v in health_info
        ], style={"width": "80%", "margin": "0 auto", "borderCollapse": "collapse", "border": "1px solid #ccc"})
    ])

    daily_table = get_daily_report_table(df)

    return html.Div([metrics_block, time_series_block]), health_table, daily_table

@app.callback(
    Output("refresh-timer", "children"),
    Input("interval-component", "n_intervals")
)
def update_timer(n):
    now = datetime.datetime.now(datetime.timezone.utc)
    next_refresh = now + datetime.timedelta(seconds=REFRESH_INTERVAL_SECONDS)
    return f"Next refresh scheduled at: {next_refresh.strftime('%Y-%m-%d %H:%M:%S UTC')}"

# -------- Run server --------
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)