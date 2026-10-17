"""
Plot a list of points (e.g. borehole / trial pit locations) into AutoCAD.

Reads a CSV of point names + coordinates and, for each point, draws any of:
    - a circle marker
    - a text label
    - an inserted block (e.g. your company borehole symbol) with its
      attribute set to the point name

Works with:
    - eastings/northings already in British National Grid  (INPUT_CRS = "EPSG:27700")
    - lat/long from Google Earth / GPS                       (INPUT_CRS = "EPSG:4326")
    - the CSV made by kml_to_csv.py, ags_summary.py or bgs_borehole_search.py

Requirements:
    - Windows with AutoCAD (full AutoCAD, not LT - LT has no COM/ActiveX API)
    - AutoCAD open with the target drawing active
    - pip install pyautocad pandas pyproj

Set DRY_RUN = True to test the CSV / coordinates without AutoCAD (works on Mac/Linux).

Usage:
    1. Edit the SETTINGS block below.
    2. Open your drawing in AutoCAD.
    3. Run:  python plot_points_to_autocad.py
"""

from pathlib import Path

import pandas as pd

# ============================== SETTINGS ==============================
# Edit these values for your project.

INPUT_CSV = "examples/sample_points_bng.csv"   # <-- your CSV of points

# Column names in your CSV
NAME_COLUMN = "Name"       # <-- e.g. "LOCA_ID", "Name", "BH"
X_COLUMN = "easting"       # <-- e.g. "LOCA_NATE", "easting", "lon"
Y_COLUMN = "northing"      # <-- e.g. "LOCA_NATN", "northing", "lat"

# Coordinate system of the CSV and of the drawing.
#   CSV in eastings/northings -> INPUT_CRS = "EPSG:27700"
#   CSV in lat/long           -> INPUT_CRS = "EPSG:4326"  (converted automatically)
INPUT_CRS = "EPSG:27700"
DRAWING_CRS = "EPSG:27700"

# What to draw
DRAW_CIRCLE = True
CIRCLE_RADIUS = 1.0        # drawing units (normally metres)

DRAW_TEXT = True
TEXT_HEIGHT = 2.5
TEXT_OFFSET = (1.5, 1.5)   # (x, y) offset of label from the point

# Block insert - the block must ALREADY exist in the drawing.
# Set INSERT_BLOCK = False if you don't have one.
INSERT_BLOCK = False
BLOCK_NAME = "BOREHOLE-A"  # <-- EXACT block name in your drawing
ATTRIBUTE_TAG = "BH_No"    # <-- attribute tag to fill with the point name
BLOCK_SCALE = 1.0

# Layer to put everything on (created if missing). None = current layer.
LAYER_NAME = "GI_LOCATIONS"

# True = print what would be drawn, don't touch AutoCAD.
DRY_RUN = False
# =====================================================================


def load_points(csv_path):
    """Load the CSV and return (names, x, y) in the drawing coordinate system."""
    df = pd.read_csv(csv_path)

    missing = [c for c in (NAME_COLUMN, X_COLUMN, Y_COLUMN) if c not in df.columns]
    if missing:
        raise KeyError(
            f"Missing column(s) {missing} in {csv_path}. "
            f"Columns found: {list(df.columns)}. Edit NAME/X/Y_COLUMN in SETTINGS."
        )

    df = df.dropna(subset=[X_COLUMN, Y_COLUMN])
    x = df[X_COLUMN].astype(float).values
    y = df[Y_COLUMN].astype(float).values

    if INPUT_CRS != DRAWING_CRS:
        from pyproj import Transformer

        transformer = Transformer.from_crs(INPUT_CRS, DRAWING_CRS, always_xy=True)
        x, y = transformer.transform(x, y)

    return df[NAME_COLUMN].astype(str).values, x, y


def connect_to_autocad():
    """Connect to an already-open AutoCAD session and return (doc, modelspace)."""
    from pyautocad import Autocad  # imported here so DRY_RUN works without it

    acad = Autocad(create_if_not_exists=False)
    doc = acad.ActiveDocument
    print(f"Connected to AutoCAD drawing: {doc.Name}")
    return doc, doc.ModelSpace


def set_layer(entity, layer_name):
    if layer_name and entity is not None:
        entity.Layer = layer_name


def set_block_attribute(block_ref, tag, value):
    """Fill the attribute with the given tag. Returns True if found."""
    for att in block_ref.GetAttributes():
        if str(att.TagString).strip().lower() == tag.lower():
            att.TextString = str(value)
            return True
    return False


def plot_points(names, xs, ys, doc=None, model=None):
    from_point = None
    if not DRY_RUN:
        from pyautocad import APoint

        from_point = APoint
        if LAYER_NAME:
            doc.Layers.Add(LAYER_NAME)  # returns the existing layer if already there

    errors = 0
    for i, (name, x, y) in enumerate(zip(names, xs, ys), start=1):
        print(f"{i:>4}. {name:<15} x={x:.3f}  y={y:.3f}")
        if DRY_RUN:
            continue

        centre = from_point(float(x), float(y), 0)
        try:
            if DRAW_CIRCLE:
                set_layer(model.AddCircle(centre, CIRCLE_RADIUS), LAYER_NAME)

            if DRAW_TEXT:
                label_pt = from_point(float(x) + TEXT_OFFSET[0], float(y) + TEXT_OFFSET[1], 0)
                set_layer(model.AddText(name, label_pt, TEXT_HEIGHT), LAYER_NAME)

            if INSERT_BLOCK:
                block = model.InsertBlock(centre, BLOCK_NAME, BLOCK_SCALE, BLOCK_SCALE, BLOCK_SCALE, 0.0)
                set_layer(block, LAYER_NAME)
                if ATTRIBUTE_TAG and not set_block_attribute(block, ATTRIBUTE_TAG, name):
                    print(f"      attribute '{ATTRIBUTE_TAG}' not found on block '{BLOCK_NAME}'")
        except Exception as e:  # AutoCAD COM errors are often transient - keep going
            errors += 1
            print(f"      ERROR plotting {name}: {e}")

    return errors


def main():
    if not Path(INPUT_CSV).exists():
        print(f"CSV not found: {INPUT_CSV}  (edit INPUT_CSV in the SETTINGS block)")
        return

    names, xs, ys = load_points(INPUT_CSV)
    print(f"Loaded {len(names)} points from {INPUT_CSV}")

    doc = model = None
    if DRY_RUN:
        print("DRY_RUN = True -> not connecting to AutoCAD\n")
    else:
        try:
            doc, model = connect_to_autocad()
        except Exception as e:
            print(f"Could not connect to AutoCAD: {e}")
            print("Is AutoCAD open with a drawing active? Try check_autocad_connection.py")
            return

    errors = plot_points(names, xs, ys, doc, model)

    if not DRY_RUN:
        doc.Regen(1)  # acAllViewports
        print("\nTip: type ZOOM > EXTENTS in AutoCAD to see the points.")
    print(f"\nDone. {len(names)} points, {errors} errors.")


if __name__ == "__main__":
    main()
