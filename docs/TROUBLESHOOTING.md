# Troubleshooting

## Fewer cameras have reference locations than expected

Confirm that reference import succeeded, CSV names match camera labels, and the CRS is
correct. Each camera must be enabled, have an image, and contain
`camera.reference.location`.

## Flight lines are missing or split incorrectly

- Check for swapped Longitude and Latitude fields.
- Inspect the PPK data for position outliers.
- Confirm that `chunk.cameras` follows the actual capture sequence.
- Check whether nearly identical coordinates from multiple bands at one station make
  the median sequential spacing too small.
- If turns do not produce a clear position jump, split the chunk by flight-line group
  before running the script.
- Adjust the `2.5` multiplier used for `LINE_BREAK_DISTANCE` carefully and inspect the
  reported lines after every change.

## Force-positioned cameras point in the wrong direction

Stop and undo the operation, then verify:

- the angle convention is actually Yaw/Pitch/Roll;
- angle units are degrees;
- orientation describes the gimbal rather than only the aircraft body;
- antenna or lever-arm offsets in Camera Calibration;
- the horizontal CRS and vertical datum.

## The orthomosaic has gaps over water

Confirm that the DEM covers the Region and that all required cameras have transforms.
When water tie points are unstable, use an external DEM with a reliable water-surface
elevation instead of increasing only the key-point limit.

## Duplicate features, seam artifacts, or distorted waves

Water is not stationary between exposures, so wave details should not automatically be
treated as fixed ground features. Inspect seamlines, select suitable source images, and
define delivery limits that reflect the actual quality of the source data.
