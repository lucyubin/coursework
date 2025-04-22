"""
Title: Campus Shortest Path Analysis Tool
Description: This script calculates the shortest walking route on a university campus,
             with optional considerations for shaded areas, indoor gate access, and slope.

Authors:
    - Yubin Lee
    - Jong-Ku Park
    - Neelam Thapa Magar

Created: 2025-04-14
Last Updated: 2025-04-22
"""

import arcpy
from arcpy.sa import *
from arcpy.sa import Hillshade

# Set environment
arcpy.env.workspace = r"D:/CampusPath/network.gdb"
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("Network")

# ----------------------------
# 1. Slope
# ----------------------------

def assign_slope(edge_fc, slope_fc, output_fc, slope_field="slope"):
    """
    Creates a new feature class where the 'is_slope' field is set to 1 for edges that intersect
    slope polylines, and 0 otherwise. The original edge_fc is left unchanged.

    Parameters:
    - edge_fc: Input polyline feature class (network edges)
    - slope_fc: Polyline feature class representing slope segments
    - output_fc: Output feature class to store updated edges
    - slope_field: Name of the field to assign slope values (default = 'is_slope')
    """
    arcpy.env.workspace = r"D:/CampusPath/network.gdb"
    arcpy.env.overwriteOutput = True

    # Step 1: Copy the input edge_fc to output_fc
    if arcpy.Exists(output_fc):
        arcpy.management.Delete(output_fc)
    arcpy.management.CopyFeatures(edge_fc, output_fc)

    # Step 2: Add 'is_slope' field to output_fc if not exists
    if slope_field not in [f.name for f in arcpy.ListFields(output_fc)]:
        arcpy.management.AddField(output_fc, slope_field, "SHORT")

    # Step 3: Spatial join to find edges that intersect slope lines
    joined_fc = arcpy.CreateUniqueName("slope_joined", "memory")
    arcpy.analysis.SpatialJoin(
        target_features=output_fc,
        join_features=slope_fc,
        out_feature_class=joined_fc,
        join_type="KEEP_ALL",
        match_option="INTERSECT"
    )

    # Step 4: Assign is_slope = 1 if intersects, else 0
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

"""
assign_slope(
    edge_fc=r"D:\CampusPath\network.gdb\walk_edge",
    slope_fc=r"D:\CampusPath\network.gdb\slope",
    output_fc=r"D:\CampusPath\network.gdb\add_edges"
)
"""

# ----------------------------
# 2. Shade
# ----------------------------

def assign_shade(edge_fc, dsm_raster, output_fc, shadow_threshold=50, azimuth=247, altitude=36, shade_field="shade"):
    """
    Generates shadow polygon from DSM and assigns shade=1 to edges intersecting shadow.
    Writes results to a new feature class (output_fc), leaves original edge_fc unchanged.

    Parameters:
    - edge_fc: Input polyline network edge feature class
    - dsm_raster: DSM raster path
    - output_fc: Output feature class with shade field added
    - shadow_threshold: Threshold to define darkness as shade (default=50)
    - azimuth: Sun azimuth (default=120)
    - altitude: Sun angle altitude (default=35)
    - shade_field: Name of the field to be added/updated (default='shade')
    """
    arcpy.env.workspace = r"D:/CampusPath/network.gdb"
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # 1. Generate hillshade from DSM
    hillshade_raster = Hillshade(
        in_raster=dsm_raster,
        azimuth=azimuth,
        altitude=altitude,
        model_shadows="SHADOWS"
    )

    # 2. Mask for shaded areas (low brightness → shadow)
    shadow_mask = Con(hillshade_raster < shadow_threshold, 1)

    # 3. Convert mask to polygon
    shadow_poly = "memory/shade_polygon"
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
    shadow_joined = "memory/shadow_joined"
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

"""
assign_shade(
    edge_fc=r"D:\CampusPath\network.gdb\add_edges",
    dsm_raster=r"D:\CampusPath\network.gdb\shade_dsm",
    output_fc=r"D:\CampusPath\network.gdb\add_edges2"
)
"""
