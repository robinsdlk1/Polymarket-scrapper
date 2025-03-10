import dash
from dash import html, dcc
import pandas as pd
from ts_data_parser import data_parser

MARKET_ID = 516710

df = data_parser(MARKET_ID)

# ------- Dernière observation --------
latest = df.sort_values("timestamp").iloc[-1]

# ------- Création de l'app Dash --------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(f"Polymarket - Market {MARKET_ID}"),
    html.Div([
        html.H3("Last Update:"),
        html.P(str(latest["timestamp"])),
    ]),
    html.Div([
        html.H3("Last Trade Price:"),
        html.P(f"{latest['lastTradePrice']:.3f}"),
    ]),
    html.Div([
        html.H3("Best Bid / Ask:"),
        html.P(f"{latest['bestBid']:.3f} / {latest['bestAsk']:.3f}"),
    ]),
    html.Div([
        html.H3("Volume:"),
        html.P(f"{latest['volume']:.2f}"),
    ]),
    html.Div([
        html.H3("24h Volume:"),
        html.P(f"{latest['volume24hr']:.2f}"),
    ]),
    html.Div([
        html.H3("Liquidity:"),
        html.P(f"{latest['liquidity']:.2f}"),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug = True)
