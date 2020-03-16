import sys
import json
import pandas as pd


def main():
    raw_df = pd.read_csv(sys.stdin)
    df = clean_df(raw_df)
    df.to_csv(sys.stdout, index=False)


def clean_df(df):
    df.columns = [c.replace(" ", "_") for c in df.columns]
    return df


if __name__ == "__main__":
    main()

