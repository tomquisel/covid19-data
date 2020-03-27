import os
import pandas as pd
import datetime as dt

# reuse custom method
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


# load all daily summary dataframes
dfs = read_dfs_in_folder("../data/csv")

# create template to be reused for different statistics
base_columns = ["County_Name", "State_Name", "Latitude", "Longitude"]
template_df = pd.DataFrame(
    columns= base_columns + list(dfs.keys())
)

# specify stats for timeseries
stats = ["Confirmed", "Death"]
stats_dfs = dict.fromkeys(stats)

for stat_name in stats_dfs.keys():
    stats_dfs[stat_name] = template_df.copy()

# iterate all daily summary dataframes and transfer to timeseries
for date, df in dfs.items():
    transfer_df = df[base_columns + stats].copy()
    for stat_name in stats_dfs.keys():
        transfer_df[date] = transfer_df[stat_name]
        # note: this creates one-row per state+county+day
        stats_dfs[stat_name] = stats_dfs[stat_name].append(
            transfer_df.drop(columns=stats)
        )

# iterate all timeseries and collapse all days into one state and county line
for stat_name in stats_dfs.keys():
    stats_dfs[stat_name] = (
        stats_dfs[stat_name]
        .groupby(["State_Name", "County_Name"])
        .first()
        .reset_index()
    )
    stats_dfs[stat_name] = stats_dfs[stat_name].sort_values(
        by=["State_Name", "County_Name"]
    )

    # swap column names so country is first
    colnames = stats_dfs[stat_name].columns.tolist()
    s, c = colnames.index("State_Name"), colnames.index("County_Name")
    colnames[c], colnames[s] = colnames[s], colnames[c]
    stats_dfs[stat_name] = stats_dfs[stat_name][colnames]

    # assume integer and cast for statistics (will need rework if float statistics used)
    for column in stats_dfs[stat_name].columns:
        if column not in base_columns:
            stats_dfs[stat_name][column] = stats_dfs[stat_name][column].astype("Int32")

# save timeseries to file
for stat_name, stat_df in stats_dfs.items():
    filename = "../data/csv/timeseries_{}.csv".format(stat_name.lower())
    stat_df.to_csv(filename, index=False)
