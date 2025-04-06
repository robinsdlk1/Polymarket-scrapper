import pandas as pd
import glob
import os

# The data scrapping isn't consistant and some indexes dissapear over time. We hope that the columnns aren't relevant and do the intersection of the collumns in common.


def data_parser(market_slug):
    folder = f"db/csv/snapshots/{market_slug}"
    if not os.path.exists(folder):
        return pd.DataFrame()
    
    files = sorted(glob.glob(os.path.join(folder, "flatdata_*.csv")))
    if not files:
        return pd.DataFrame()

    dfs = []
    common_cols = None

    for file in files:
        try:
            df = pd.read_csv(file, sep=";")
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            dfs.append(df)

            if common_cols is None:
                common_cols = set(df.columns)
            else:
                common_cols &= set(df.columns)
        except Exception:
            continue

    if not dfs or not common_cols:
        return pd.DataFrame()

    trimmed_dfs = [df[list(common_cols)].copy() for df in dfs]

    return pd.concat(trimmed_dfs, ignore_index=True)