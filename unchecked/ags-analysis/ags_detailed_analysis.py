"""
!! UNCHECKED - AI-WRITTEN CODE (Claude), NOT YET REVIEWED !!
Check the logic and results before relying on them.
Reviewed by: ____________   Date: ____________

Detailed analysis of an AGS4 ground investigation data file (AGS4 only, not AGS3).
(For a quick high-level look, use ../../tools/ags-analysis/ags_summary.py)

What it does:
    1. Lists every group (table) in the file with its number of rows
    2. Prints project details (PROJ) and exploratory hole locations (LOCA)
    3. Summarises strata (GEOL): which holes hit each stratum, depths, thicknesses
    4. Matches each SPT result (ISPT) to its stratum and summarises N values
    5. Plots SPT N vs depth and saves it as a PNG
    6. Exports a locations CSV (ready for ../../tools/autocad-plotting/plot_points_to_autocad.py)
    7. Exports every group to one Excel workbook (one sheet per group)
    8. Optionally runs the AGS4 file checker and saves an error report

Usage:
    1. pip install python-ags4 pandas matplotlib openpyxl
    2. Edit the SETTINGS block below.
    3. Run:  python ags_detailed_analysis.py
"""

from pathlib import Path

import pandas as pd
from python_ags4 import AGS4

# ============================== SETTINGS ==============================
# Edit these values for your project.

AGS_FILE = "../../tools/ags-analysis/examples/sample.ags"   # <-- path to your .ags file
OUTPUT_FOLDER = "outputs"                                    # <-- where results are saved

# Which GEOL column to group strata by:
#   "GEOL_GEOL" = geology code/name (e.g. GLACIAL TILL)  - usually best
#   "GEOL_LEG"  = legend code (e.g. CLAY, MDST)
STRATA_COLUMN = "GEOL_GEOL"

PLOT_SPT = True            # save SPT N vs depth plot
EXPORT_EXCEL = True        # save all groups to an .xlsx
RUN_AGS_CHECKER = False    # run the official AGS4 rule checker (can be slow on big files)
# =====================================================================


def load_ags(path):
    """Load an AGS4 file into {group: DataFrame} with numbers converted to numeric.

    The raw tables keep the UNIT and TYPE rows at the top; convert_to_numeric
    uses them to convert columns and then drops them.
    """
    tables, headings = AGS4.AGS4_to_dataframe(path)
    numeric = {}
    for group, df in tables.items():
        try:
            numeric[group] = AGS4.convert_to_numeric(df)
        except Exception:
            numeric[group] = df.iloc[2:].reset_index(drop=True)  # drop UNIT/TYPE rows
        numeric[group] = numeric[group].drop(columns=["HEADING"], errors="ignore")
    return tables, headings, numeric


def print_heading(text):
    print(f"\n{'=' * 10} {text} {'=' * 10}")


def group_overview(tables):
    print_heading("GROUPS IN FILE")
    overview = pd.DataFrame(
        {"group": list(tables), "rows": [len(df) for df in tables.values()]}
    )
    print(overview.to_string(index=False))
    return overview


def strata_summary(geol, strata_col=STRATA_COLUMN):
    """One row per stratum: holes encountered, top depth range, thickness stats."""
    if strata_col not in geol.columns:
        print(f"'{strata_col}' not in GEOL - try STRATA_COLUMN = 'GEOL_LEG'")
        return pd.DataFrame()

    geol = geol.copy()
    geol["thickness"] = geol["GEOL_BASE"] - geol["GEOL_TOP"]
    summary = geol.groupby(strata_col).agg(
        holes=("LOCA_ID", "nunique"),
        top_min_m=("GEOL_TOP", "min"),
        top_max_m=("GEOL_TOP", "max"),
        thick_min_m=("thickness", "min"),
        thick_mean_m=("thickness", "mean"),
        thick_max_m=("thickness", "max"),
    )
    return summary.sort_values("top_min_m").round(2)


def assign_strata_to_spt(ispt, geol, strata_col=STRATA_COLUMN):
    """Add a stratum column to each SPT by matching hole + depth to GEOL."""
    ispt = ispt.copy()
    ispt["stratum"] = None
    if strata_col not in geol.columns:
        return ispt

    for idx, row in ispt.iterrows():
        match = geol[
            (geol["LOCA_ID"] == row["LOCA_ID"])
            & (geol["GEOL_TOP"] <= row["ISPT_TOP"])
            & (geol["GEOL_BASE"] > row["ISPT_TOP"])
        ]
        if not match.empty:
            ispt.at[idx, "stratum"] = match.iloc[0][strata_col]
    return ispt


def spt_summary(ispt):
    """N value stats per stratum."""
    return (
        ispt.dropna(subset=["ISPT_NVAL"])
        .groupby("stratum")["ISPT_NVAL"]
        .agg(tests="count", N_min="min", N_mean="mean", N_max="max")
        .round(1)
    )


def plot_spt(ispt, out_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plot (pip install matplotlib)")
        return False

    fig, ax = plt.subplots(figsize=(6, 8))
    for loca_id, df in ispt.groupby("LOCA_ID"):
        df = df.sort_values("ISPT_TOP")  # join points in depth order, not file order
        ax.plot(df["ISPT_NVAL"], df["ISPT_TOP"], "o-", label=loca_id)
    ax.set_xlim(left=0)
    ax.set_ylim(ispt["ISPT_TOP"].max() * 1.05, 0)  # depth increasing downwards from 0
    ax.xaxis.set_label_position("top")
    ax.xaxis.tick_top()
    ax.set_xlabel("SPT N value")
    ax.set_ylabel("Depth below ground level (m)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Hole", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return True


def main():
    if not Path(AGS_FILE).exists():
        print(f"AGS file not found: {AGS_FILE}  (edit AGS_FILE in the SETTINGS block)")
        return

    out = Path(OUTPUT_FOLDER)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(AGS_FILE).stem

    raw_tables, headings, t = load_ags(AGS_FILE)
    group_overview(t)

    if "PROJ" in t:
        print_heading("PROJECT")
        print(t["PROJ"].T.to_string(header=False))

    if "LOCA" in t:
        print_heading("LOCATIONS (LOCA)")
        cols = [c for c in ["LOCA_ID", "LOCA_TYPE", "LOCA_NATE", "LOCA_NATN", "LOCA_GL", "LOCA_FDEP"]
                if c in t["LOCA"].columns]
        print(t["LOCA"][cols].to_string(index=False))
        loca_csv = out / f"{stem}_locations.csv"
        t["LOCA"][cols].to_csv(loca_csv, index=False)
        print(f"-> saved {loca_csv}  (use with plot_points_to_autocad.py: "
              f"NAME_COLUMN='LOCA_ID', X_COLUMN='LOCA_NATE', Y_COLUMN='LOCA_NATN')")

    if "GEOL" in t:
        print_heading(f"STRATA SUMMARY (GEOL by {STRATA_COLUMN})")
        strata = strata_summary(t["GEOL"])
        print(strata.to_string())
        strata.to_csv(out / f"{stem}_strata_summary.csv")

    if "ISPT" in t:
        ispt = t["ISPT"]
        if "GEOL" in t:
            ispt = assign_strata_to_spt(ispt, t["GEOL"])
            print_heading("SPT N VALUES BY STRATUM")
            print(spt_summary(ispt).to_string())
            unmatched = ispt[ispt["stratum"].isna()]
            if not unmatched.empty:
                print(f"\nWARNING: {len(unmatched)} SPT(s) not matched to a stratum "
                      "(below the logged strata, or no GEOL for that hole) - not in the table above:")
                print(unmatched[["LOCA_ID", "ISPT_TOP", "ISPT_NVAL"]].to_string(index=False))
        ispt.to_csv(out / f"{stem}_spt.csv", index=False)
        if PLOT_SPT:
            png = out / f"{stem}_spt_vs_depth.png"
            if plot_spt(ispt, png):
                print(f"-> saved {png}")

    if EXPORT_EXCEL:
        xlsx = out / f"{stem}_all_groups.xlsx"
        with pd.ExcelWriter(xlsx) as writer:
            for group, df in t.items():
                df.to_excel(writer, sheet_name=group[:31], index=False)
        print(f"\n-> saved every group to {xlsx}")

    if RUN_AGS_CHECKER:
        print_heading("AGS4 FILE CHECK")
        errors = AGS4.check_file(AGS_FILE)
        report = out / f"{stem}_ags_check.txt"
        AGS4.write_error_report(errors, str(report))
        print(f"-> error report saved to {report}")


if __name__ == "__main__":
    main()
