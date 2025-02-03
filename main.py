import json
import os
import re

import folium
from geopandas import gpd
from shapely.geometry import Point
from folium.plugins import MarkerCluster

# Specify GeoJSON file
rcr_geojson_file = "datasets/RoadCrashes_GDA2020.geojson"
suburbs_geojson_file = "datasets/Suburbs_GDA2020.geojson"

# Read suburbs data as GeoDataFrame
print(f"Collecting suburbs data from dataset: {suburbs_geojson_file}")
suburbs_gdf = gpd.read_file(suburbs_geojson_file)

# Simplify geometry (Reduce HTML file size)
print("Simplifying Suburbs GeoJSON")
suburbs_gdf['geometry'] = suburbs_gdf['geometry'].simplify(tolerance=0.001)

suburbs_gdf.to_file('datasets/simplified_suburbs.geojson', driver='GeoJSON')

suburbs_geojson_file = "datasets/simplified_suburbs.geojson"

# Read road crash data
print(f"Collecting road crash data from dataset: {rcr_geojson_file}")
with open(rcr_geojson_file, 'r') as file:
    geojson_data = json.load(file)

# Convert road crash data to GeoDataFrame
print("Converting road crash data to GeoDataFrame")
crashes = []
for feature in geojson_data['features']:
    coords = feature['geometry']['coordinates']
    crashes.append({
        "geometry": Point(coords),
        "TOTAL_CRASHES": feature['properties']['TOTAL_CRASHES']
    })

# Collect GeoDataFrame for crashes using CRS data (Coordinate Reference System) for lat/long
crash_gdf = gpd.GeoDataFrame(crashes, crs="EPSG:4326")

# Spatial join to map crashes to suburbs
print("Performing spatial join")
crash_to_suburb = gpd.sjoin(crash_gdf, suburbs_gdf, how="left", predicate="intersects")

# Aggregate crash counts by suburb
print("Aggregating crash counts by suburb")
suburb_crash_data = crash_to_suburb.groupby("suburb", as_index=False)["TOTAL_CRASHES"].sum()

# Set map center coordinates
map_center = [-30.5344, 135.6300]
print(f"Setting map (center) location to {map_center[0]}, {map_center[1]}")

# Generate map
print("Generating map")
geojson_map = folium.Map(
    location=map_center,
    zoom_start=6
)

crash_types = {
    "CSE_FAT": "Fatal Crashes",
    "CSE_SI": "Serious Injuries",
    "CSE_INJ": "Minor Injuries",
    "CSE_PDO": "Property Damage Only",
    "CTY_REAR_END": "Rear End",
    "CTY_HIT_FIXED_OBJECT": "Hit Fixed Object",
    "CTY_SIDE_SWIPE": "Side Swipe",
    "CTY_RIGHT_ANGLE": "Right Angle",
    "CTY_HEAD_ON": "Head On",
    "CTY_HIT_PEDESTRIAN": "Hit Pedestrian",
    "CTY_ROLL_OVER": "Roll Over",
    "CTY_RIGHT_TURN": "Right Turn",
    "CTY_HIT_PARKED_VEHILE": "Hit Parked Vehicle",
    "CTY_HIT_ANIMAL": "Hit Animal",
    "CTY_HIT_OBJECT_ON_ROAD": "Hit Object on Road",
    "CTY_LEFT_ROAD_OC": "Left Road",
    "CTY_OTHER": "Other"
}

crash_clusters = {}

for key, name in crash_types.items():
    feature_group = folium.FeatureGroup(name=name, show=False)
    cluster = MarkerCluster(name=name, show=True).add_to(feature_group)
    geojson_map.add_child(feature_group)
    crash_clusters[key] = cluster

# Add markers for specific crash types
# Create an empty GeoJSON structure
geojson_markers = {
    "type": "FeatureCollection",
    "features": []
}

# Loop through crash data and save it as GeoJSON
for feature in geojson_data['features']:
    coords = feature['geometry']['coordinates']
    properties = feature['properties']

    geojson_markers["features"].append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coords
        },
        "properties": properties
    })

# Save markers to an external GeoJSON file
output_file = "datasets/markers.geojson"
with open(output_file, "w") as f:
    json.dump(geojson_markers, f)

print(f"Markers saved externally to {output_file}")

# Add choropleth layer for suburb crash data
print("Adding choropleth layer")
folium.Choropleth(
    geo_data=suburbs_geojson_file,
    name='Choropleth',
    data=suburb_crash_data,
    columns=['suburb', 'TOTAL_CRASHES'],
    key_on='feature.properties.suburb',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    threshold_scale=[0, 10, 25, 50, 80, 150, 300, 600, 800, 1000, 1500, 2000, suburb_crash_data["TOTAL_CRASHES"].max()],
    legend_name='Total Crashes by Suburb',
).add_to(geojson_map)

# Save the map to an HTML file
map_file = 'index.html'
print(f"Saving generated HTML map to {map_file}")

geojson_map.save(map_file)

file_size = os.path.getsize(map_file) / 1024  # Convert bytes to KB
print(f"Map generated: {map_file} ({file_size:.2f} KB)")

# JavaScript code to load markers externally
external_marker_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    fetch("datasets/markers.geojson")
        .then(response => response.json())
        .then(data => {
            let featureGroups = {
                "Fatal Crashes": L.markerClusterGroup(),
                "Serious Injuries": L.markerClusterGroup(),
                "Minor Injuries": L.markerClusterGroup(),
                "Property Damage": L.markerClusterGroup(),
                "Rear End": L.markerClusterGroup(),
                "Hit Fixed Object": L.markerClusterGroup(),
                "Side Swipe": L.markerClusterGroup(),
                "Right Angle": L.markerClusterGroup(),
                "Head On": L.markerClusterGroup(),
                "Hit Pedestrian": L.markerClusterGroup(),
                "Roll Over": L.markerClusterGroup(),
                "Right Turn": L.markerClusterGroup(),
                "Hit Parked Vehicle": L.markerClusterGroup(),
                "Hit Animal": L.markerClusterGroup(),
                "Hit Object on Road": L.markerClusterGroup(),
                "Left Road": L.markerClusterGroup(),
                "Other (unknown)": L.markerClusterGroup()
            };

            L.geoJSON(data, {
                pointToLayer: function(feature, latlng) {
                    return L.marker(latlng); // Convert GeoJSON points to markers
                },
                onEachFeature: function(feature, layer) {
                    let popupContent = `<h5><b>Crash Type</b></h5>`;
                    for (const [key, value] of Object.entries(feature.properties)) {
                        popupContent += `<span><b>${key}:</b> ${value}<br></span>`;
                    }
                    layer.bindPopup(popupContent);

                    // Use an array to collect all matching groups
                    let assignedGroups = [];

                    // Check each condition and add the marker to the corresponding group
                    if (feature.properties["CSE_FAT"] > 0) {
                        assignedGroups.push(featureGroups["Fatal Crashes"]);
                    }
                    if (feature.properties["CSE_SI"] > 0) {
                        assignedGroups.push(featureGroups["Serious Injuries"]);
                    }
                    if (feature.properties["CSE_INJ"] > 0) {
                        assignedGroups.push(featureGroups["Minor Injuries"]);
                    }
                    if (feature.properties["CSE_PDO"] > 0) {
                        assignedGroups.push(featureGroups["Property Damage"]);
                    }
                    if (feature.properties["CTY_REAR_END"] > 0) {
                        assignedGroups.push(featureGroups["Rear End"]);
                    }
                    if (feature.properties["CTY_HIT_FIXED_OBJECT"] > 0) {
                        assignedGroups.push(featureGroups["Hit Fixed Object"]);
                    }
                    if (feature.properties["CTY_SIDE_SWIPE"] > 0) {
                        assignedGroups.push(featureGroups["Side Swipe"]);
                    }
                    if (feature.properties["CTY_RIGHT_ANGLE"] > 0) {
                        assignedGroups.push(featureGroups["Right Angle"]);
                    }
                    if (feature.properties["CTY_HEAD_ON"] > 0) {
                        assignedGroups.push(featureGroups["Head On"]);
                    }
                    if (feature.properties["CTY_HIT_PEDESTRIAN"] > 0) {
                        assignedGroups.push(featureGroups["Hit Pedestrian"]);
                    }
                    if (feature.properties["CTY_ROLL_OVER"] > 0) {
                        assignedGroups.push(featureGroups["Roll Over"]);
                    }
                    if (feature.properties["CTY_RIGHT_TURN"] > 0) {
                        assignedGroups.push(featureGroups["Right Turn"]);
                    }
                    if (feature.properties["CTY_HIT_PARKED_VEHICLE"] > 0) {
                        assignedGroups.push(featureGroups["Hit Parked Vehicle"]);
                    }
                    if (feature.properties["CTY_HIT_ANIMAL"] > 0) {
                        assignedGroups.push(featureGroups["Hit Animal"]);
                    }
                    if (feature.properties["CTY_HIT_OBJECT_ON_ROAD"] > 0) {
                        assignedGroups.push(featureGroups["Hit Object on Road"]);
                    }
                    if (feature.properties["CTY_LEFT_ROAD_OC"] > 0) {
                        assignedGroups.push(featureGroups["Left Road"]);
                    }
                    if (feature.properties["CTY_OTHER"] > 0) {
                        assignedGroups.push(featureGroups["Other (unknown)"]);
                    }

                    // Add the marker to all assigned groups
                    assignedGroups.forEach(group => {
                        group.addLayer(layer);
                    });
                }
            });

            // Add the feature groups to the layer control
            let layerControl = L.control.layers(null, featureGroups, { collapsed: true }).addTo(map);
        })
        .catch(error => console.error("Error loading markers:", error));
});
</script>
"""

# Append the script to the HTML file
with open("index.html", "a") as f:
    f.write(external_marker_script)

print("Added external marker script to index.html")

# Simplify map var name
# Read the generated index.html file
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Find the dynamically generated map variable
map_var_match = re.search(r"var (map_[a-f0-9]+) = L\.map\(", html_content)

if map_var_match:
    old_map_var = map_var_match.group(1)  # Extract the generated map variable name
    print(f"Replacing {old_map_var} with 'map'...")

    # Replace all occurrences of the generated name with 'map'
    html_content = html_content.replace(old_map_var, "map")

    # Write the updated content back to index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Updated index.html to use 'map' as the variable name.")
else:
    print("Map variable not found. No changes made.")
