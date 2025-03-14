import dash
from dash import html
import pandas as pd
from ts_data_parser import data_parser
from daily_report import get_daily_report_table

# -------- Parameters --------
MARKET_ID = 516710

# -------- Load Data --------
df = data_parser(MARKET_ID)
df = df.sort_values("timestamp")

# -------- Create Dash App --------
app = dash.Dash(__name__)
app.title = "Test Daily Report Table"

# -------- Layout --------
app.layout = html.Div([
    html.H1("✅ Test Daily Report Table", style={"textAlign": "center"}),
    get_daily_report_table(df)
])

# -------- Run --------
if __name__ == '__main__':
    app.run_server(debug=True)
