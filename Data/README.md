# Reference data

The local workspace contains two survey datasets:

| Dataset | Records | Camera stations | Bands per station | GeoPackage CRS |
|---|---:|---:|---:|---|
| `K_AreaC/Area_C` | 1,450 | 290 | 5 | EPSG:4326 |
| `T_AreaE/Area_E` | 2,495 | 499 | 5 | EPSG:4326 |

Each station contains `RGB`, `Green`, `Red`, `RedEdge`, and `NIR` records. The CSV and
GeoPackage files contain `image_name`, `camera_band`, `Longitude`, `Latitude`, and
`Elevation` fields.

Real `.csv` and `.gpkg` files are intentionally excluded by `.gitignore` because they
contain survey coordinates and image identifiers. Confirm publication rights and
anonymize sensitive information before sharing a sample. Use Git LFS for approved
large files, or publish a small synthetic example instead.
