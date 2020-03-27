import os
import datetime as dt
import pandas as pd


def read_dfs_in_folder(folder):
    """Read all csvs in folder named after dates"""
    dfs = {}
    for f in sorted(os.listdir(folder)):
        try:
            df_date = dt.date.fromisoformat(f.split(".")[0])
        except ValueError:
            continue
        dfs[df_date] = pd.read_csv(os.path.join(folder, f))
    return dfs
