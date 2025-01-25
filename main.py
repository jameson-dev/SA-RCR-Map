import json
import folium
from folium.plugins import MarkerCluster

# Specify GeoJSON file
geojson_file = "datasets/RoadCrashes_GDA2020.geojson"

# Read data from file
print(f"Collecting data from dataset: {geojson_file}")
with open(geojson_file, 'r') as file:
    geojson_data = json.load(file)

# Set map center coordinates
map_center = [-30.5344, 135.6300]
print(f"Setting map (center) location to {map_center[0]}, {map_center[1]}")

# Generate map
print("Generating map")
geojson_map = folium.Map(location=map_center, zoom_start=6)

# Create MarkerCluster object
marker_cluster = MarkerCluster().add_to(geojson_map)

# Add markers to cluster
for feature in geojson_data['features']:
    coords = feature['geometry']['coordinates']
    folium.Marker(location=[coords[1], coords[0]], popup=str(feature)).add_to(marker_cluster)


# Save GeoJSON map to HTML file
print("Saving generated HTML map")
map_file = 'rcr_interactive_map.html'

geojson_map.save(map_file)
print(f"Map generated: {map_file}")

