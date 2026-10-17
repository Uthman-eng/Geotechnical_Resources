"""
Written with AI (Claude) from the BGS API notes in docs/bgs-api.md.
Lightly checked: tested on a sample area, not fully reviewed.
Reviewed by: ____________   Date: ____________

Find every BGS borehole record in an area and download the scanned logs as PDFs.

Uses the free British Geological Survey OGC API (https://ogcapi.bgs.ac.uk):
    - onshoreboreholeindex : the Single Onshore Borehole Index (SOBI) - historical
                             borehole records, most with a scanned log PDF
    - agsboreholeindex     : boreholes that have digital AGS data held by BGS

What it does:
    1. Searches both indexes inside your bounding box (all pages of results)
    2. Saves the results to CSV (with eastings/northings, depth, year, links)
    3. Downloads the scanned log PDF for each borehole (optional)
    4. Merges all PDFs into one file with a bookmark per borehole (optional)

The borehole CSV has easting/northing columns, so it can be plotted straight
into AutoCAD with ../autocad-plotting/plot_points_to_autocad.py
(NAME_COLUMN="reference", X_COLUMN="easting", Y_COLUMN="northing").

Usage:
    1. Edit the SETTINGS block below (at minimum: BBOX).
    2. Run:  python bgs_borehole_search.py

Only the Python standard library is needed, except:
    - pyproj  if you give the area in eastings/northings (BBOX_CRS = "EPSG:27700")
    - pypdf   if MERGE_PDFS = True

Data: contains British Geological Survey materials (c) UKRI. Check the BGS
terms of use before re-publishing logs, and keep downloads reasonable.
"""

import csv
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ============================== SETTINGS ==============================
# Edit these values for your project.

# Search area as (west, south, east, north).
#   In lat/long (BBOX_CRS = "EPSG:4326"):          (-1.47, 53.27, -1.37, 53.29)
#   In eastings/northings (BBOX_CRS = "EPSG:27700"): (437000, 375000, 439000, 377000)
# Tip: get lat/long by right-clicking in Google Maps, or draw a box in
# Google Earth and read the corner coordinates.
BBOX = (437500, 375000, 439000, 376500)     # <-- your site area
BBOX_CRS = "EPSG:27700"                      # "EPSG:27700" (E/N) or "EPSG:4326" (lat/long)

OUTPUT_FOLDER = "outputs/bgs_site_search"   # <-- where CSVs and PDFs are saved

SEARCH_AGS_INDEX = True  # also list boreholes that have AGS data at BGS

DOWNLOAD_PDFS = True     # download the scanned log for each borehole
MAX_DOWNLOADS = 50       # safety limit - a big area can have thousands of logs
MERGE_PDFS = True        # combine all downloads into one PDF (needs: pip install pypdf)
DELAY_SECONDS = 0.5      # pause between downloads, to be polite to the BGS server
# =====================================================================

API_ROOT = "https://ogcapi.bgs.ac.uk/collections"
PAGE_SIZE = 500
HEADERS = {"User-Agent": "Geotechnical_Resources bgs_borehole_search.py"}

SOBI_FIELDS = [
    "reference", "name", "easting", "northing", "grid_ref", "length", "year_known",
    "precision", "bgs_id", "scan_url", "ags_log_url", "water_well_ref", "lon", "lat",
]
AGS_FIELDS = [
    "loca_id", "proj_name", "x", "y", "loca_fdep", "ags_log_url", "dad_item_url",
    "bgs_loca_id", "lon", "lat",
]


def bbox_to_wgs84(bbox, crs):
    """The BGS API only accepts lat/long boxes, so convert E/N if needed."""
    if crs.upper() in ("EPSG:4326", "WGS84"):
        return bbox
    from pyproj import Transformer

    t = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    west, south, east, north = t.transform_bounds(*bbox)
    return (west, south, east, north)


def fetch_json(url):
    with urlopen(Request(url, headers=HEADERS), timeout=60) as resp:
        return json.load(resp)


def search_collection(collection, bbox_wgs84):
    """Return every feature in the bbox, following pages of results."""
    features, offset = [], 0
    while True:
        params = {
            "f": "json",
            "limit": PAGE_SIZE,
            "offset": offset,
            "bbox": ",".join(f"{v:.6f}" for v in bbox_wgs84),
        }
        data = fetch_json(f"{API_ROOT}/{collection}/items?{urlencode(params)}")
        page = data.get("features", [])
        features.extend(page)
        matched = data.get("numberMatched", len(features))
        print(f"  {collection}: {len(features)} / {matched}")
        if not page or len(features) >= matched:
            return features
        offset += len(page)


def flatten(feature):
    """GeoJSON feature -> flat dict with lon/lat added."""
    row = dict(feature.get("properties", {}))
    coords = (feature.get("geometry") or {}).get("coordinates") or [None, None]
    row["lon"], row["lat"] = coords[0], coords[1]
    return row


def write_csv(rows, fields, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"-> saved {len(rows)} records to {path}")


def safe_filename(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")


def download_pdf(url, path):
    with urlopen(Request(url, headers=HEADERS), timeout=120) as resp:
        if "pdf" not in resp.headers.get("Content-Type", ""):
            raise ValueError(f"not a PDF ({resp.headers.get('Content-Type')})")
        path.write_bytes(resp.read())


def download_scans(rows, folder):
    """Download each borehole's scanned log. Returns [(label, path), ...]."""
    folder.mkdir(parents=True, exist_ok=True)
    with_scans = [r for r in rows if r.get("scan_url")]
    print(f"\n{len(with_scans)} of {len(rows)} boreholes have a scanned log.")
    if len(with_scans) > MAX_DOWNLOADS:
        print(f"Only downloading the first {MAX_DOWNLOADS} (increase MAX_DOWNLOADS for more).")

    downloaded = []
    for i, r in enumerate(with_scans[:MAX_DOWNLOADS], start=1):
        label = f"{r.get('reference')} - {r.get('name') or ''}".strip(" -")
        path = folder / f"{safe_filename(r.get('reference'))}_{int(r.get('bgs_id') or 0)}.pdf"
        if path.exists():
            print(f"  [{i}] exists, skipping: {path.name}")
            downloaded.append((label, path))
            continue
        try:
            download_pdf(r["scan_url"], path)
            print(f"  [{i}] downloaded {path.name}")
            downloaded.append((label, path))
        except (HTTPError, URLError, ValueError, TimeoutError) as e:
            print(f"  [{i}] FAILED {r.get('reference')}: {e}")
        time.sleep(DELAY_SECONDS)
    return downloaded


def merge_pdfs(items, out_path):
    """Combine PDFs into one, with a bookmark per borehole."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    for label, path in items:
        try:
            writer.append(str(path), outline_item=label)
        except Exception as e:
            print(f"  could not add {path.name}: {e}")
    with open(out_path, "wb") as f:
        writer.write(f)
    print(f"-> merged {len(items)} logs into {out_path}")


def main():
    out = Path(OUTPUT_FOLDER)
    out.mkdir(parents=True, exist_ok=True)

    bbox = bbox_to_wgs84(BBOX, BBOX_CRS)
    print(f"Searching BGS in bbox (lon/lat): {', '.join(f'{v:.5f}' for v in bbox)}")

    sobi = [flatten(f) for f in search_collection("onshoreboreholeindex", bbox)]
    sobi.sort(key=lambda r: str(r.get("reference")))
    write_csv(sobi, SOBI_FIELDS, out / "bgs_boreholes.csv")

    if SEARCH_AGS_INDEX:
        ags = [flatten(f) for f in search_collection("agsboreholeindex", bbox)]
        write_csv(ags, AGS_FIELDS, out / "bgs_ags_boreholes.csv")
        if ags:
            print("   (AGS data: open the ags_log_url / dad_item_url links to view or request it)")

    if DOWNLOAD_PDFS and sobi:
        downloaded = download_scans(sobi, out / "scans")
        if MERGE_PDFS and downloaded:
            merge_pdfs(downloaded, out / "bgs_borehole_logs_combined.pdf")

    print("\nDone.")


if __name__ == "__main__":
    main()
