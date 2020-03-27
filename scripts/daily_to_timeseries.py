import os
import argparse
import pandas as pd
from utils import read_dfs_in_folder


def main():
    args = process_args()
    aggregate_to_timeseries(args.folder)


def process_args():
    parser = argparse.ArgumentParser(
        description="Aggregate daily CSVs to timeseries CSVs in a folder"
    )
    parser.add_argument("folder")
    args = parser.parse_args()
    return args


def aggregate_to_timeseries(folder):

    # load all daily summary dataframes
    dfs = read_dfs_in_folder(folder)

    full_index = None
    for date, date_df in dfs.items():
        date_df.set_index(["County_Name", "State_Name"], inplace=True)
        if full_index is None:
            full_index = date_df.index
        else:
            full_index = full_index.union(date_df.index)

    # create template to be reused for different statistics
    base_columns = ["Latitude", "Longitude"]
    template_df = pd.DataFrame(
        columns=base_columns + list(dfs.keys()), index=full_index
    )

    # specify stats for timeseries
    stats = ["Confirmed", "Death"]
    stats_dfs = {}
    for stat_name in stats:
        stats_dfs[stat_name] = template_df.copy()

    for stat_name, stat_df in stats_dfs.items():
        for date, date_df in dfs.items():
            stat_df[date] = date_df[stat_name]
            stat_df[date] = stat_df[date].fillna(0).astype(int)
            stat_df["Latitude"].fillna(date_df["Latitude"], inplace=True)
            stat_df["Longitude"].fillna(date_df["Longitude"], inplace=True)

    # save timeseries to file
    for stat_name, stat_df in stats_dfs.items():
        filename = os.path.join(folder, "timeseries_{}.csv".format(stat_name.lower()))
        stat_df.to_csv(filename, float_format="%.7f")


if __name__ == "__main__":
    main()
