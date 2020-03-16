"""The raw county-level data has some strange issues. Fix those up here"""
import sys
import json
import pandas as pd
import argparse
import os
import datetime as dt


def main():
    args = process_args()
    clean_folder(args.folder)


def process_args():
    parser = argparse.ArgumentParser(
        description="Fix up a folder of daily county-level data"
    )
    parser.add_argument("folder")
    args = parser.parse_args()
    return args


def clean_folder(folder):
    dfs = read_dfs_in_folder(folder)

    for date, df in dfs.items():
        # There shouldn't be any duplicates, this is just a safeguard
        df.drop_duplicates(["County_Name", "State_Name"], inplace=True)
        # Deaths are sometimes reported with a string like "2+1".
        # Simplify to a single number (3)
        df["Death"] = (
            df["Death"]
            .astype(str)
            .str.split("+")
            .map(lambda l: sum([int(s) for s in l]))
        )
        # Recalculate fatality rate as a proper rate [0-1]
        df["Fatality_Rate"] = df["Death"] / df["Confirmed"]

    for date, df in dfs.items():
        print(df)
        yesterday = date - dt.timedelta(days=1)
        if yesterday in dfs:
            fixed_df = make_df_consistent_with_yesterday(df, dfs[yesterday])
        else:
            fixed_df = df.copy()
            # "New" cases means nothing
            fixed_df["New"] = None
        filename = os.path.join(folder, date.isoformat() + ".csv")
        fixed_df.to_csv(filename, index=False)
        print("Fixed up", filename)


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


def make_df_consistent_with_yesterday(df, df_y):
    """This fixes the New column so that today = yesterday + New"""
    df = df.copy()
    df_y = df_y.copy()
    df.set_index(["County_Name", "State_Name"], inplace=True, verify_integrity=True)
    df_y.set_index(["County_Name", "State_Name"], inplace=True)
    df_y.reindex(df.index)
    df["New"] = df["Confirmed"] - df_y["Confirmed"]
    df.loc[df["New"].isnull(), "New"] = df["Confirmed"]
    df["New"] = df["New"].astype(int)
    return df.reset_index()


if __name__ == "__main__":
    main()

