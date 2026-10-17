[← Back to main README](../../README.md)

# BGS data

Get every British Geological Survey (BGS) borehole record in a site area and download the scanned logs as PDFs, for desk studies.

## Files

| File | Purpose |
|---|---|
| [`bgs_borehole_search.py`](bgs_borehole_search.py) | Site area → borehole list (CSV), each scanned log, and **one combined PDF** with a bookmark for each borehole |
| [`download_pdfs.py`](download_pdfs.py) | Downloads a list of PDF links |
| [`examples/links.txt`](examples/links.txt) | Placeholder list of links for `download_pdfs.py` |

## Requirements

Standard Python, plus `pip install pyproj pypdf`. pyproj is only needed for areas given in eastings/northings, and pypdf only for merging the PDFs.

## Usage

**Search an area**
1. In `bgs_borehole_search.py`, set:
   - `BBOX = (west, south, east, north)`
   - `BBOX_CRS`: `"EPSG:27700"` for eastings/northings, `"EPSG:4326"` for lat/long
   - `MAX_DOWNLOADS`: safety limit on how many logs are downloaded (default 50)
2. Run `python bgs_borehole_search.py`

Saved to `outputs/bgs_site_search/`:

| File | Contents |
|---|---|
| `bgs_boreholes.csv` | Reference, name, easting/northing, depth, year, scan link. Ready for [AutoCAD plotting](../autocad-plotting/README.md) |
| `bgs_ags_boreholes.csv` | Boreholes where BGS holds AGS data |
| `scans/*.pdf` | One log per borehole |
| `bgs_borehole_logs_combined.pdf` | All logs in one PDF, bookmarked |

**Download a list of links**
1. Paste URLs into [`examples/links.txt`](examples/links.txt), one per line
2. Run `python download_pdfs.py`

## Notes

- An area in eastings/northings is converted to a slightly larger lat/long box, so a few holes just outside it may be included.
- Confidential boreholes, and those with no scan, have no PDF.
- Start with a small area. City centres can have thousands of records.

## Review status

> Lightly checked: written or tidied with AI, tested on the example data, not fully reviewed.

| File | Written by | Reviewed by | Date | Notes |
|---|---|---|---|---|
| `bgs_borehole_search.py` | AI-written, from the BGS API notes | | | |
| `download_pdfs.py` | Original (Uthman), cleaned up by AI | | | |

## References

- [BGS OGC API](https://ogcapi.bgs.ac.uk/collections) · [how to use it](../../docs/bgs-api.md)
- [BGS GeoIndex (map viewer)](https://www.bgs.ac.uk/map-viewers/geoindex-onshore/)
- [BGS terms of use](https://www.bgs.ac.uk/legal-and-policy/terms-of-use/). BGS data © UKRI
- [pypdf documentation](https://pypdf.readthedocs.io/)
