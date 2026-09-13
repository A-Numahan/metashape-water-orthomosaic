import Metashape
import math
import os
import statistics

# ============================================================
# DJI M3M WATER ALIGN V5
# RTK SPATIAL STRIP CLUSTERING
# GREEN BAND ONLY
#
# Designed for:
# - DJI Mavic 3 Multispectral
# - Water / very low texture imagery
# - RTK positions available
# - Multiple parallel flight lines
#
# Agisoft Metashape 2.x
# ============================================================

doc = Metashape.app.document
chunk = doc.chunk

if chunk is None:
    raise RuntimeError("No active chunk.")


# ============================================================
# SETTINGS
# ============================================================

# Match image with next N images in same strip
NEIGHBOR_COUNT = 3

# 1 = High
# 2 = Medium
# ใช้ 1 ก่อน ถ้า CUDA ยังมีปัญหาเปลี่ยนเป็น 2
DOWNSCALE = 1

KEYPOINT_LIMIT = 100000
KEYPOINT_LIMIT_PER_MPX = 0

# unlimited
TIEPOINT_LIMIT = 0

GUIDED_MATCHING = True
KEEP_KEYPOINTS = True
FILTER_STATIONARY_POINTS = False

# ------------------------------------------------------------
# STRIP CLUSTERING
# ------------------------------------------------------------

# multiplier สำหรับ auto-detect strip spacing
# ปกติ 0.35 - 0.55
STRIP_TOLERANCE_FACTOR = 0.45

# ถ้า strip มีภาพน้อยกว่านี้ จะไม่ใช้
MIN_CAMERAS_PER_STRIP = 5

# รวม strip ที่อยู่ใกล้กันผิดปกติหรือไม่
MERGE_CLOSE_STRIPS = True

# threshold เทียบกับ median strip spacing
MERGE_FACTOR = 0.35


# ============================================================
# FUNCTIONS
# ============================================================

def is_green_camera(cam):
    texts = []

    try:
        texts.append(cam.sensor.label.lower())
    except:
        pass

    try:
        texts.append(cam.label.lower())
    except:
        pass

    try:
        texts.append(
            os.path.basename(cam.photo.path).lower()
        )
    except:
        pass

    text = " ".join(texts)

    if "green" in text:
        return True

    if "_ms_g" in text:
        return True

    if "ms_g." in text:
        return True

    return False


def median(values):
    if not values:
        return 0.0
    return statistics.median(values)


# ============================================================
# START
# ============================================================

print("")
print("=" * 80)
print("DJI M3M WATER ALIGN V5")
print("RTK SPATIAL STRIP CLUSTERING")
print("=" * 80)

print("Total cameras in chunk:", len(chunk.cameras))


# ============================================================
# GET GREEN CAMERAS
# ============================================================

green_all = []

for cam in chunk.cameras:

    if not cam.enabled:
        continue

    if cam.photo is None:
        continue

    if is_green_camera(cam):
        green_all.append(cam)


print("Green detected:", len(green_all))

if len(green_all) == 0:
    raise RuntimeError("No Green cameras detected.")


# ============================================================
# GREEN WITH RTK
# ============================================================

green = []

for cam in green_all:

    try:
        loc = cam.reference.location
    except:
        loc = None

    if loc is not None:
        green.append(cam)


print("Green with RTK:", len(green))

if len(green) < 2:
    raise RuntimeError(
        "Not enough Green cameras with RTK coordinates."
    )


# ============================================================
# RESET OLD ALIGNMENT
# ============================================================

print("")
print("Resetting previous alignment...")

for cam in chunk.cameras:
    cam.transform = None


# ============================================================
# BUILD XY ARRAY
# ============================================================

points = []

for cam in green:

    loc = cam.reference.location

    points.append(
        (
            cam,
            float(loc.x),
            float(loc.y)
        )
    )


# ============================================================
# CALCULATE XY CENTROID
# ============================================================

mean_x = sum(p[1] for p in points) / len(points)
mean_y = sum(p[2] for p in points) / len(points)


# ============================================================
# PCA 2D
# Find major flight direction
# ============================================================

sxx = 0.0
syy = 0.0
sxy = 0.0

for _, x, y in points:

    dx = x - mean_x
    dy = y - mean_y

    sxx += dx * dx
    syy += dy * dy
    sxy += dx * dy


n = len(points)

sxx /= n
syy /= n
sxy /= n


# eigenvector of largest eigenvalue

trace = sxx + syy

det = (
    sxx * syy -
    sxy * sxy
)

disc = max(
    0.0,
    trace * trace / 4.0 - det
)

lambda1 = (
    trace / 2.0 +
    math.sqrt(disc)
)


if abs(sxy) > 1e-12:

    vx = lambda1 - syy
    vy = sxy

else:

    if sxx >= syy:
        vx = 1.0
        vy = 0.0
    else:
        vx = 0.0
        vy = 1.0


norm = math.sqrt(vx * vx + vy * vy)

vx /= norm
vy /= norm


# perpendicular vector

px = -vy
py = vx


heading = math.degrees(
    math.atan2(vx, vy)
)

if heading < 0:
    heading += 360


print("")
print("=" * 80)
print("PCA RESULT")
print("=" * 80)

print("Principal flight heading:", heading, "deg")
print("Along vector:", vx, vy)
print("Cross vector:", px, py)


# ============================================================
# PROJECT EACH CAMERA
# ============================================================

projected = []

for cam, x, y in points:

    dx = x - mean_x
    dy = y - mean_y

    along = (
        dx * vx +
        dy * vy
    )

    cross = (
        dx * px +
        dy * py
    )

    projected.append(
        {
            "cam": cam,
            "x": x,
            "y": y,
            "along": along,
            "cross": cross
        }
    )


# ============================================================
# ESTIMATE CROSS-TRACK SPACING
# ============================================================

cross_sorted = sorted(
    p["cross"]
    for p in projected
)

cross_gaps = []

for i in range(len(cross_sorted) - 1):

    gap = (
        cross_sorted[i + 1] -
        cross_sorted[i]
    )

    if gap > 0:
        cross_gaps.append(gap)


# ------------------------------------------------------------
# camera-to-camera differences within same strip
# are very small
# strip-to-strip gap is much larger
#
# Find unusually large gaps
# ------------------------------------------------------------

if not cross_gaps:
    raise RuntimeError("Unable to calculate cross-track spacing.")


small_gap = median(cross_gaps)

large_candidates = [
    g for g in cross_gaps
    if g > small_gap * 5.0
]


if large_candidates:

    estimated_strip_spacing = median(
        large_candidates
    )

else:

    # fallback
    estimated_strip_spacing = (
        max(cross_sorted) -
        min(cross_sorted)
    ) / 20.0


cluster_tolerance = (
    estimated_strip_spacing *
    STRIP_TOLERANCE_FACTOR
)


print("")
print("=" * 80)
print("STRIP SPACING")
print("=" * 80)

print("Median small cross gap :", small_gap)
print("Estimated strip spacing:", estimated_strip_spacing)
print("Cluster tolerance      :", cluster_tolerance)


# ============================================================
# CLUSTER CROSS-TRACK VALUES
# ============================================================

projected_sorted = sorted(
    projected,
    key=lambda p: p["cross"]
)


raw_strips = []

current = [
    projected_sorted[0]
]

current_center = projected_sorted[0]["cross"]


for p in projected_sorted[1:]:

    diff = abs(
        p["cross"] -
        current_center
    )

    if diff <= cluster_tolerance:

        current.append(p)

        current_center = sum(
            q["cross"]
            for q in current
        ) / len(current)

    else:

        raw_strips.append(current)

        current = [p]

        current_center = p["cross"]


raw_strips.append(current)


print("")
print("Raw strips detected:", len(raw_strips))


# ============================================================
# REMOVE TINY STRIPS
# ============================================================

strips = []

for strip in raw_strips:

    if len(strip) >= MIN_CAMERAS_PER_STRIP:
        strips.append(strip)


print(
    "Valid strips >=",
    MIN_CAMERAS_PER_STRIP,
    "images:",
    len(strips)
)


# ============================================================
# OPTIONAL MERGE CLOSE STRIPS
# ============================================================

if MERGE_CLOSE_STRIPS and len(strips) > 1:

    centers = []

    for strip in strips:

        c = sum(
            p["cross"]
            for p in strip
        ) / len(strip)

        centers.append(c)


    center_gaps = []

    for i in range(len(centers) - 1):

        center_gaps.append(
            abs(
                centers[i + 1] -
                centers[i]
            )
        )


    median_center_gap = median(center_gaps)

    merge_threshold = (
        median_center_gap *
        MERGE_FACTOR
    )


    merged = []

    current = strips[0]

    for i in range(1, len(strips)):

        prev_center = sum(
            p["cross"]
            for p in current
        ) / len(current)

        this_center = sum(
            p["cross"]
            for p in strips[i]
        ) / len(strips[i])

        if abs(
            this_center -
            prev_center
        ) < merge_threshold:

            current = (
                current +
                strips[i]
            )

        else:

            merged.append(current)
            current = strips[i]


    merged.append(current)

    strips = merged


# ============================================================
# SORT CAMERAS INSIDE EACH STRIP
# ============================================================

flight_lines = []

for strip in strips:

    line = sorted(
        strip,
        key=lambda p: p["along"]
    )

    cams = [
        p["cam"]
        for p in line
    ]

    flight_lines.append(cams)


# ============================================================
# PRINT FLIGHT LINES
# ============================================================

print("")
print("=" * 80)
print("FINAL FLIGHT LINES")
print("=" * 80)

print("Flight lines:", len(flight_lines))


for i, line in enumerate(flight_lines):

    cross_values = []

    for cam in line:

        for p in projected:

            if p["cam"] == cam:
                cross_values.append(
                    p["cross"]
                )
                break


    center = (
        sum(cross_values) /
        len(cross_values)
    )

    print(
        "Line {:02d}: {:3d} images | cross = {:.3f}".format(
            i + 1,
            len(line),
            center
        )
    )


# ============================================================
# CREATE PAIRS
# ============================================================

pair_set = set()

for line in flight_lines:

    for i in range(len(line)):

        for offset in range(
            1,
            NEIGHBOR_COUNT + 1
        ):

            j = i + offset

            if j >= len(line):
                break

            k1 = line[i].key
            k2 = line[j].key

            pair_set.add(
                tuple(
                    sorted(
                        (k1, k2)
                    )
                )
            )


pairs = list(pair_set)


print("")
print("Generated Green-Green pairs:", len(pairs))


# ============================================================
# MATCH
# ============================================================

print("")
print("=" * 80)
print("MATCHING GREEN BAND")
print("=" * 80)


chunk.matchPhotos(

    downscale=DOWNSCALE,

    generic_preselection=False,
    reference_preselection=False,

    keypoint_limit=KEYPOINT_LIMIT,

    keypoint_limit_per_mpx=
        KEYPOINT_LIMIT_PER_MPX,

    tiepoint_limit=
        TIEPOINT_LIMIT,

    guided_matching=
        GUIDED_MATCHING,

    keep_keypoints=
        KEEP_KEYPOINTS,

    filter_stationary_points=
        FILTER_STATIONARY_POINTS,

    pairs=pairs,

    reset_matches=True
)


Metashape.app.update()


# ============================================================
# MATCH REPORT
# ============================================================

tp = chunk.tie_points

tracks = 0
projections = 0

if tp:

    try:
        tracks = len(tp.tracks)
    except:
        pass

    for cam in green:

        try:

            projections += len(
                tp.projections[cam]
            )

        except:
            pass


print("")
print("=" * 80)
print("MATCH RESULT")
print("=" * 80)

print("Tracks      :", tracks)
print("Projections :", projections)

if tracks > 0:

    print(
        "Average projections / track:",
        projections / tracks
    )


# ============================================================
# PROGRESSIVE ALIGNMENT BY STRIP
# ============================================================

print("")
print("=" * 80)
print("PROGRESSIVE STRIP ALIGNMENT")
print("=" * 80)


for idx, line in enumerate(flight_lines):

    print("")
    print(
        "Aligning strip {} / {} | {} images".format(
            idx + 1,
            len(flight_lines),
            len(line)
        )
    )

    try:

        chunk.alignCameras(

            cameras=line,

            min_image=2,

            adaptive_fitting=True,

            reset_alignment=False
        )

    except Exception as e:

        print(
            "Alignment error:",
            str(e)
        )


    aligned = sum(
        1
        for cam in line
        if cam.transform is not None
    )


    print(
        "Aligned:",
        aligned,
        "/",
        len(line)
    )

    Metashape.app.update()


# ============================================================
# SECOND PASS
# ============================================================

remaining = [
    cam
    for cam in green
    if cam.transform is None
]


if remaining:

    print("")
    print("=" * 80)
    print("SECOND PASS")
    print("=" * 80)

    print(
        "Remaining Green images:",
        len(remaining)
    )

    try:

        chunk.alignCameras(

            cameras=remaining,

            min_image=2,

            adaptive_fitting=True,

            reset_alignment=False
        )

    except Exception as e:

        print(
            "Second pass error:",
            str(e)
        )


Metashape.app.update()


# ============================================================
# FINAL REPORT
# ============================================================

green_aligned = sum(
    1
    for cam in green
    if cam.transform is not None
)

all_aligned = sum(
    1
    for cam in chunk.cameras
    if cam.transform is not None
)

valid_points = 0

if chunk.tie_points:

    try:

        valid_points = sum(
            1
            for p in chunk.tie_points.points
            if p.valid
        )

    except:
        pass


print("")
print("=" * 80)
print("M3M WATER ALIGN V5 FINISHED")
print("=" * 80)

print(
    "Green detected :",
    len(green_all)
)

print(
    "Green with RTK :",
    len(green)
)

print(
    "Flight lines   :",
    len(flight_lines)
)

print(
    "Pairs          :",
    len(pairs)
)

print(
    "Tracks         :",
    tracks
)

if tracks:

    print(
        "Multiplicity   :",
        projections / tracks
    )

print(
    "Green aligned  :",
    green_aligned,
    "/",
    len(green)
)

print(
    "All aligned    :",
    all_aligned,
    "/",
    len(chunk.cameras)
)

print(
    "3D Tie Points  :",
    valid_points
)

print("=" * 80)


Metashape.app.messageBox(

    "M3M Water Align V5 finished.\n\n"
    "Green: {}\n"
    "Flight lines: {}\n"
    "Pairs: {}\n"
    "Tracks: {}\n"
    "Green aligned: {} / {}\n"
    "3D Tie Points: {}".format(

        len(green),
        len(flight_lines),
        len(pairs),
        tracks,

        green_aligned,
        len(green),

        valid_points
    )
)