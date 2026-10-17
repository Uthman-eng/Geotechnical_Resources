"""
High-level summary of an AGS4 ground investigation data file.

What it does:
    1. Lists every group (table) in the file with its number of data rows
    2. For the key groups (locations, strata, SPT, samples, lab tests...),
       shows the headings, units and first few rows - or "not in file"
    3. Optionally prints every group in full

For more detailed analysis (strata summary, SPT by stratum, plots, exports)
see ../../unchecked/ags-analysis/  (AI-written, not yet reviewed).

Usage:
    1. pip install python-ags4 pandas
    2. Edit the SETTINGS block below.
    3. Run:  python ags_summary.py
"""

from pathlib import Path

import pandas as pd
from python_ags4 import AGS4

# ============================== SETTINGS ==============================
AGS_FILE = "examples/sample.ags"   # <-- path to your .ags file

PREVIEW_ROWS = 5           # data rows to show for each key group
PRINT_ALL_GROUPS = False   # True = print every group in full

# Key groups to preview - add or remove any AGS group names
KEY_GROUPS = {
    "PROJ": "Project",
    "LOCA": "Locations",
    "GEOL": "Geology / strata",
    "ISPT": "SPT",
    "SAMP": "Samples",
    "WSTD": "Water strikes",
    "LNMC": "Moisture content",
    "LLPL": "Atterberg limits",
    "GRAT": "Particle size (grading)",
}
# =====================================================================

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)


def print_heading(text):
    print(f"\n{'=' * 10} {text} {'=' * 10}")


def main():
    if not Path(AGS_FILE).exists():
        print(f"AGS file not found: {AGS_FILE}  (edit AGS_FILE in the SETTINGS block)")
        return

    # Each table keeps the UNIT and TYPE rows at the top, followed by the DATA rows
    tables, headings = AGS4.AGS4_to_dataframe(AGS_FILE)

    print_heading("GROUPS IN FILE")
    for group, df in tables.items():
        print(f"{group:<5} {len(df) - 2:>6} rows")

    for group, description in KEY_GROUPS.items():
        print_heading(f"{group} - {description}")
        if group not in tables:
            print("not in file")
            continue
        df = tables[group]
        print(f"{len(df) - 2} rows | headings: {', '.join(headings[group][1:])}\n")
        print(df.head(PREVIEW_ROWS + 2).to_string(index=False))  # +2 = UNIT and TYPE rows

    if PRINT_ALL_GROUPS:
        for group, df in tables.items():
            print_heading(group)
            print(df.to_string(index=False))


if __name__ == "__main__":
    main()
