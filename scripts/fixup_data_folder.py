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

    do_basic_fixups(dfs)
    index_by_county(dfs)
    improve_lat_lons(dfs)
    fixup_new_column(dfs)

    write_csvs(folder, dfs)


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


def fixup_new_column(dfs):
    """Compute the "New" column from today's & yesterday's Confirmed values"""
    for date, df in dfs.items():
        yesterday = date - dt.timedelta(days=1)
        if yesterday in dfs:
            fixed_df = make_df_consistent_with_yesterday(df, dfs[yesterday])
        else:
            fixed_df = df.copy()
            # If there was no data yesterday, "New" cases isn't meaningful
            fixed_df.New = None
        dfs[date] = fixed_df


def make_df_consistent_with_yesterday(df, df_y):
    """This fixes the New column so that today = yesterday + New"""
    df = df.copy()
    df_y = df_y.copy()
    df_y.reindex(df.index)
    df.New = df.Confirmed - df_y.Confirmed
    df.loc[df.New.isnull(), "New"] = df.Confirmed
    df.New = df.New.astype(int)
    return df


def write_csvs(folder, dfs):
    for date, df in dfs.items():
        filename = os.path.join(folder, date.isoformat() + ".csv")
        df.to_csv(filename, float_format="%.7f")
        print(f"Fixed up {filename} : {df.Confirmed.sum()} cases")


if __name__ == "__main__":
    main()

