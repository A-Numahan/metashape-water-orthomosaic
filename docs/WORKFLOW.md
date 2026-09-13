# Water-area orthomosaic processing workflow

## 1. Project preparation for both scenarios

1. Create a new project and chunk, then add the photographs. Confirm that
   multispectral imagery is grouped correctly for the DJI Mavic 3 Multispectral import.
2. Set the coordinate reference system to match the PPK data and required output.
3. Import coordinates from the Reference pane. Labels must match camera names,
   including file extensions when extensions are present in the camera labels.
4. Verify EXIF/PPK positions and orientations, and enable the location and rotation
   references that should be used.
5. Set Camera Accuracy from the PPK report—for example, `0.02 m` horizontally and
   `0.05 m` vertically.
6. Save a project checkpoint before alignment.

Do not interpret the CSV `Elevation` value as ground or water elevation. It is a camera
position and may be ellipsoidal or orthometric height depending on the PPK workflow.

## 2. Scenario 1 — Shoreline or stable objects are visible

Use this workflow when land, buildings, vegetation, buoys, or other stationary details
appear in overlapping photographs.

1. Run `Workflow > Align Photos`.
   - Start with High accuracy when computing resources permit.
   - Use Generic preselection and Reference preselection when positions are reliable.
   - Confirm that tie points lie on stable objects rather than waves or reflections.
2. Review aligned and unaligned camera counts and camera errors.
3. Run `Py/force_camera_position.py` only for cameras that remain unaligned.
   - Set `TARGET_LABELS` to test one or two cameras first.
   - Inspect viewing directions against adjacent cameras in Model view.
4. Resize the Region to cover the required area with a small boundary margin.
5. Build depth maps and a point cloud if no suitable elevation source exists.
6. Build the DEM from the verified elevation source.
   - Remove or filter obvious water-surface outliers first.
   - Inspect gaps and unrealistic elevation jumps.
7. Build the orthomosaic using the generated DEM as the surface.
8. Inspect coverage, gaps, seamlines, duplicate objects, and ghosting before exporting
   GeoTIFF.

If the internal DEM contains large gaps over water, use the external-DEM workflow from
Scenario 2 rather than unconstrained interpolation.

## 3. Scenario 2 — Water only or extremely low texture

Use this workflow when standard alignment cannot create a stable tie-point network.

1. Confirm that required cameras are enabled, have image files, and have RTK/PPK
   reference locations.
2. Confirm that camera order in the chunk follows the actual capture sequence.
3. Save a project copy because `Py/align_water_sequential_flightlines.py` removes all
   existing camera alignment.
4. Run `Py/align_water_sequential_flightlines.py`.
   - It measures distances between sequential cameras in the chunk.
   - It starts a new flight line when a distance jump exceeds 2.5 times normal spacing.
   - It pairs only neighboring cameras within the same flight line.
   - It aligns one line at a time and reports track and aligned-camera counts.
5. Confirm that the reported flight lines match the flight plan. Stop and revise the
   split logic if they do not.
6. Run `Py/force_camera_position.py` for cameras that still lack transforms.
7. Resize the Region to include every required footprint and a small boundary margin.
8. Create an external DEM.
   - Use water-surface elevation from a survey, gauge, terrain model, or another source
     with a documented datum.
   - For an assumed flat water surface, create a constant-elevation raster in a
     projected CRS.
   - Never use camera elevations from the reference CSV as water elevations.
   - The raster must cover the full Region and use suitable resolution and NoData.
9. Import the DEM into Metashape and inspect its position and elevation in Ortho view.
10. Build the orthomosaic using the imported DEM as the surface.
11. Compare coverage and positional consistency with shoreline data, checkpoints, or
    independent GIS layers.

## 4. Quality control before delivery

- Report total cameras, bundle-aligned cameras, and force-positioned cameras separately.
- Clearly distinguish bundle-adjusted results from GPS/INS-only results.
- Measure RMSE against independent checkpoints when available.
- Verify both the horizontal CRS and vertical datum.
- Confirm that the orthomosaic covers the complete target area.
- Inspect seams, reflections, waves, vessels, and other moving objects.
- Archive the Metashape processing report, parameters, and software version.
