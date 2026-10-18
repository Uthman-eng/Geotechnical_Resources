[← Back to unchecked](../README.md) · [Main README](../../README.md)

# AGS detailed analysis ⚠️ UNCHECKED

> **AI-written (Claude), not yet reviewed.** Check the logic and results against the AGS data before relying on them.

Detailed analysis of an AGS4 file. It builds on the high-level [AGS analysis](../../tools/ags-analysis/README.md) tool.

**AGS4 files only.** AGS3 is not supported.

## Files

| File | Purpose |
|---|---|
| [`ags_detailed_analysis.py`](ags_detailed_analysis.py) | Strata summary, SPT by stratum, N vs depth plot, CSV/Excel exports, AGS checker |
| [`examples/ags_detailed_analysis.ipynb`](examples/ags_detailed_analysis.ipynb) | Notebook version, run cell by cell |

The example data is shared with the main tool: [`tools/ags-analysis/examples/sample.ags`](../../tools/ags-analysis/examples/sample.ags).

## Requirements

```bash
pip install python-ags4 pandas matplotlib openpyxl
```

## Usage

1. In `ags_detailed_analysis.py`, set `AGS_FILE` (and optionally `STRATA_COLUMN` or `RUN_AGS_CHECKER`)
2. Run `python ags_detailed_analysis.py`

## What to check when reviewing

| Function | What it does | Check |
|---|---|---|
| `load_ags` | Loads the file and converts columns to numbers | Values match the original file |
| `strata_summary` | Groups `GEOL` by stratum: holes, top depths, thickness = `GEOL_BASE − GEOL_TOP` | Grouping column suits the contractor's data |
| `assign_strata_to_spt` | Matches each SPT to the `GEOL` layer in the same hole where `GEOL_TOP ≤ ISPT_TOP < GEOL_BASE` | SPTs on a boundary go to the layer below. Unmatched SPTs are listed as a WARNING |
| `spt_summary` | Count and min/mean/max of `ISPT_NVAL` for each stratum | Blank N (refusals) are **skipped**, and no corrections such as N60 are applied |
| `plot_spt` | N vs depth, one line per hole, sorted by depth | Axes and units |

## Known limitations (to review)

The code runs correctly, but these results need engineering judgement:

1. **Bottom stratum thickness is only the proven thickness.** The last layer in each hole stops at the hole's final depth, so its "thickness" understates the real thickness (e.g. bedrock).
2. **SPT refusals are left out.** A blank `ISPT_NVAL` (refusal, details in `ISPT_REP`) isn't counted, so the N statistics in dense ground or rock come out too low.
3. **Strata tops are depths (m bgl), not levels (mAOD).** Holes with different ground levels (`LOCA_GL`) aren't directly comparable.

## Outputs (saved to `outputs/`)

| File | Contents |
|---|---|
| `<name>_locations.csv` | Hole IDs and coordinates, ready for [AutoCAD plotting](../../tools/autocad-plotting/README.md) |
| `<name>_strata_summary.csv` | Strata summary |
| `<name>_spt.csv` | SPTs with their matched stratum |
| `<name>_spt_vs_depth.png` | SPT N vs depth plot |
| `<name>_all_groups.xlsx` | Every AGS group on its own sheet |
| `<name>_ags_check.txt` | AGS rule check (if `RUN_AGS_CHECKER = True`) |

## Review status

| File | Written by | Reviewed by | Date | Notes |
|---|---|---|---|---|
| `ags_detailed_analysis.py` | AI-written | | | Fixed: plot sort order, unmatched SPT warning, missing-matplotlib message |
| `examples/ags_detailed_analysis.ipynb` | AI-written | | | |

Once it has been reviewed, it can move to [`tools/`](../../tools/).

## References

- [AGS4 data format standard and data dictionary](https://www.ags.org.uk/data-format/ags4-data-format/)
- [python-ags4 source and docs](https://gitlab.com/ags-data-format-wg/ags-python-library)
