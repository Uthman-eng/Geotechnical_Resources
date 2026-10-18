[← Back to main README](../../README.md)

# AGS analysis

High-level look at an **AGS4** ground investigation data file: what data is in it and what it looks like, without OpenGround or gINT.

**AGS4 files only.** AGS3 is not supported.

For a more detailed analysis (strata summary, SPT by stratum, plots, exports), see [unchecked/ags-analysis](../../unchecked/ags-analysis/README.md). That one is AI-written and not yet reviewed.

## Files

| File | Purpose |
|---|---|
| [`ags_summary.py`](ags_summary.py) | Lists every group, then previews the key groups (headings, units, first rows) |
| [`examples/ags_summary.ipynb`](examples/ags_summary.ipynb) | Notebook version: load, view LOCA/GEOL/ISPT, then every group |
| [`examples/sample.ags`](examples/sample.ags) | Small **fictional** AGS4 file to try it out |

## Requirements

```bash
pip install python-ags4 pandas
```

## Usage

1. In `ags_summary.py`, set `AGS_FILE`
2. Run `python ags_summary.py`

| Setting | What it does |
|---|---|
| `PREVIEW_ROWS` | Number of data rows shown for each key group |
| `KEY_GROUPS` | Groups to preview, e.g. `LOCA`, `GEOL`, `ISPT`, `SAMP`. Add any AGS group |
| `PRINT_ALL_GROUPS` | `True` = print every group in full |

## Example output

```
========== GROUPS IN FILE ==========
LOCA       4 rows
GEOL      11 rows
ISPT      13 rows

========== ISPT - SPT ==========
13 rows | headings: LOCA_ID, ISPT_TOP, ISPT_NVAL, ISPT_TYPE

HEADING LOCA_ID ISPT_TOP ISPT_NVAL ISPT_TYPE
   UNIT                m
   TYPE      ID      2DP       0DP        PA
   DATA    BH01     1.20         8         S

========== WSTD - Water strikes ==========
not in file
```

## Review status

| File | Written by | Reviewed by | Date | Notes |
|---|---|---|---|---|
| `ags_summary.py` | Original idea (Uthman), written up as a script by AI | | | |
| `examples/ags_summary.ipynb` | Original (Uthman) | | | |
| `examples/sample.ags` | AI-written, **fictional data** | | | |

## References

- [AGS4 data format standard and data dictionary](https://www.ags.org.uk/data-format/ags4-data-format/): explains every group and heading code
- [python-ags4 on PyPI](https://pypi.org/project/python-ags4/) · [source and docs](https://gitlab.com/ags-data-format-wg/ags-python-library)
- See also: [Python resources](../../docs/python-resources.md)
