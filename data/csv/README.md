This folder contains daily US county COVID-19 data pulled from [CSBS.org's interactive map](https://www.csbs.org/information-covid-19-coronavirus).

### Fields

| Name | Description |
| County_Name | Name of the county |
| State_Name | State that the county is in |
| Confirmed | Number of confirmed COVID-19 cases |
| New | These numbers are smaller than I'd expect. Ignore for now |
| Deaths | Total deaths. Sometimes uses a strange A+B notation, probably indicating new death count. I'd just add those together.|
| Fatality_Rate | Deaths divided by Confirmed as a percentage |
| Latitude | Latitude of the county's centroid |
| Longitude | Longitude of the county's centroid |
| Last_Update | Time the row was last updated |
