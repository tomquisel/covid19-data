"""The raw county-level data has some strange issues. Fix those up here"""
import sys
import json
import pandas as pd
import argparse
import os
import datetime as dt
from utils import read_dfs_in_folder


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

    do_basic_fixups(dfs)
    index_by_county(dfs)
    improve_lat_lons(dfs)
    fixup_diff_columns(dfs)

    write_csvs(folder, dfs)


def do_basic_fixups(dfs):
    for df in dfs.values():
        # fix some county names that change over time
        df.County_Name = df.County_Name.map(
            lambda c: {
                "Kauai County": "Kauai",
                "Maui County": "Maui",
                "Sheridan County": "Sheridan",
            }.get(c, c)
        )
        # There shouldn't be any duplicates, this is just a safeguard
        df.drop_duplicates(["County_Name", "State_Name"], inplace=True)
        # Deaths are sometimes reported with a string like "2+1".
        # Simplify to a single number (3)
        df.Death = (
            df.Death.astype(str).str.split("+").map(lambda l: sum([int(s) for s in l]))
        )
        # Recalculate fatality rate as a proper rate [0-1]
        df.Fatality_Rate = (df.Death / df.Confirmed).clip(0, 1)


def index_by_county(dfs):
    # switch to county + state index for all dfs
    for df in dfs.values():
        df.set_index(["County_Name", "State_Name"], inplace=True, verify_integrity=True)


def improve_lat_lons(dfs):
    """Early lat/lon values were flawed. Use the most recent values in all dfs"""
    newest_df = dfs[max(dfs.keys())]
    for df in dfs.values():
        fill_df = newest_df.reindex(df.index)
        if "Latitude" in df.columns:
            fill_df.Latitude.fillna(df.Latitude, inplace=True)
        if "Longitude" in df.columns:
            fill_df.Longitude.fillna(df.Longitude, inplace=True)
        df.Latitude = fill_df.Latitude
        df.Longitude = fill_df.Longitude


def fixup_diff_columns(dfs):
    """Compute the diff columns from today's & yesterday's values"""
    for date, df in dfs.items():
        yesterday = date - dt.timedelta(days=1)
        if yesterday in dfs:
            fixed_df = make_df_consistent_with_yesterday(df, dfs[yesterday])
        else:
            fixed_df = df.copy()
            # If there was no data yesterday, "New" cases isn't meaningful
            fixed_df["New"] = None
            fixed_df["New_Death"] = None
        dfs[date] = fixed_df


def make_df_consistent_with_yesterday(
    df, df_y, columns={"Confirmed": "New", "Death": "New_Death"}
):
    """This fixes the specified difference columns so that today = yesterday + New"""
    df = df.copy()
    df_y = df_y.reindex(df.index)
    for col, diff_col in columns.items():
        df[diff_col] = df[col] - df_y[col]
        # if a difference is missing, that's because it was 0 yesterday.
        # Backfill with today's value
        df[diff_col].fillna(df[col], inplace=True)
        df[diff_col] = df[diff_col].astype(int)
    return df


def write_csvs(folder, dfs):
    columns = [
        "Confirmed",
        "New",
        "Death",
        "New_Death",
        "Fatality_Rate",
        "Latitude",
        "Longitude",
        "Last_Update",
    ]
    for date, df in dfs.items():
        print(date, df)
        assert sorted(df.columns) == sorted(
            columns
        ), f"Unexpected or missing columns: {set(df.columns) ^ set(columns)}"
        df = df[columns]
        filename = os.path.join(folder, date.isoformat() + ".csv")
        df.to_csv(filename, float_format="%.7f")
        print(f"Fixed up {filename} : {df.Confirmed.sum()} cases")


if __name__ == "__main__":
    main()
