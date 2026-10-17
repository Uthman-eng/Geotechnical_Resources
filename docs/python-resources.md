[← Back to main README](../README.md)

# Python resources for geotechnical engineering / engineering geology

Short notes and starter snippets for each library. The official documentation is very good, so for full details follow the links. Most of these work alongside the standard data libraries (`numpy`, `pandas`, `matplotlib`).

## Coordinate conversion: [pyproj](https://pyproj4.github.io/pyproj/stable/)

Converts between coordinate systems, e.g. lat/long ↔ British National Grid eastings/northings.

```python
from pyproj import Transformer

# lat/long (WGS84) -> eastings/northings (British National Grid)
t = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
easting, northing = t.transform(lon, lat)       # note: longitude first

# and back again
t_back = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
lon, lat = t_back.transform(easting, northing)
```

- Use `always_xy=True` so the order is always (x, y) = (longitude, latitude) or (easting, northing). Without it, the axis order changes between coordinate systems and is easy to get wrong.
- Without the OSTN15 grid file, conversions are good to about 1 m. Rounding coordinates (fewer decimal places) also adds small errors.

## Geospatial data / Google Earth: [GeoPandas](https://geopandas.org/)

Reads and writes KML, shapefiles, GeoJSON, GeoPackage, etc. into a pandas-like table with a geometry column. Google Earth files must be `.kml`, not `.kmz` (a `.kmz` is a zipped `.kml`).

```python
import geopandas as gpd

gi = gpd.read_file("GI_Data.kml")            # reads the FIRST folder only
layers = gpd.list_layers("GI_Data.kml")      # list all folders in the file

print("Rows & columns:", gi.shape)
print("Columns:", list(gi.columns))
print(gi.isnull().sum())

gi_bng = gi.to_crs("EPSG:27700")             # convert the whole layer to BNG
```

Full example: [`kml_to_csv.py`](../tools/autocad-plotting/kml_to_csv.py)

## AGS data: [python-ags4](https://pypi.org/project/python-ags4/) ([source](https://gitlab.com/ags-data-format-wg/ags-python-library))

Reads AGS4 files into clean pandas tables without OpenGround or gINT. It can also check files against the AGS rules and write AGS files.

```python
from python_ags4 import AGS4

tables, headings = AGS4.AGS4_to_dataframe("data.ags")
loca = AGS4.convert_to_numeric(tables["LOCA"])   # drops UNIT/TYPE rows, makes numbers numeric

errors = AGS4.check_file("data.ags")             # AGS4 rule checker
```

Full example: [`ags_summary.py`](../tools/ags-analysis/ags_summary.py). AGS format: [AGS4 data format standard](https://www.ags.org.uk/data-format/ags4-data-format/)

## AutoCAD: [pyautocad](https://pyautocad.readthedocs.io/)

Controls a running AutoCAD (Windows, full AutoCAD, not LT) from Python. Reference: [AutoCAD ActiveX documentation](https://help.autodesk.com/view/OARX/2025/ENU/). The connection can sometimes be unreliable, so wrap calls in `try/except`.

```python
from pyautocad import Autocad, APoint

acad = Autocad(create_if_not_exists=False)   # use the AutoCAD that's already open
model = acad.ActiveDocument.ModelSpace
model.AddCircle(APoint(438100, 376040), 1.0)
model.AddText("BH01", APoint(438101.5, 376041.5), 2.5)
```

Connection test: [`check_autocad_connection.py`](../tools/autocad-plotting/check_autocad_connection.py)

## Other useful libraries

| Library | Use |
|---|---|
| [ezdxf](https://ezdxf.readthedocs.io/) | Writes DXF drawings **without AutoCAD** (works on Mac/Linux, no COM issues) |
| [simplekml](https://simplekml.readthedocs.io/) | Creates KML files, e.g. to view BGS boreholes or GI locations in Google Earth |
| [folium](https://python-visualization.github.io/folium/) | Interactive web maps (HTML) of site data |
| [groundhog](https://groundhog.readthedocs.io/) | Geotechnical calculations and correlations library |
| [openpyxl](https://openpyxl.readthedocs.io/) | Reads and writes Excel files (used by `pandas.to_excel`) |

## Useful data sources (UK)

| Source | What |
|---|---|
| [BGS OGC API](https://ogcapi.bgs.ac.uk/collections) | Boreholes, geology, landslides, mine plans. See [bgs-api.md](bgs-api.md) |
| [BGS GeoIndex](https://www.bgs.ac.uk/map-viewers/geoindex-onshore/) | Map viewer for BGS data |
| [DEFRA Survey Data (LiDAR)](https://environment.data.gov.uk/survey) | Free LiDAR DTM/DSM for England |
| [Grid Reference Finder](https://gridreferencefinder.com/) | Quick checks of easting/northing ↔ lat/long |
