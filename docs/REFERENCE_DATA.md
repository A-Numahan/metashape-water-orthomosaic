# Camera reference-data format

## Existing CSV structure

```text
image_name,camera_band,Longitude,Latitude,Elevation
DJI_..._D.JPG,RGB,98.93993468,7.853135269,141.26119
DJI_..._MS_G.TIF,Green,98.9399348118,7.8531354409,141.2703240
```

Map the fields in Metashape's Import CSV dialog as follows:

| CSV field | Metashape field |
|---|---|
| `image_name` | Label |
| `Longitude` | Longitude/X |
| `Latitude` | Latitude/Y |
| `Elevation` | Altitude/Z |
| `camera_band` | Do not import as a coordinate field |

Select the CRS used by the actual PPK workflow. The existing GeoPackages identify the
horizontal coordinates as EPSG:4326, but EPSG:4326 alone does not establish the
vertical datum of the `Elevation` values.

## Rotation data required by the force-position script

`force_camera_position.py` requires both location and rotation in the Reference pane.
The existing CSV files do not contain Yaw/Pitch/Roll columns, so rotation must come from
image metadata or an additional PPK/INS file. A camera without rotation is skipped.

When importing angles, verify the convention—for example, Yaw/Pitch/Roll versus
Omega/Phi/Kappa. The current force-position script supports only
`Metashape.EulerAnglesYPR`.

## Accuracy settings

Accuracy values should represent actual post-processed PPK uncertainty rather than the
best value in the hardware specification. If the report gives H = 2 cm and V = 5 cm:

- X accuracy = `0.02 m`
- Y accuracy = `0.02 m`
- Z accuracy = `0.05 m`

If Metashape displays metres, entering `0.02 cm` would mean `0.0002 m` and would assign
unrealistically high weight to the camera position.
