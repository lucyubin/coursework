import arcpy
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from pyproj import Transformer
import osmnx as ox

# Network dataset path
network_dataset = r"*\final_project\network.gdb\SM_walk\SM_walk_network"

# 1️. Build the network dataset
arcpy.na.BuildNetwork(network_dataset)

# 2️. Create a Route Analysis Layer
layer_name = "RouteLayer"
if arcpy.Exists(layer_name):
    arcpy.management.Delete(layer_name)
arcpy.na.MakeRouteAnalysisLayer(network_dataset, layer_name, "Length")

# 3️. Get network analysis sublayers
sub_layers = arcpy.na.GetNAClassNames(layer_name)
stops_layer = sub_layers["Stops"]

# 4️. Define start and destination coordinates
stops = [
    ("Alkek Library", 29.8886, -97.9431),  # Start location
    ("Old Main", 29.888600, -97.943100)  # Destination
]

# 5️. Convert stops to a feature class (layer) and add to the route analysis layer
stops_fc = "memory/Stops"
if arcpy.Exists(stops_fc):
    arcpy.management.Delete(stops_fc)
arcpy.management.CreateFeatureclass("memory", "Stops", "POINT", spatial_reference=arcpy.SpatialReference(4326))
arcpy.management.AddField(stops_fc, "Name", "TEXT")

# Use InsertCursor to add coordinates
with arcpy.da.InsertCursor(stops_fc, ["Name", "SHAPE@XY"]) as cursor:
    for name, x, y in stops:
        cursor.insertRow((name, (x, y)))

# 6️. Add stops to the Route Layer (connect to the network)
arcpy.na.AddLocations(layer_name, "Stops", stops_fc, search_tolerance="500 Meters")

# 7️. Solve for the shortest route
arcpy.na.Solve(layer_name)

# 8️. Save the results
output_fc = r"*\final_project\network.gdb\ShortestRoute"
if arcpy.Exists(output_fc):
    arcpy.management.Delete(output_fc)
arcpy.management.CopyFeatures(layer_name + "/Routes", output_fc)
