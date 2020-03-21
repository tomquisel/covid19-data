#!/usr/bin/env bash
set -e

URL=https://facts.csbs.org/covid-19/covid19_county.csv
DATE=`date +"%Y-%m-%d"`

cd ..
curl $URL -o data/raw_scraped/$DATE.csv
cat data/raw_scraped/$DATE.csv | python3 scripts/csbs_csv_clean.py > data/csv/$DATE.csv
echo "CSV for $DATE written to data/csv/$DATE.csv"
python3 scripts/fixup_data_folder.py data/csv
