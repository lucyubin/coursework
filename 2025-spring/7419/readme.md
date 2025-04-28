# CampusPath 🏫🚶‍♀️

A custom ArcGIS Pro toolbox for **shortest path analysis** on the Texas State University campus, considering **indoor gate access**, **slope**, and **shade**.

## Overview
CampusPath calculates optimal walking routes across campus by adjusting path impedance based on:
- **Indoor gate** shortcuts between buildings
- Presence of **slope**
- Presence of **shaded areas**

Users can assign custom weights (0-1) to prioritize different walking conditions according to their needs.

## Features
- **Gate Assignment**: Connects building entrances internally for efficient indoor navigation.
- **Slope Assignment**: Identifies edges affected by slope.
- **Shade Assignment**: Detects shaded areas based on DSM-derived hillshade analysis.
- **Weighted Routing**: Finds a walking route optimized based on user-defined shade, slope, and gate access preferences.

## Requirements
- ArcGIS Pro (with Network Analyst and Spatial Analyst extensions)
- Python (ArcPy environment)

## Usage
1. **Prepare Network Data**:
   - Walk network edge
   - Gate points
   - Slope polylines
   - DSM raster for hillshade generation

2. **Run the Toolbox**:
   - Assign gates: Add internal edges connecting the building's indoor gates.
   - Assign slope: Mark edges affected by slope.
   - Assign shade: Identify edges under shaded areas.
   - Generate weighted routes: Specify slope, shade, and gate preferences weights (0-1).

3. **Parameters** (for `run_impedance_route`):
   - `use_slope`, `slope_weight`
   - `use_shade`, `shade_weight`
   - `use_gate`, `gate_weight`
   - Start and end points
   - Output feature class name

## Example
```python
run_impedance_route(
    workspace_gdb="*/data/CampusPath.gdb",
    input_fc_name="walk_edge",
    use_slope=True,
    slope_weight=0.8,
    use_shade=True,
    shade_weight=0.6,
    use_gate=True,
    gate_weight=0.5,
    start_point=(-97.9461797, 29.8908552),
    end_point=(-97.9390373, 29.8894287),
    output_fc="FinalRoute"
)
```

## Authors
- Jong-Ku Park
- Neelam Thapa Magar
- Yubin Lee

(Team JNY)

---

> **Created:** 2025-04-14  
> **Last Updated:** 2025-04-27
