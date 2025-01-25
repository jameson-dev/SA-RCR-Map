import json
import folium

geojson_file = "datasets/RoadCrashes_GDA2020.geojson"


print(f"Collecting data from dataset: {geojson_file}")
with open(geojson_file, 'r') as file:
    geojson_data = json.load(file)

map_center = [30.0002, 136.2092]
print(f"Setting map (center) location to {map_center[0]}, {map_center[1]}")

print("Generating map")
m = folium.Map(location=map_center, zoom_start=10)


folium.GeoJson(geojson_data).add_to(m)
print("Saving generated HTML map")
map_file = 'rcr_interactive_map.html'

m.save(map_file)
print(f"Map generated: {map_file}")

m.save('rcr_interactive_map.html')