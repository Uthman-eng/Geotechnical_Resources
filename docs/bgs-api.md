[← Back to main README](../README.md)

# BGS OGC API: quick guide

The British Geological Survey (BGS) publishes free datasets through an OGC API at <https://ogcapi.bgs.ac.uk>. You can open a request in a web browser, use it in Excel (*Data → From Web*), or call it from Python (see [`bgs_borehole_search.py`](../tools/bgs-data/bgs_borehole_search.py)).

## Request format

```
https://ogcapi.bgs.ac.uk/collections/{collection}/items?f={format}&limit={number_of_records}&bbox={west},{south},{east},{north}
```

| Parameter | Meaning |
|---|---|
| `{collection}` | Dataset name (see the table below) |
| `f` | Output format: `csv`, `json` (GeoJSON, which opens in QGIS) or `html` (view in a browser) |
| `limit` | Maximum number of records to return. **Defaults to 10** if left out |
| `offset` | Skip this many records (used to page through large results) |
| `bbox` | Search box as **west, south, east, north** in **WGS84 lat/long** (min longitude, min latitude, max longitude, max latitude). The API does not accept eastings/northings, so convert them first |

**Example: borehole records near Chesterfield, as CSV**

<https://ogcapi.bgs.ac.uk/collections/onshoreboreholeindex/items?f=csv&limit=100&bbox=-1.47,53.27,-1.37,53.29>

Each JSON response includes `numberMatched` (the total number of records in the area). If it's higher than your `limit`, page through with `offset`. The Python script does this for you.

## Useful collections for ground engineering

| Collection | What it is |
|---|---|
| `onshoreboreholeindex` | Single Onshore Borehole Index (SOBI). Includes `scan_url`, a direct link to the scanned log PDF |
| `agsboreholeindex` | Boreholes where BGS holds digital AGS data |
| `bgsgeology625kbedrock` | 1:625 000 bedrock geology (regional only, too coarse for site scale) |
| `bgsgeology625ksuperficial` | 1:625 000 superficial deposits |
| `bgsgeology625kfaults` | 1:625 000 faults |
| `landslideindex` | National Landslide Database index |
| `mine_plans` | Index of BGS-held mine plans |
| `recentearthquakes`, `historicalearthquakes` | Earthquake records |
| `offshore-sample-geotechnical-data` | Offshore geotechnical sample data |
| `scanned-maps-250k` (and others) | Scanned geological map sheets |

Full list: <https://ogcapi.bgs.ac.uk/collections>

## Other BGS sources (web viewers)

- [GeoIndex Onshore](https://www.bgs.ac.uk/map-viewers/geoindex-onshore/): boreholes, 1:50k geology, and many other layers on one map
- [BGS Geology Viewer](https://www.bgs.ac.uk/map-viewers/bgs-geology-viewer/): 1:50k bedrock and superficial geology

Data © UKRI. See the [BGS terms of use](https://www.bgs.ac.uk/legal-and-policy/terms-of-use/).
