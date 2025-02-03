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
print("Storing GeoDataFrame data using CRS (Coordinate Reference System data for lat/long conversion")
crash_gdf = gpd.GeoDataFrame(crashes, crs="EPSG:4326")

# Spatial join to map crashes to suburbs
print("Performing spatial join (Crashes to Suburbs)")
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
    "CTY_OTHER": "Other (unknown)"
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

# Save markers to an external GeoJSON file

output_file = "datasets/markers.geojson"
print(f"Saving markers externally to {output_file}")
with open(output_file, "w") as f:
    json.dump(geojson_markers, f)

cluster_data = {
    "Fatal Crashes": [],
    "Serious Injuries": [],
    "Minor Injuries": [],
    "Property Damage Only": [],
    "Rear End": [],
    "Hit Fixed Object": [],
    "Side Swipe": [],
    "Right Angle": [],
    "Head On": [],
    "Hit Pedestrian": [],
    "Roll Over": [],
    "Right Turn": [],
    "Hit Parked Vehicle": [],
    "Hit Animal": [],
    "Hit Object on Road": [],
    "Left Road": [],
    "Other (unknown)": []
}

# Loop through crash data and assign markers to their respective clusters
print("Assigning markers to clusters")
for feature in geojson_data['features']:
    coords = feature['geometry']['coordinates']
    properties = feature['properties']
    crash_types_found = []  # List to store all matching crash types

    # Iterate through each crash type
    for key, name in crash_types.items():
        value = properties.get(key)
        if value and value > 0:
            print(f"Found crash type {name} for feature with {key}: {value}")
            crash_types_found.append(name)

    # If there are any matching crash types, add the feature to those clusters
    if crash_types_found:
        for crash_type in crash_types_found:
            print(f"Feature with coordinates {coords} added to crash type {crash_type}")
            cluster_data[crash_type].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "properties": properties
            })

            # Also add the feature to geojson_markers
            geojson_markers["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "properties": {
                    **properties,
                    "crash_type": crash_type  # Add the crash_type here
                }
            })
    else:
        print(f"Warning: No valid crash type found for feature with properties {properties}")


# Save the markers to a file after collecting them
output_file = "datasets/markers.geojson"
with open(output_file, "w") as f:
    json.dump(geojson_markers, f)

print(f"Markers saved externally to {output_file}")

# Save cluster data to a JSON file
cluster_file = "datasets/cluster_data.json"
with open(cluster_file, "w") as f:
    json.dump(cluster_data, f)

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
                "Fatal Crashes": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Serious Injuries": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Minor Injuries": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Property Damage Only": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Rear End": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Hit Fixed Object": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Side Swipe": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Right Angle": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Head On": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Hit Pedestrian": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Roll Over": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Right Turn": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Hit Parked Vehicle": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Hit Animal": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Hit Object on Road": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Left Road": L.markerClusterGroup({ maxClusterRadius: 50 }),
                "Other (unknown)": L.markerClusterGroup({ maxClusterRadius: 50 })
            };
            console.log("Feature Groups:", featureGroups);  // Log to verify all feature groups are present
            
            L.geoJSON(data, {
                pointToLayer: function(feature, latlng) {
                    return L.marker(latlng);
                },
                onEachFeature: function(feature, layer) {
                    let popupContent = `<h5><b>Crash Type</b></h5>`;
                    for (const [key, value] of Object.entries(feature.properties)) {
                        popupContent += `<span><b>${key}:</b> ${value}<br></span>`;
                    }
                    layer.bindPopup(popupContent);
                
                    // Assign the marker to the appropriate cluster
                    let crashType = feature.properties.crash_type; // This assumes `crash_type` is defined
                    if (featureGroups[crashType]) {
                        featureGroups[crashType].addLayer(layer);
                    }
                }
            });
            
            // Add all feature groups to the map
            for (let groupName in featureGroups) {
                map.addLayer(featureGroups[groupName]);
            }

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
