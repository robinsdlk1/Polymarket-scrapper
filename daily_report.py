import pandas as pd

def compute_daily_report(df):
    df = df.copy()
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date").agg(
        open_price = ("lastTradePrice", "first"),
        close_price = ("lastTradePrice", "last"),
        volatility = ("lastTradePrice", "std"),
        best_bid_avg = ("bestBid", "mean"),
        best_ask_avg = ("bestAsk", "mean"),
        volume_total = ("volume", "last"),
        liquidity_avg = ("liquidity", "mean"),
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
        html.H3("📅 Daily Report Summary", style={"textAlign": "center", "marginTop": "3rem", "color": "#2c3e50"}),
        html.Table(header + rows, style={
            "width": "95%",
            "margin": "0 auto",
            "borderCollapse": "collapse",
            "border": "1px solid #ccc",
            "backgroundColor": "#ffffff"
        })
    ])
    return table