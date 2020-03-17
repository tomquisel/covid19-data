# Daily county-level COVID-19 cases in US

This folder contains daily US county COVID-19 data pulled from [CSBS.org's interactive map](https://www.csbs.org/information-covid-19-coronavirus).

## Fields

| Name | Description |
|-|-|
| County_Name | Name of the county |
| State_Name | State that the county is in |
| Confirmed | Number of confirmed COVID-19 cases |
| New | New cases since the previous day |
| Deaths | Total deaths |
| Fatality_Rate | Deaths divided by Confirmed (0-1)|
| Latitude | Latitude of the county's centroid |
| Longitude | Longitude of the county's centroid |
| Last_Update | Time the row was last updated |

## Caveats

* There are a few catch-all non-county rows in some states. Examples include `Unassigned, Montana`, `Unknown, Idaho`, `Outside-Florida, Florida`, `Non-Utah resident, Utah`.
