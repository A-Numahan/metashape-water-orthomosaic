# Metashape scripts

Run these scripts from Agisoft Metashape Professional through `Tools > Run Script`
or the Python Console. They are not intended for a standard external Python runtime.

## `align_water_sequential_flightlines.py`

Use this script when the scene contains only water or has extremely low texture. It:

1. Selects enabled cameras that have an image and a reference location.
2. Measures spacing between adjacent cameras in the chunk sequence.
3. Starts a new flight line when the sequential distance exceeds 2.5 times the median.
4. Pairs each camera with up to `NEIGHBOR` following cameras in the same flight line.
5. Matches photos and aligns cameras one flight line at a time.

> [!CAUTION]
> The script sets `camera.transform = None` for every camera before matching. This
> removes all previous camera alignment. Save a copy of the `.psx` project first and
> do not run the script in a chunk whose existing alignment must be preserved.

> [!IMPORTANT]
> The method assumes `chunk.cameras` follows the actual capture sequence and that
> transitions between flight lines produce a clear distance jump. If images are
> ordered by band or name, or if multiple bands at one camera station have nearly
> identical positions, inspect the reported flight lines before trusting the result.

Common settings:

- `NEIGHBOR` — number of following cameras paired within the same flight line
- `DOWNSCALE` — `0` = Highest, `1` = High, `2` = Medium
- `KEYPOINT_LIMIT` — maximum number of key points
- `LINE_BREAK_DISTANCE` — calculated as median sequential spacing × 2.5

## `force_camera_position.py`

Creates `camera.transform` for unaligned regular cameras using the position and
Yaw/Pitch/Roll values in the Reference pane. Cameras that are already aligned or lack
reference information are skipped.

Verify these assumptions before running it:

- `chunk.euler_angles` is `Yaw/Pitch/Roll`.
- Both `camera.reference.location` and `camera.reference.rotation` are available.
- No unaccounted antenna or lever-arm offset is configured.
- The horizontal CRS and vertical datum are correct.

Set `TARGET_LABELS` and test one or two cameras before processing the full dataset.
