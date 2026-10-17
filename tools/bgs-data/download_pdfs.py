"""
Download a list of PDFs from links in a text file (one URL per line).

Handy for BGS borehole scan links copied from the BGS GeoIndex / Onshore
Borehole Index, or any other list of report links.
(To search an area and download automatically, use bgs_borehole_search.py.)

links.txt format:
    # lines starting with # are ignored
    https://api.bgs.ac.uk/sobi-scans/v1/borehole/scans/items/212929
    https://example.com/some/report.pdf

Usage:
    1. Paste your links into examples/links.txt (or point LINKS_FILE at your own file).
    2. Run:  python download_pdfs.py
"""

import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

# ============================== SETTINGS ==============================
LINKS_FILE = "examples/links.txt"         # <-- text file of URLs, one per line
OUTPUT_FOLDER = "outputs/downloaded_pdfs"  # <-- where PDFs are saved
DELAY_SECONDS = 0.5                        # pause between downloads
# =====================================================================

HEADERS = {"User-Agent": "Geotechnical_Resources download_pdfs.py"}


def read_links(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def filename_for(url, resp, index):
    """Use the server's filename if given, else the last part of the URL."""
    disposition = resp.headers.get("Content-Disposition", "")
    match = re.search(r'filename="?([^";]+)"?', disposition)
    name = match.group(1) if match else Path(unquote(urlparse(url).path)).name
    name = re.sub(r'[\\/:*?"<>|]+', "_", name or f"download_{index}")
    return name if name.lower().endswith(".pdf") else name + ".pdf"


def main():
    if not Path(LINKS_FILE).exists():
        print(f"Links file not found: {LINKS_FILE}")
        return

    links = read_links(LINKS_FILE)
    if not links:
        print(f"No links in {LINKS_FILE} - paste one URL per line and run again.")
        return

    out = Path(OUTPUT_FOLDER)
    out.mkdir(parents=True, exist_ok=True)

    ok = 0
    for i, url in enumerate(links, start=1):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=120) as resp:
                path = out / filename_for(url, resp, i)
                path.write_bytes(resp.read())
            print(f"[{i}/{len(links)}] downloaded {path.name}")
            ok += 1
        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            print(f"[{i}/{len(links)}] FAILED {url}: {e}")
        time.sleep(DELAY_SECONDS)

    print(f"\nDone. {ok} of {len(links)} downloaded to {out}")


if __name__ == "__main__":
    main()
