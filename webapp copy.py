import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
from ts_data_parser import data_parser

# -------- Parameters --------
MARKET_ID = 516710
REFRESH_INTERVAL_SECONDS = 60  # Vous pouvez modifier cette valeur

# -------- Load data --------
def load_data():
    df = data_parser(MARKET_ID)
    df = df.sort_values("timestamp")
    return df

df = load_data()

# -------- Create Dash app --------
app = dash.Dash(__name__)
app.title = f"Polymarket Dashboard - Market {MARKET_ID}"

# -------- Layout --------
app.layout = html.Div(style={"fontFamily": "Arial", "padding": "2rem", "backgroundColor": "#f9f9f9"}, children=[
    html.H1(f"Polymarket Market #{MARKET_ID}", style={"textAlign": "center", "color": "#333"}),

    dcc.Interval(
        id="interval-component",
        interval = REFRESH_INTERVAL_SECONDS * 1000,
        n_intervals=0
    ),

    html.Div(id="refresh-timer", style={"textAlign": "center", "fontSize": "1rem", "color": "#666", "marginBottom": "1rem"}),
    html.Div(id="metrics-and-graphs")
])

# -------- Callback layout update --------
from dash.dependencies import Input, Output, State
import datetime

@app.callback(
    Output("metrics-and-graphs", "children"),
    Input("interval-component", "n_intervals")
)
def update_layout(n):
    df = load_data()
    latest = df.iloc[-1]

    return html.Div([
        html.Div([
            html.Div([
                html.H3("Current Metrics", style={"marginBottom": "1rem", "color": "#2c3e50"}),
                html.P(f"Last Update: {latest['timestamp']}", style={"marginBottom": "0.5rem"}),
                html.P(f"💰 Last Trade Price: {latest['lastTradePrice']:.3f}"),
                html.P(f"📈 Best Bid: {latest['bestBid']:.3f}"),
                html.P(f"📉 Best Ask: {latest['bestAsk']:.3f}"),
                html.P(f"📊 Volume: {latest['volume']:,}"),
                html.P(f"🔄 24h Volume: {latest['volume24hr']:,}"),
                html.P(f"💧 Liquidity: {latest['liquidity']:,}"),
            ], style={
                "width": "30%",
                "display": "inline-block",
                "verticalAlign": "top",
                "padding": "1rem",
                "backgroundColor": "#ffffff",
                "borderRadius": "10px",
                "boxShadow": "0px 2px 8px rgba(0, 0, 0, 0.1)",
            })
        ]),

        html.Div([
            html.Div([
                html.H3("Price Time Series", style={"color": "#2c3e50"}),
                dcc.Graph(
                    figure={
                        "data": [
                            go.Scatter(x=df["timestamp"], y=df["lastTradePrice"], mode="lines", name="Last Trade Price"),
                            go.Scatter(x=df["timestamp"], y=df["bestBid"], mode="lines", name="Best Bid"),
                            go.Scatter(x=df["timestamp"], y=df["bestAsk"], mode="lines", name="Best Ask"),
                        ],
                        "layout": go.Layout(
                            xaxis={"title": "Timestamp"},
                            yaxis={"title": "Price"},
                            margin={"l": 40, "r": 10, "t": 20, "b": 40},
                            hovermode="closest",
                            plot_bgcolor="#f4f4f4",
                            paper_bgcolor="#f4f4f4"
                        )
                    }
                )
            ], style={"marginTop": "2rem"}),

            html.Div([
                html.H3("Volume and Liquidity Time Series", style={"color": "#2c3e50"}),
                dcc.Graph(
                    figure={
                        "data": [
                            go.Scatter(x=df["timestamp"], y=df["volume"], mode="lines", name="Volume"),
                            go.Scatter(x=df["timestamp"], y=df["volume24hr"], mode="lines", name="24h Volume"),
                            go.Scatter(x=df["timestamp"], y=df["liquidity"], mode="lines", name="Liquidity"),
                        ],
                        "layout": go.Layout(
                            xaxis={"title": "Timestamp"},
                            yaxis={"title": "Amount"},
                            margin={"l": 40, "r": 10, "t": 20, "b": 40},
                            hovermode="closest",
                            plot_bgcolor="#f4f4f4",
                            paper_bgcolor="#f4f4f4"
                        )
                    }
                )
            ], style={"marginTop": "2rem"})
        ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top", "paddingLeft": "2rem"})
    ])

@app.callback(
    Output("refresh-timer", "children"),
    Input("interval-component", "n_intervals")
)
def update_timer(n):
    now = datetime.datetime.utcnow()
    next_refresh = now + datetime.timedelta(seconds=REFRESH_INTERVAL_SECONDS)
    return f"⏳ Next refresh scheduled at: {next_refresh.strftime('%Y-%m-%d %H:%M:%S UTC')}"

# -------- Run server --------
if __name__ == '__main__':
    app.run_server(debug=True)
