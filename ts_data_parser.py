import pandas as pd
import json

def data_parser(Market_id):
    csv_path = "db/market_" + str(Market_id) + "_history.csv"
    
    df = pd.read_csv(csv_path, header = None, names = ["timestamp", "raw_json"], sep = ";")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["parsed"] = df["raw_json"].apply(json.loads)
    
    df_extracted = pd.json_normalize(df["parsed"])
    df_extracted["timestamp"] = df["timestamp"]
    
    timeseries = df_extracted[["timestamp", "lastTradePrice", "bestBid", "bestAsk", "volume", "volume24hr", "liquidity"]].copy()
    
    timeseries["volume"] = pd.to_numeric(timeseries["volume"], errors="coerce")
    timeseries["liquidity"] = pd.to_numeric(timeseries["liquidity"], errors="coerce")
    
    return timeseries