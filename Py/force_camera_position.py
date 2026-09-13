# force_camera_position.py
#
# Forces camera.transform (exterior orientation) directly from the Reference pane's
# GPS location + gimbal yaw/pitch/roll, for cameras that have NO tie-point alignment
# (camera.transform is empty). Use this only for cameras where bundle adjustment could
# not solve a position (e.g. water frames with no tie points).
#
# This is the mathematical INVERSE of Agisoft's own official script
# "Save estimated reference" (save_estimated_reference.py, agisoft-llc/metashape-scripts):
# that script converts camera.transform -> reference location/rotation for QA reporting.
# This script goes the other way: reference location/rotation -> camera.transform.
#
# IMPORTANT — READ BEFORE RUNNING
# 1. This gives LOWER ACCURACY positions than real tie-point alignment. It relies purely
#    on RTK GPS + gimbal IMU, with no bundle-adjustment refinement. Only use it on cameras
#    that genuinely cannot align any other way.
# 2. Assumes chunk.euler_angles == Metashape.EulerAnglesYPR (Metashape's default for
#    drone/GPS+INS projects, showing "Yaw / Pitch / Roll" columns in the Reference pane).
#    If your Reference pane instead shows Omega/Phi/Kappa, STOP — this script needs
#    adjustment for that convention.
# 3. Assumes no GPS/INS antenna offset is configured on the sensor (Tools > Camera
#    Calibration > Antenna). True by default unless you set one manually.
# 4. TEST ON 1-2 CAMERAS FIRST (see TARGET_LABELS below), then visually check their
#    position/orientation in the 3D view against neighboring aligned cameras before
#    running on the full set.
# 5. Run this from Metashape's own Python Console (or Tools > Run Script), not from
#    an external Python install — it needs the Metashape module and an open document.

import Metashape

doc = Metashape.app.document
chunk = doc.chunk
if chunk is None:
    raise Exception("No active chunk in the document")

if chunk.euler_angles != Metashape.EulerAnglesYPR:
    raise Exception(
        "chunk.euler_angles is not YPR (Yaw/Pitch/Roll). This script does not handle "
        "OPK/POK/ANK conventions — check the Reference pane column headers and adjust "
        "the script before proceeding."
    )

# --- Optional: restrict to specific cameras for a first test run. ---
# Set to a list of exact camera labels (filenames without extension, as shown in the
# Reference pane) to test on just those. Set to None to process ALL unaligned cameras
# that have reference data.
TARGET_LABELS = None
# Example for a first test:
# TARGET_LABELS = ["DJI_20260619071543_0071_MS_G", "DJI_20260619071543_0071_MS_R"]

transform = chunk.transform.matrix
crs = chunk.crs
if chunk.camera_crs:
    transform = Metashape.CoordinateSystem.datumTransform(crs, chunk.camera_crs) * transform
    crs = chunk.camera_crs

ecef_crs = crs.geoccs
if ecef_crs is None:
    ecef_crs = Metashape.CoordinateSystem('LOCAL')

# Matches getAntennaTransform() in Agisoft's script when no antenna offset is set:
# Diag((1,-1,-1,1)) with zero translation/rotation. It's its own inverse (diagonal ±1).
flip = Metashape.Matrix.Diag((1, -1, -1, 1))
flip_rotation = flip.rotation()

forced = 0
skipped_already_aligned = 0
skipped_no_reference = 0
skipped_not_targeted = 0

for camera in chunk.cameras:
    if camera.type != Metashape.Camera.Type.Regular:
        continue

    if TARGET_LABELS is not None and camera.label not in TARGET_LABELS:
        skipped_not_targeted += 1
        continue

    if camera.transform:
        skipped_already_aligned += 1
        continue

    if not camera.reference.location or not camera.reference.rotation:
        skipped_no_reference += 1
        continue

    # --- location: reference (crs) -> cartesian (ecef-like) ---
    location_ecef = Metashape.CoordinateSystem.transform(camera.reference.location, crs, ecef_crs)

    # --- rotation: reference YPR -> cartesian rotation matrix ---
    localframe = ecef_crs.localframe(location_ecef)
    Rypr = Metashape.Utils.ypr2mat(camera.reference.rotation)
    rotation_ecef = localframe.rotation().t() * Rypr
    camera_rotation = rotation_ecef * flip_rotation  # undo the antenna flip convention

    camera_transform_ecef = Metashape.Matrix.Translation(location_ecef) * Metashape.Matrix.Rotation(camera_rotation)

    # transform * camera.transform == camera_transform_ecef  =>  camera.transform = transform^-1 * camera_transform_ecef
    camera.transform = transform.inv() * camera_transform_ecef
    forced += 1
    print("Forced: {}".format(camera.label))

print("")
print("Done.")
print("  Forced position/orientation : {}".format(forced))
print("  Already aligned (skipped)   : {}".format(skipped_already_aligned))
print("  Missing reference (skipped) : {}".format(skipped_no_reference))
if TARGET_LABELS is not None:
    print("  Not in TARGET_LABELS         : {}".format(skipped_not_targeted))
print("")
print("Next: visually inspect these cameras in the 3D view / Reference pane before")
print("building the orthomosaic. If positions look wrong, undo (Edit > Undo) and check")
print("chunk.euler_angles / antenna offset assumptions above.")
