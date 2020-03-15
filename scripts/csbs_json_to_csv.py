import sys
import json
import pandas as pd


def main():
    raw = sys.stdin.readlines()
    data = json.loads(" ".join(raw))
    df = json_to_df(data)
    df.to_csv(sys.stdout, index=False)


def json_to_df(data):
    county_dicts = []
    layers = data["operationalLayers"]
    layer = [l for l in layers if "cumulative cases" in l["title"].lower()][0]
    counties = layer["featureCollection"]["layers"][0]["featureSet"]["features"]
    for c in counties:
        c_attributes = c["attributes"]
        del c_attributes["ObjectId"]
        c_attributes["Last_Update"] = ":".join(
            c_attributes["Last_Update"].split(":")[1:]
        ).strip()
        county_dicts.append(c_attributes)
    df = pd.DataFrame.from_records(county_dicts)
    return df


if __name__ == "__main__":
    main()

