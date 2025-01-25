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
    properties = feature['properties']

    # Create formatted (human-readable) popup
    popup_content = f"""
    <h4><b>Crash Information</b></h4>
    <p><b>Unique Location:</b> {properties['UNIQUE_LOC']}</p>
    <p><b>Total Crashes:</b> {properties['TOTAL_CRASHES']}</p>
    <p><b>CSE PDO (Property Damage Only):</b> {properties['CSE_PDO']}</p>
    <p><b>CSE Injuries:</b> {properties['CSE_INJ']}</p>
    <p><b>CSE Fatalities:</b> {properties['CSE_FAT']}</p>
    <p><b>CSE Serious Injuries:</b> {properties['CSE_SI']}</p>
    <p><b>Total Casualties:</b> {properties['TOTAL_CASUALTIES']}</p>
    <p><b>Total Fatalities:</b> {properties['TOTAL_FATALITIES']}</p>
    <p><b>Total Serious Injuries:</b> {properties['TOTAL_SERIOUS_INJURIES']}</p>
    <p><b>Crash Types:</b></p>
    <ul>
        <li><b>Rear End:</b> {properties['CTY_REAR_END']}</li>
        <li><b>Hit Fixed Object:</b> {properties['CTY_HIT_FIXED_OBJECT']}</li>
        <li><b>Side Swipe:</b> {properties['CTY_SIDE_SWIPE']}</li>
        <li><b>Right Angle:</b> {properties['CTY_RIGHT_ANGLE']}</li>
        <li><b>Head On:</b> {properties['CTY_HEAD_ON']}</li>
        <li><b>Hit Pedestrian:</b> {properties['CTY_HIT_PEDESTRIAN']}</li>
        <li><b>Roll Over:</b> {properties['CTY_ROLL_OVER']}</li>
        <li><b>Right Turn:</b> {properties['CTY_RIGHT_TURN']}</li>
        <li><b>Hit Parked Vehicle:</b> {properties['CTY_HIT_PARKED_VEHILE']}</li>
        <li><b>Hit Animal:</b> {properties['CTY_HIT_ANIMAL']}</li>
        <li><b>Object On Road:</b> {properties['CTY_HIT_OBJECT_ON_ROAD']}</li>
        <li><b>Left Road (Off Course):</b> {properties['CTY_LEFT_ROAD_OC']}</li>
        <li><b>Other:</b> {properties['CTY_OTHER']}</li>
    </ul>
    <p><b>Night Time Crash:</b> {properties['LCO_NIGHT']}</p>
    <p><b>Pedestrian/Bicycle Crash:</b> Pedestrian: {properties['UTY_PEDESTRIAN']}, Bicycle: {properties['UTY_BICYCLE']}</p>
    """

    # Create marker with readable popup data
    folium.Marker(
        location=[coords[1], coords[0]],
        popup=folium.Popup(popup_content, max_width=400)
    ).add_to(marker_cluster)


# Save GeoJSON map to HTML file
print("Saving generated HTML map")
map_file = 'rcr_interactive_map.html'

geojson_map.save(map_file)
print(f"Map generated: {map_file}")

