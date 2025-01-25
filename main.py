import json
import folium

geojson_file = "datasets/RoadCrashes_GDA2020.geojson"

with open(geojson_file, 'r') as file:
    geojson_data = json.load(file)

map_center = [-37.8301386, 140.7842627]
m = folium.Map(location=map_center, zoom_start=10)


folium.GeoJson(geojson_data).add_to(m)

m.save('rcr_interactive_map.html')