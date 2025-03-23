import pandas as pd

def data_parser(market_slug):
    csv_path = f"db/csv/market_{market_slug}_flatdata.csv"
    
    # Loading of the data
    df = pd.read_csv(csv_path, sep = ";")
    
    # Conversion to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Conversion of numeric columns (error without this)
    for col in df.columns:
        if col != "timestamp":
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                continue

    return df