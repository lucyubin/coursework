"""
Title: Campus Shortest Path Analysis Tool (CampusPath)
Description: This script calculates the shortest walking route on a university campus,
             with optional considerations for shaded areas, indoor gate access, and slope.
Authors: (Team JNY)
          Jong-Ku Park
          Neelam Thapa Magar
          Yubin Lee
Created: 2025-04-14
Last Updated: 2025-04-27
"""

import arcpy
import os
from arcpy.sa import *
from arcpy.sa import Hillshade

# Set environment
arcpy.env.workspace = r"C:\CampusPath\data\network.gdb"
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("Network")


# ----------------------------
# 1. Gates
# ----------------------------

def assign_gate(input_network_fc, gate_fc, output_fc):
    """
    Adds internal gate-to-gate edges between gates of the same building and merges with existing network.
    Adds 'internal' field: 1 for internal gate edge, 0 for original edges.

    Parameters:
    - input_network_fc: Existing edge feature class (e.g., walk_edge)
    - gate_fc: Point feature class with BldgID
    - output_fc: Output merged feature class (e.g., add_edges)
    """
    arcpy.env.workspace = r"C:\CampusPath\data\network.gdb"
    arcpy.env.overwriteOutput = True

    # 1. Get spatial reference
    spatial_ref = arcpy.Describe(gate_fc).spatialReference

    # 2. Create in-memory feature class for gate-to-gate edges
    gate_edges_fc = "memory\gate_edges"
    if arcpy.Exists(gate_edges_fc):
        arcpy.management.Delete(gate_edges_fc)

    arcpy.management.CreateFeatureclass(
        out_path="memory",
        out_name="gate_edges",
        geometry_type="POLYLINE",
        spatial_reference=spatial_ref
    )

    # 3. Add 'internal' field only
    if "internal" not in [f.name.lower() for f in arcpy.ListFields(gate_edges_fc)]:
        arcpy.management.AddField(gate_edges_fc, "internal", "SHORT")

    # 4. Group gate points by building
    gate_dict = {}
    with arcpy.da.SearchCursor(gate_fc, ["BldgID", "SHAPE@XY"]) as cursor:
        for bldg_id, coord in cursor:
            gate_dict.setdefault(bldg_id, []).append(coord)

    # 5. Create internal edges
    with arcpy.da.InsertCursor(gate_edges_fc, ["SHAPE@", "internal"]) as cursor:
        for gate_list in gate_dict.values():
            if len(gate_list) < 2:
                continue
            for i in range(len(gate_list)):
                for j in range(i + 1, len(gate_list)):
                    pt1, pt2 = gate_list[i], gate_list[j]
                    line = arcpy.Polyline(arcpy.Array([arcpy.Point(*pt1), arcpy.Point(*pt2)]), spatial_ref)
                    cursor.insertRow([line, 1])

    # 6. Copy input network and ensure 'internal' field = 0
    temp_fc = "memory\temp_network"
    arcpy.management.CopyFeatures(input_network_fc, temp_fc)

    if "internal" not in [f.name.lower() for f in arcpy.ListFields(temp_fc)]:
        arcpy.management.AddField(temp_fc, "internal", "SHORT")

    with arcpy.da.UpdateCursor(temp_fc, ["internal"]) as cursor:
        for row in cursor:
            row[0] = 0
            cursor.updateRow(row)

    # 7. Merge
    arcpy.management.Merge([temp_fc, gate_edges_fc], output_fc)

    print(f"✅ Internal gate edges merged. Output saved to: {output_fc}")

assign_gate(
    input_network_fc=r"C:\CampusPath\data\network.gdb\walk_edge",
    gate_fc=r"C:\CampusPath\data\network.gdb\gate_points",
    output_fc=r"C:\CampusPath\data\network.gdb\add_edges"
)

# ----------------------------
# 2. Slope
# ----------------------------

def assign_slope(edge_fc, slope_fc, output_fc, slope_field="slope"):
    """
    Creates a new feature class where the 'slope' field is set to 1 for edges that intersect
    slope polylines, and 0 otherwise. The original edge_fc is left unchanged.

    Parameters:
    - edge_fc: Input polyline feature class (network edges)
    - slope_fc: Polyline feature class representing slope segments
    - output_fc: Output feature class to store updated edges
    - slope_field: Name of the field to assign slope values (default = 'slope')
    """
    arcpy.env.workspace = r"C:\CampusPath\data\network.gdb"
    arcpy.env.overwriteOutput = True

    # 1: Copy the input edge_fc to output_fc
    if arcpy.Exists(output_fc):
        arcpy.management.Delete(output_fc)
    arcpy.management.CopyFeatures(edge_fc, output_fc)

    # 2: Add 'slope' field to output_fc if not exists
    if slope_field not in [f.name for f in arcpy.ListFields(output_fc)]:
        arcpy.management.AddField(output_fc, slope_field, "SHORT")

    # 3: Spatial join to find edges that intersect slope lines
    joined_fc = arcpy.CreateUniqueName("slope_joined", "memory")
    arcpy.analysis.SpatialJoin(
        target_features=output_fc,
        join_features=slope_fc,
        out_feature_class=joined_fc,
        join_type="KEEP_ALL",
        match_option="INTERSECT"
    )

    # 4: Assign slope = 1 if intersects, else 0
    with arcpy.da.UpdateCursor(joined_fc, ["Join_Count", slope_field]) as cursor:
        for join_count, _ in cursor:
            cursor.updateRow((join_count, 1 if join_count > 0 else 0))

    # Step 5: Transfer updated values back to output_fc
    oid_field = arcpy.Describe(output_fc).OIDFieldName
    joined_dict = {}

    with arcpy.da.SearchCursor(joined_fc, [oid_field, slope_field]) as cursor:
        for oid, val in cursor:
            joined_dict[oid] = val

    with arcpy.da.UpdateCursor(output_fc, [oid_field, slope_field]) as cursor:
        for oid, _ in cursor:
            val = joined_dict.get(oid, 0)
            cursor.updateRow((oid, val))

    print(f"✅ Slope assignment complete in {output_fc}: {slope_field} = 1 if intersects slope")

assign_slope(
    edge_fc=r"C:\CampusPath\data\network.gdb\add_edges",
    slope_fc=r"C:\CampusPath\data\network.gdb\slope",
    output_fc=r"C:\CampusPath\data\network.gdb\add_edges2"
)

# ----------------------------
# 3. Shade
# ----------------------------

def assign_shade(edge_fc, dsm_raster, output_fc, azimuth=247, altitude=36, shade_field="shade"):
    """
    Generates shadow polygon from DSM where pixel value = 0 and assigns shade=1 to edges intersecting shadow.
    Writes results to a new feature class (output_fc), leaves original edge_fc unchanged.

    Parameters:
    - edge_fc: Input polyline network edge feature class
    - dsm_raster: DSM raster path
    - output_fc: Output feature class with shade field added
    - azimuth: Sun azimuth (default=247)
    - altitude: Sun angle altitude (default=36)
    - shade_field: Name of the field to be added\updated (default='shade')
    """
    arcpy.env.workspace = r"C:\CampusPath\data\network.gdb"
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # 1. Generate hillshade from DSM
    hillshade_raster = Hillshade(
        in_raster=dsm_raster,
        azimuth=azimuth,
        altitude=altitude,
        model_shadows="SHADOWS"
    )

    # Optional: Save hillshade raster to visually inspect shadow values
    # hillshade_raster.save(r"C:\CampusPath\data\network.gdb\hillshade_output")

    # 2. Mask for shaded areas (only pixel value = 0 is shadow)
    shadow_mask = Con(hillshade_raster == 0, 1)

    # 3. Convert mask to polygon
    shadow_poly = "memory\shade_polygon"
    arcpy.conversion.RasterToPolygon(
        in_raster=shadow_mask,
        out_polygon_features=shadow_poly,
        simplify="NO_SIMPLIFY"
    )

    # 4. Copy edge_fc → output_fc
    if arcpy.Exists(output_fc):
        arcpy.management.Delete(output_fc)
    arcpy.management.CopyFeatures(edge_fc, output_fc)

    # 5. Add 'shade' field if missing
    if shade_field not in [f.name for f in arcpy.ListFields(output_fc)]:
        arcpy.management.AddField(output_fc, shade_field, "SHORT")

    # 6. Perform spatial join: output edges ∩ shadow polygon
    shadow_joined = "memory\shadow_joined"
    arcpy.analysis.SpatialJoin(
        target_features=output_fc,
        join_features=shadow_poly,
        out_feature_class=shadow_joined,
        join_type="KEEP_ALL",
        match_option="INTERSECT"
    )

    # 7. Update shade field in joined feature class
    with arcpy.da.UpdateCursor(shadow_joined, ["Join_Count", shade_field]) as cursor:
        for join_count, _ in cursor:
            cursor.updateRow((join_count, 1 if join_count > 0 else 0))

    # 8. Transfer updated 'shade' values back to output_fc
    oid_field = arcpy.Describe(output_fc).OIDFieldName
    shade_dict = {}
    with arcpy.da.SearchCursor(shadow_joined, [oid_field, shade_field]) as cursor:
        for oid, val in cursor:
            shade_dict[oid] = val

    with arcpy.da.UpdateCursor(output_fc, [oid_field, shade_field]) as cursor:
        for oid, _ in cursor:
            cursor.updateRow((oid, shade_dict.get(oid, 0)))

    # 9. Summary
    shaded_count = sum(1 for v in shade_dict.values() if v == 1)
    print(f"✅ Shade assignment complete: {shaded_count} shaded edges in '{output_fc}'")

assign_shade(
    edge_fc=r"C:\CampusPath\data\network.gdb\add_edges2",
    dsm_raster=r"C:\CampusPath\data\network.gdb\shade_dsm",
    output_fc=r"C:\CampusPath\data\network.gdb\add_edges3"
)

# ----------------------------
# 4. Weighted route
# ----------------------------

def run_impedance_route(
    workspace_gdb,
    input_fc_name,
    use_slope=False,
    slope_weight=0.0,
    use_shade=False,
    shade_weight=0.0,
    use_gate=False,
    gate_weight=0.0,
    start_point=(-97.9461797, 29.8908552),
    end_point=(-97.9390373, 29.8894287),
    output_fc="FinalRoute"
):
    """
    Finds an optimal walking route using impedance values adjusted by slope, shade, and gate preferences.
    Impedance is calculated as: Impedance = Shape_Length * penalty_factor
    The penalty factor decreases when preferred features (slope, shade, gate) are present.

    Parameters:
    - workspace_gdb: Path to geodatabase
    - input_fc_name: Name of edge feature class
    - use_slope, use_shade, use_gate: Whether to apply slope\shade\gate preferences
    - slope_weight, shade_weight, gate_weight: Preference weights (0 to 1)
    - start_point, end_point: Tuple (X, Y) coordinates
    - output_fc: Name of output route feature class
    """
    arcpy.env.workspace = workspace_gdb
    arcpy.env.overwriteOutput = True

    input_fc = os.path.join(workspace_gdb, input_fc_name)

    # Ensure required fields exist
    for field_name, field_type in [("slope", "SHORT"), ("shade", "SHORT"), ("internal", "SHORT"), ("Impedance", "DOUBLE")]:
        if field_name not in [f.name for f in arcpy.ListFields(input_fc)]:
            arcpy.management.AddField(input_fc, field_name, field_type)

    # Fill NULLs with 0
    with arcpy.da.UpdateCursor(input_fc, ["slope", "shade", "internal"]) as cursor:
        for row in cursor:
            row[0] = row[0] or 0
            row[1] = row[1] or 0
            row[2] = row[2] or 0
            cursor.updateRow(row)

    # Validate Shape_Length
    if "Shape_Length" not in [f.name for f in arcpy.ListFields(input_fc)]:
        raise Exception("❗ 'Shape_Length' field missing.")

    # Calculate impedance = Shape_Length * penalty_factor
    with arcpy.da.UpdateCursor(input_fc, ["slope", "shade", "internal", "Shape_Length", "Impedance"]) as cursor:
        for row in cursor:
            slope_val, shade_val, internal_val, length = row[:4]

            if not use_gate and internal_val == 1:
                row[4] = None  # exclude gate edges if gate=False
            else:
                penalty_factor = 1.0
                if use_slope and slope_val == 1:
                    penalty_factor *= slope_weight
                if use_shade and shade_val == 1:
                    penalty_factor *= shade_weight
                if use_gate and internal_val == 1:
                    penalty_factor *= gate_weight
                row[4] = length * penalty_factor
            cursor.updateRow(row)

    # Load appropriate network dataset
    network_name = "network_ND" if use_gate else "network_ND2"
    network_dataset = os.path.join(workspace_gdb, "network", network_name)
    arcpy.na.BuildNetwork(network_dataset)

    # Create route layer
    route_layer = "in_memory\RouteLayer"
    arcpy.na.MakeRouteAnalysisLayer(network_dataset, route_layer, "Impedance")

    # Create Stops in memory
    stops_fc = "in_memory\Stops"
    if arcpy.Exists(stops_fc):
        arcpy.management.Delete(stops_fc)
    arcpy.management.CreateFeatureclass("in_memory", "Stops", "POINT", spatial_reference=4326)
    arcpy.management.AddField(stops_fc, "Name", "TEXT")
    with arcpy.da.InsertCursor(stops_fc, ["Name", "SHAPE@XY"]) as cursor:
        cursor.insertRow(("Start", start_point))
        cursor.insertRow(("End", end_point))

    # Add Stops to route layer
    sub_layers = arcpy.na.GetNAClassNames(route_layer)
    arcpy.na.AddLocations(route_layer, sub_layers["Stops"], stops_fc, search_tolerance="5000 Meters")

    # Solve and export route
    result_path = os.path.join(workspace_gdb, output_fc)

    try:
        arcpy.na.Solve(route_layer)
        if arcpy.Exists(result_path):
            arcpy.management.Delete(result_path)
        arcpy.management.CopyFeatures(f"{route_layer}\Routes", result_path)
        print(f"Route saved to: {result_path}")
    except Exception as e:
        print(f"Route solve failed: {e}")
        result_path = None

    # Add to current map with custom symbology
    project = arcpy.mp.ArcGISProject("CURRENT")
    active_map = project.activeMap
    active_map.addDataFromPath(result_path)

    # Set symbology to dark blue arrow
    project = arcpy.mp.ArcGISProject("CURRENT")
    active_map = project.activeMap
    added_layer = active_map.addDataFromPath(result_path)

    for lyr in active_map.listLayers():
        if lyr.name == os.path.basename(result_path):
            sym = lyr.symbology

            if hasattr(sym, "renderer"):
                sym.renderer.symbol.applySymbolFromGallery("Bold Arrow 3")
                sym.renderer.symbol.color = {'RGB': [0, 51, 153, 100]}  # Thick blue color
                sym.renderer.symbol.size = 5.5

                lyr.symbology = sym
            break

    # Clean up leftover feature datasets
    for ds in arcpy.ListDatasets("*", "Feature"):
        if ds.lower().startswith("routesolver"):
            arcpy.management.Delete(ds)

# ArcGIS Toolbox Interface
if __name__ == "__main__":
    gdb = arcpy.GetParameterAsText(0)
    use_slope = arcpy.GetParameter(1)
    slope_weight = float(arcpy.GetParameterAsText(2))
    use_shade = arcpy.GetParameter(3)
    shade_weight = float(arcpy.GetParameterAsText(4))
    use_gate = arcpy.GetParameter(5)
    gate_weight = float(arcpy.GetParameterAsText(6))
    start_fs = arcpy.GetParameter(7)  # Feature Set (Start Point)
    end_fs = arcpy.GetParameter(8)  # Feature Set (End Point)
    # Coordinate refresh
    start_point = None
    end_point = None

    with arcpy.da.SearchCursor(start_fs, ["SHAPE@XY"]) as cursor:
        for row in cursor:
            start_point = row[0]
            break

    with arcpy.da.SearchCursor(end_fs, ["SHAPE@XY"]) as cursor:
        for row in cursor:
            end_point = row[0]
            break
    output_fc = arcpy.GetParameterAsText(9)

    # Input setting
    input_fc_name = "walk_join2"

    # Calling the function
    run_impedance_route(
        workspace_gdb=gdb,
        input_fc_name=input_fc_name,
        use_slope=use_slope,
        slope_weight=slope_weight,
        use_shade=use_shade,
        shade_weight=shade_weight,
        use_gate=use_gate,
        gate_weight=gate_weight,
        start_point=start_point,
        end_point=end_point,
        output_fc=output_fc
    )
