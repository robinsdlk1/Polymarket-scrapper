import pandas as pd
import json

def data_parser(Market_id):
    csv_path = f"db/market_{Market_id}_history.csv"
    
    # Loading of the data
    df = pd.read_csv(csv_path, header = None, names = ["timestamp", "raw_json"], sep = ";")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # JSON auto parsing
    df["parsed"] = df["raw_json"].apply(json.loads)
    
    # Extraction of the json data
    df_extracted = pd.json_normalize(df["parsed"])
    
    # Timestamp addition
    df_extracted["timestamp"] = df["timestamp"]
    
    # Conversion of numeric columns (error without this)
    for col in df_extracted.columns:
        if col != "timestamp":
            try:
                df_extracted[col] = pd.to_numeric(df_extracted[col])
            except Exception:
                continue

    return df_extracted