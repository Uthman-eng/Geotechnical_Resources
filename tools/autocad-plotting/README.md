[← Back to main README](../../README.md)

# AutoCAD plotting

Plot GI locations (boreholes, trial pits, CPTs) into AutoCAD from a Google Earth KML or a list of coordinates.

## Files

| File | Purpose |
|---|---|
| [`kml_to_csv.py`](kml_to_csv.py) | Google Earth `.kml` → CSV with lat/long **and** eastings/northings |
| [`plot_points_to_autocad.py`](plot_points_to_autocad.py) | CSV of points → circle, label and/or block in AutoCAD |
| [`check_autocad_connection.py`](check_autocad_connection.py) | Tests the Python ↔ AutoCAD connection |
| [`examples/`](examples/) | Sample KML and CSVs (fictional) and the step-by-step notebook [`kml_to_autocad.ipynb`](examples/kml_to_autocad.ipynb) |

## Requirements

- Windows with full AutoCAD (**not LT**, which has no ActiveX/COM API), open with your drawing active
- `pip install pyautocad pandas pyproj geopandas`

`kml_to_csv.py` and `DRY_RUN = True` also work on Mac/Linux.

## Usage

**A. Google Earth → AutoCAD**
1. In Google Earth: right-click your folder → **Save Place As…** → `.kml`
2. In `kml_to_csv.py`, set `INPUT_KML`, then run `python kml_to_csv.py`
3. Plot the CSV it creates using step B

**B. Coordinates → AutoCAD**
1. Make a CSV with a name column and two coordinate columns (see [`examples/sample_points_bng.csv`](examples/sample_points_bng.csv))
2. Set the SETTINGS in `plot_points_to_autocad.py`:

| Setting | Value |
|---|---|
| `INPUT_CSV` | Path to your CSV |
| `NAME_COLUMN`, `X_COLUMN`, `Y_COLUMN` | Your column headers |
| `INPUT_CRS` | `"EPSG:27700"` for eastings/northings, `"EPSG:4326"` for lat/long |
| `INSERT_BLOCK`, `BLOCK_NAME`, `ATTRIBUTE_TAG` | Your borehole block. It must already exist in the drawing, and the name must match exactly |
| `LAYER_NAME` | Layer to draw on (created if missing) |
| `DRY_RUN` | `True` = print coordinates only, so you can check them first |

3. Run `python plot_points_to_autocad.py`, then type `ZOOM` → `E` in AutoCAD.

**Column names for CSVs from the other tools:**

| Source | `NAME_COLUMN` | `X_COLUMN` | `Y_COLUMN` |
|---|---|---|---|
| [`kml_to_csv.py`](kml_to_csv.py) | `Name` | `easting` | `northing` |
| [AGS analysis](../ags-analysis/README.md) | `LOCA_ID` | `LOCA_NATE` | `LOCA_NATN` |
| [BGS data](../bgs-data/README.md) | `reference` | `easting` | `northing` |

## Troubleshooting

- **Points are far from the site:** `INPUT_CRS` is wrong.
- **Can't connect:** run `check_autocad_connection.py`. Press Esc in AutoCAD, and run Python and AutoCAD as the same user.
- **Accuracy:** the lat/long → BNG conversion is good to about 1 m. Use surveyed coordinates for setting out.

## Review status

> Lightly checked: written or tidied with AI, tested on the example data, not fully reviewed.

| File | Written by | Reviewed by | Date | Notes |
|---|---|---|---|---|
| `kml_to_csv.py` | Original (Uthman), restructured by AI | | | |
| `plot_points_to_autocad.py` | Original (Uthman), restructured by AI | | | |
| `check_autocad_connection.py` | Original (Uthman) | | | |
| `examples/kml_to_autocad.ipynb` | Rebuilt by AI from the original notebook | | | |

## References

- [pyautocad documentation](https://pyautocad.readthedocs.io/) · [source](https://github.com/reclosedev/pyautocad)
- [AutoCAD developer documentation (ActiveX reference)](https://help.autodesk.com/view/OARX/2025/ENU/)
- [pyproj documentation](https://pyproj4.github.io/pyproj/stable/)
- [GeoPandas documentation](https://geopandas.org/)
- See also: [Python resources](../../docs/python-resources.md)
