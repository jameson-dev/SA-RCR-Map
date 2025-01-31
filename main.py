import json
import os

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
suburb_crash_data = crash_to_suburb.groupby("suburb")["TOTAL_CRASHES"].sum().to_dict()

# Set map center coordinates
map_center = [-30.5344, 135.6300]
print(f"Setting map (center) location to {map_center[0]}, {map_center[1]}")

# Generate map
print("Generating map")
geojson_map = folium.Map(
    location=map_center,
    zoom_start=6
    )

# Create MarkerCluster object
marker_cluster = MarkerCluster(name="Crash Sites").add_to(geojson_map)

# Add markers to cluster
print("Adding markers to map clusters")
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

# Add choropleth layer
print("Adding choropleth layer")
folium.Choropleth(
    geo_data=suburbs_geojson_file,
    name='Choropleth',
    data=list(suburb_crash_data.items()),
    columns=['suburb', 'crash_count'],
    key_on='feature.properties.suburb',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    threshold_scale=[0, 5, 10, 25, 50, 80, 150, 300, 600, 800, 1000, 1500, 2000, max(suburb_crash_data.values())],
    legend_name='Total Crashes by Suburb',

).add_to(geojson_map)

# Add layer control
print("Adding layer control to map")
folium.LayerControl().add_to(geojson_map)

# Save the map to an HTML file
map_file = 'index.html'
print(f"Saving generated HTML map to {map_file}")

geojson_map.save(map_file)
file_size = os.path.getsize(map_file) / 1024  # Convert bytes to KB
print(f"Map generated: {map_file} ({file_size:.2f} KB)")
