import pandas as pd
from datetime import datetime, timedelta, timezone

def compute_daily_report(df):
    df = df.copy()
    
    # Keep only the data form  the last 24hrs
    now = datetime.now(timezone.utc)
    df = df[df["timestamp"] >= now - timedelta(hours= 24)]

    # In ase there is no data.
    if df.empty:
        return pd.DataFrame(columns=[
            "date", "open_price", "close_price", "volatility",
            "best_bid_avg", "best_ask_avg", "volume_total",
            "liquidity_avg", "change_pct"
        ])

    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date").agg(
        open_price = ("data_lastTradePrice", "first"),
        close_price = ("data_lastTradePrice", "last"),
        volatility = ("data_lastTradePrice", "std"),
        best_bid_avg = ("data_bestBid", "mean"),
        best_ask_avg = ("data_bestAsk", "mean"),
        volume_total = ("data_volume", "last"),
        liquidity_avg = ("data_liquidity", "mean"),
    )

    daily["change_pct"] = ((daily["close_price"] - daily["open_price"]) / daily["open_price"]) * 100

    return daily.reset_index()

def export_daily_report(df, output_path):
    report = compute_daily_report(df)
    report.to_csv(output_path, index = False)
    return output_path

def get_daily_report_table(df):
    from dash import html
    report = compute_daily_report(df)

    header = [html.Tr([html.Th(col) for col in report.columns])]
    rows = [html.Tr([html.Td(round(row[col], 3) if isinstance(row[col], float) else row[col]) for col in report.columns]) for _, row in report.iterrows()]

    table = html.Div([
        html.H3("Daily Report Summary (Last 24h)", style={"textAlign": "center", "marginTop": "3rem", "color": "#2c3e50"}),
        html.Table(header + rows, style={
            "width": "95%",
            "margin": "0 auto",
            "borderCollapse": "collapse",
            "border": "1px solid #ccc",
            "backgroundColor": "#ffffff"
        })
    ])
    return table
