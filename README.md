## Overview

**SA RCR Map** is a project designed to visualize and interact with **South Australia Road Crash Reports (SA RCR)** (from 2019 to 2023). This tool allows users to view crash data on an interactive map to better understand traffic crash patterns, severity, and locations in South Australia.

The map visualizes road crash incidents, categorized by severity, including data such as property damage, injuries, fatalities, and specific crash types. This visualization is built using **Python**, **Folium**, and **GeoJSON** to provide an easy-to-use and accessible tool for crash data analysis.

The dataset used is provided by Data SA

## Screenshot
![rcr-map-full1](https://github.com/user-attachments/assets/5cb865e3-d068-4b9c-a092-87a6870cba55) ![rcr-map-marker1](https://github.com/user-attachments/assets/c80c1d94-da99-4eb4-b689-022603dce703)




## Features

- **Interactive Map**: View crash data on a zoomable and pannable map.
- **Markers and Clusters**: Displays crash incidents using clustered (grouped) markers
- **Readable Data Popups**: Each marker shows detailed crash information when clicked, including data on crash severity (CSE), location, and type.

## Data Format

The crash data is expected to be in **GeoJSON** format, with the following general structure (partial data shown):

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "UNIQUE_LOC": "unique_location_id",
        "TOTAL_CRASHES": 1,
        "CSE_PDO": 1,
        "CSE_INJ": 0,
        "CSE_FAT": 0,
        "CSE_SI": 0,
      }
    }
  ]
}
```

### Example of GeoJSON Attributes:
- UNIQUE_LOC: Unique location identifier.
- TOTAL_CRASHES: Total number of crashes at this location.
- CSE_PDO: Number of crashes with property damage only.
- CSE_INJ: Number of crashes with injuries.
- CSE_FAT: Number of fatalities.
- CSE_SI: Number of serious injuries.
- CTY_ properties*: Different **C**rash **Ty**pes (e.g., rear end, head-on, roll-over).
