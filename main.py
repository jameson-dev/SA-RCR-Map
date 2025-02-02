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

# Create FeatureGroups for filtering
fatal_crashes = folium.FeatureGroup(name="Fatal Crashes", show=False)
serious_inj = folium.FeatureGroup(name="Serious Injuries", show=False)
minor_inj = folium.FeatureGroup(name="Minor Injuries", show=False)
property_dmg = folium.FeatureGroup(name="Property Damage", show=False)
rear_end = folium.FeatureGroup(name="Rear End", show=False)
hit_fixed_object = folium.FeatureGroup(name="Hit Fixed Object", show=False)
side_swipe = folium.FeatureGroup(name="Side Swipe", show=False)
right_angle = folium.FeatureGroup(name="Right Angle", show=False)
head_on = folium.FeatureGroup(name="Head On", show=False)
hit_pedestrian = folium.FeatureGroup(name="Hit Pedestrian", show=False)
roll_over = folium.FeatureGroup(name="Roll Over", show=False)
right_turn = folium.FeatureGroup(name="Right Turn", show=False)
hit_parked_veh = folium.FeatureGroup(name="Hit Parked Vehicle", show=False)
hit_animal = folium.FeatureGroup(name="Hit Animal", show=False)
hit_object_on_road = folium.FeatureGroup(name="Hit Object on Road", show=False)
left_road = folium.FeatureGroup(name="Left Road", show=False)
cty_other = folium.FeatureGroup(name="Other", show=False)

# Define Feature Groups with Clustering
fatal_cluster = MarkerCluster(name="Fatal Crashes", show=True).add_to(fatal_crashes)
serious_cluster = MarkerCluster(name="Serious Injuries", show=True).add_to(serious_inj)
minor_cluster = MarkerCluster(name="Minor Injuries", show=True).add_to(minor_inj)
property_cluster = MarkerCluster(name="Property Damage", show=True).add_to(property_dmg)
rear_end_cluster = MarkerCluster(name="Rear End", show=True).add_to(rear_end)
hit_fixed_cluster = MarkerCluster(name="Hit Fixed Object", show=True).add_to(hit_fixed_object)
side_swipe_cluster = MarkerCluster(name="Side Swipe", show=True).add_to(side_swipe)
right_angle_cluster = MarkerCluster(name="Right Angle", show=True).add_to(right_angle)
head_on_cluster = MarkerCluster(name="Head On", show=True).add_to(head_on)
hit_pedestrian_cluster = MarkerCluster(name="Hit Pedestrian", show=True).add_to(hit_pedestrian)
roll_over_cluster = MarkerCluster(name="Roll Over", show=True).add_to(roll_over)
right_turn_cluster = MarkerCluster(name="Right Turn", show=True).add_to(right_turn)
hit_parked_veh_cluster = MarkerCluster(name="Hit Parked Vehicle", show=True).add_to(hit_parked_veh)
hit_animal_cluster = MarkerCluster(name="Hit Animal", show=True).add_to(hit_animal)
hit_object_on_road_cluster = MarkerCluster(name="Hit Object on Road", show=True).add_to(hit_object_on_road)
left_road_cluster = MarkerCluster(name="Left Road", show=True).add_to(left_road)
cty_other_cluster = MarkerCluster(name="Other", show=True).add_to(cty_other)

# Add clusters to the map
geojson_map.add_child(fatal_crashes)
geojson_map.add_child(serious_inj)
geojson_map.add_child(minor_inj)
geojson_map.add_child(rear_end)
geojson_map.add_child(hit_fixed_object)
geojson_map.add_child(side_swipe)
geojson_map.add_child(right_angle)
geojson_map.add_child(head_on)
geojson_map.add_child(hit_pedestrian)
geojson_map.add_child(roll_over)
geojson_map.add_child(right_turn)
geojson_map.add_child(hit_parked_veh)
geojson_map.add_child(hit_animal)
geojson_map.add_child(hit_object_on_road)
geojson_map.add_child(left_road)
geojson_map.add_child(cty_other)

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
for feature in geojson_data['features']:
    coords = feature['geometry']['coordinates']
    properties = feature['properties']

    popup_content = f"""
    <h5><b>Crash Type</b></h5>
    """ + "".join(f"<span><b>{name}:</b> {properties[key]}<br></span>" for key, name in crash_types.items() if properties.get(key, 0) > 0)

    # Add marker to the appropriate cluster
    for key, cluster in crash_clusters.items():
        if properties.get(key):
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(popup_content, max_width=400)
            ).add_to(cluster)

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

# Add layer control
print("Adding layer control to map")
folium.LayerControl().add_to(geojson_map)

# Save the map to an HTML file
map_file = 'index.html'
print(f"Saving generated HTML map to {map_file}")

geojson_map.save(map_file)

file_size = os.path.getsize(map_file) / 1024  # Convert bytes to KB
print(f"Map generated: {map_file} ({file_size:.2f} KB)")
