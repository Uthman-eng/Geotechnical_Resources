from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import urlretrieve

for url in Path("links.txt").read_text().splitlines():
    url = url.strip()
    if url:
        name = Path(unquote(urlparse(url).path)).name or "download"
        if not name.lower().endswith(".pdf"):
            name += ".pdf"

        urlretrieve(url, name)
        print(f"Downloaded {name}")
