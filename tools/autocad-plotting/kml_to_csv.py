"""
KML (Google Earth) -> CSV of points with British National Grid coordinates.

Reads every point in a Google Earth .kml file (including points inside
folders), keeps the placemark name and converts the coordinates from
WGS84 lat/long (EPSG:4326) to British National Grid (EPSG:27700).

The output CSV can be fed straight into plot_points_to_autocad.py.

Usage:
    1. Export your points from Google Earth: right-click folder > "Save Place As" > .kml
    2. Edit the SETTINGS block below.
    3. Run:  python kml_to_csv.py
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import Transformer

# ============================== SETTINGS ==============================
# Edit these values for your project.

INPUT_KML = "examples/sample_locations.kml"    # <-- path to your .kml file
OUTPUT_CSV = "outputs/points_from_kml.csv"        # <-- where to save the CSV

# Coordinate system to convert to. 27700 = British National Grid (OSGB36).
# Use e.g. "EPSG:2157" for Irish Transverse Mercator.
TARGET_CRS = "EPSG:27700"

# Number of decimal places to keep on eastings/northings (3 = millimetres).
DECIMALS = 3
# =====================================================================


def read_all_kml_layers(kml_path):
    """Read every layer (Google Earth folder) in a KML into one GeoDataFrame.

    gpd.read_file() on its own only reads the FIRST folder in a KML, which
    is a common reason points go "missing".
    """
    try:
        layers = gpd.list_layers(kml_path)["name"].tolist()
    except Exception:
        layers = [None]  # older geopandas: fall back to the default layer

    frames = []
    for layer in layers:
        gdf = gpd.read_file(kml_path, layer=layer) if layer else gpd.read_file(kml_path)
        if not gdf.empty:
            gdf["folder"] = layer or ""
            frames.append(gdf)

    if not frames:
        raise ValueError(f"No features found in {kml_path}")

    combined = pd.concat(frames, ignore_index=True)
    return gpd.GeoDataFrame(combined, geometry="geometry", crs=frames[0].crs or "EPSG:4326")


def kml_to_points_dataframe(kml_path, target_crs=TARGET_CRS, decimals=DECIMALS):
    """Return a DataFrame with Name, folder, lon, lat, easting, northing."""
    gdf = read_all_kml_layers(kml_path)

    # Tidy column names (KML exports sometimes have 'Name' / 'name' / stray spaces)
    gdf.columns = [c.strip().lower() if c != "geometry" else c for c in gdf.columns]

    points = gdf[gdf.geometry.geom_type == "Point"].copy()
    skipped = len(gdf) - len(points)
    if skipped:
        print(f"Skipped {skipped} non-point features (lines/polygons).")

    points["lon"] = points.geometry.x
    points["lat"] = points.geometry.y

    transformer = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)
    easting, northing = transformer.transform(points["lon"].values, points["lat"].values)
    points["easting"] = pd.Series(easting, index=points.index).round(decimals)
    points["northing"] = pd.Series(northing, index=points.index).round(decimals)

    points = points.rename(columns={"name": "Name"})
    if "Name" not in points.columns:
        points["Name"] = [f"PT{i + 1}" for i in range(len(points))]

    return pd.DataFrame(points[["Name", "folder", "lon", "lat", "easting", "northing"]])


def main():
    if not Path(INPUT_KML).exists():
        print(f"KML not found: {INPUT_KML}  (edit INPUT_KML in the SETTINGS block)")
        return

    df = kml_to_points_dataframe(INPUT_KML)
    print(f"Found {len(df)} points:")
    print(df.to_string(index=False))

    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
