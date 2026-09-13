import Metashape
import math
import statistics

doc = Metashape.app.document
chunk = doc.chunk

if chunk is None:
    raise RuntimeError("No active chunk.")

# ============================================================
# WATER ALIGN BY SEQUENTIAL FLIGHT LINES
# Sequential / same-flight-line focused
# ============================================================

NEIGHBOR = 3
KEYPOINT_LIMIT = 300000
DOWNSCALE = 0

cameras = [
    c for c in chunk.cameras
    if c.enabled
    and c.photo is not None
    and c.reference.location is not None
]

print("=" * 70)
print("WATER ALIGN BY SEQUENTIAL FLIGHT LINES")
print("Cameras:", len(cameras))
print("=" * 70)

if len(cameras) < 2:
    raise RuntimeError(
        "At least two enabled cameras with reference locations are required."
    )

# ------------------------------------------------------------
# Determine normal spacing between consecutive images
# ------------------------------------------------------------

seq_dist = []

for i in range(len(cameras) - 1):

    a = cameras[i].reference.location
    b = cameras[i + 1].reference.location

    dx = a.x - b.x
    dy = a.y - b.y

    d = math.sqrt(dx * dx + dy * dy)

    seq_dist.append(d)

median_spacing = statistics.median(seq_dist)

# A large jump usually means turn / new flight line
LINE_BREAK_DISTANCE = median_spacing * 2.5

print("Median sequential spacing:", median_spacing)
print("Line-break threshold:", LINE_BREAK_DISTANCE)


# ------------------------------------------------------------
# Split cameras into flight lines
# ------------------------------------------------------------

flight_lines = []
current = [cameras[0]]

for i in range(1, len(cameras)):

    a = cameras[i - 1].reference.location
    b = cameras[i].reference.location

    dx = a.x - b.x
    dy = a.y - b.y

    d = math.sqrt(dx * dx + dy * dy)

    if d > LINE_BREAK_DISTANCE:

        if len(current) > 1:
            flight_lines.append(current)

        current = [cameras[i]]

    else:

        current.append(cameras[i])


if len(current) > 1:
    flight_lines.append(current)


print("Detected flight lines:", len(flight_lines))

for i, line in enumerate(flight_lines):
    print(
        "Line {:02d}: {} images".format(
            i + 1,
            len(line)
        )
    )


# ------------------------------------------------------------
# Build SAME-LINE pairs only
# ------------------------------------------------------------

pair_set = set()

for line in flight_lines:

    for i in range(len(line)):

        for offset in range(1, NEIGHBOR + 1):

            j = i + offset

            if j >= len(line):
                break

            k1 = line[i].key
            k2 = line[j].key

            pair_set.add(
                tuple(sorted((k1, k2)))
            )


pairs = list(pair_set)

print("")
print("Same-line pairs:", len(pairs))


# ------------------------------------------------------------
# RESET old camera alignment
# ------------------------------------------------------------

for cam in chunk.cameras:
    cam.transform = None


# ------------------------------------------------------------
# MATCH
# ------------------------------------------------------------

print("")
print("Matching...")
print("")

chunk.matchPhotos(

    downscale=DOWNSCALE,

    generic_preselection=False,
    reference_preselection=False,

    keypoint_limit=KEYPOINT_LIMIT,
    keypoint_limit_per_mpx=0,

    tiepoint_limit=0,

    keep_keypoints=True,

    guided_matching=True,

    filter_stationary_points=False,

    pairs=pairs,

    reset_matches=True
)


tp = chunk.tie_points

tracks = len(tp.tracks) if tp else 0

projections = 0

if tp:

    for cam in chunk.cameras:

        try:
            projections += len(tp.projections[cam])
        except:
            pass


print("")
print("Tracks:", tracks)
print("Projections:", projections)

if tracks:
    print(
        "Average multiplicity:",
        projections / tracks
    )


# ------------------------------------------------------------
# PROGRESSIVE ALIGNMENT
# ------------------------------------------------------------

print("")
print("=" * 70)
print("PROGRESSIVE ALIGNMENT")
print("=" * 70)


for line_id, line in enumerate(flight_lines):

    print("")
    print(
        "Aligning line {} / {} | {} cameras".format(
            line_id + 1,
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
            "Line alignment error:",
            e
        )

    aligned_line = sum(
        1 for c in line
        if c.transform is not None
    )

    print(
        "Aligned in this line:",
        aligned_line,
        "/",
        len(line)
    )

    Metashape.app.update()


# ------------------------------------------------------------
# FINAL REPORT
# ------------------------------------------------------------

aligned_total = sum(
    1 for c in chunk.cameras
    if c.transform is not None
)

valid_points = 0

if chunk.tie_points:

    valid_points = sum(
        1 for p in chunk.tie_points.points
        if p.valid
    )


print("")
print("=" * 70)
print("WATER ALIGN BY SEQUENTIAL FLIGHT LINES FINISHED")
print("=" * 70)
print(
    "Aligned cameras:",
    aligned_total,
    "/",
    len(chunk.cameras)
)

print(
    "Valid 3D Tie Points:",
    valid_points
)

print("=" * 70)


Metashape.app.messageBox(
    "Water align by sequential flight lines finished.\n\n"
    "Flight lines: {}\n"
    "Pairs: {}\n"
    "Aligned: {} / {}\n"
    "3D Tie Points: {}".format(
        len(flight_lines),
        len(pairs),
        aligned_total,
        len(chunk.cameras),
        valid_points
    )
)
