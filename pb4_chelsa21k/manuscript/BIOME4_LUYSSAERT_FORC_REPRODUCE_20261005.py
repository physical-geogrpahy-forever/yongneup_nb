"""Reproduce a diagnostic NPP/AGB audit; does not alter any model parameter.

Input: the ForC data/ directory at commit
407c520e6350917bca42e6bf7d5031dbcc551362 (2024-08-08).
Usage: python reproduce_luyssaert_ratios.py /path/to/ForC/data /output/dir
"""
from pathlib import Path
import json
import math
import sys

import pandas as pd


def year_range(row, suffix):
    start = pd.to_numeric(row[f"start.date_{suffix}"], errors="coerce")
    end = pd.to_numeric(row[f"end.date_{suffix}"], errors="coerce")
    point = pd.to_numeric(row[f"date_{suffix}"], errors="coerce")
    if pd.notna(start) and pd.notna(end):
        return math.floor(start), math.floor(end)
    if pd.notna(point):
        return math.floor(point), math.floor(point)
    return None


def time_status(row):
    npp, agb = year_range(row, "npp"), year_range(row, "agb")
    if npp is None or agb is None:
        return "unknown"
    if max(npp[0], agb[0]) <= min(npp[1], agb[1]):
        return "calendar_year_overlap"
    return "recorded_years_differ"


def map_pft(row):
    ecozone = str(row["FAO.ecozone"])
    veg = row["dominant.veg_npp"]
    if ecozone.startswith("Temperate "):
        return {"2TDB": 4, "2TEN": 5}.get(veg)
    if ecozone.startswith("Boreal "):
        return {"2TEN": 6, "2TDB": 7, "2TDN": 7, "2TD": 7}.get(veg)
    return None


def main(data_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    measurements = pd.read_csv(data_dir / "ForC_measurements.csv", low_memory=False)
    sites = pd.read_csv(data_dir / "ForC_sites.csv", encoding="cp1252", low_memory=False)
    keep = (
        measurements["loaded.from"].astype(str).str.contains("Luyssaert_2007_cbob", regex=False)
        & pd.to_numeric(measurements["mean"], errors="coerce").gt(0)
        & pd.to_numeric(measurements["stand.age"], errors="coerce").ge(100)
        & pd.to_numeric(measurements["D.precedence"], errors="coerce").ne(0)
        & pd.to_numeric(measurements["flag.suspicious"], errors="coerce").ne(1)
    )
    selected = measurements.loc[keep].copy()
    npp = selected[selected["variable.name"].eq("NPP_1_C")]
    agb = selected[selected["variable.name"].eq("biomass_ag_C")]
    pairs = npp.merge(
        agb, on=["sites.sitename", "plot.name"], suffixes=("_npp", "_agb")
    ).merge(sites[["sites.sitename", "FAO.ecozone"]], on="sites.sitename", validate="many_to_one")
    pairs = pairs[
        pairs["dominant.veg_npp"].eq(pairs["dominant.veg_agb"])
        & pairs["plot.name"].notna()
        & ~pairs["plot.name"].isin(["NI", "NRA", "NA", "NAC"])
    ].copy()
    pairs["PFT"] = pairs.apply(map_pft, axis=1)
    pairs = pairs[pairs["PFT"].notna()].copy()
    pairs["PFT"] = pairs["PFT"].astype(int)
    # The standardized mean uses the variable dictionary's units, not original.units.
    variables = pd.read_csv(data_dir / "ForC_variables.csv").set_index("variable.name")
    assert variables.loc["NPP_1_C", "units"] == "Mg C ha-1 yr-1"
    assert variables.loc["biomass_ag_C", "units"] == "Mg C ha-1"
    pairs["ratio_carbon_years"] = pairs["mean_agb"] / pairs["mean_npp"]
    pairs["c_dry_if_fC_0_5"] = pairs["ratio_carbon_years"] / 500
    pairs["time_status"] = pairs.apply(time_status, axis=1)
    pairs["same_reported_age"] = pairs["stand.age_npp"].eq(pairs["stand.age_agb"])
    # Repeated combinations from one plot are not independent sample units.
    plots = pairs.groupby(["PFT", "sites.sitename", "plot.name"], as_index=False).agg(
        ratio_carbon_years=("ratio_carbon_years", "median"),
        c_dry_if_fC_0_5=("c_dry_if_fC_0_5", "median"),
        candidate_pair_rows=("measurement.ID_npp", "size"),
        any_calendar_year_overlap=("time_status", lambda x: x.eq("calendar_year_overlap").any()),
    )
    summary = plots.groupby("PFT", as_index=False).agg(
        plots=("sites.sitename", "size"),
        ratio_carbon_median_years=("ratio_carbon_years", "median"),
        c_median_if_fC_0_5=("c_dry_if_fC_0_5", "median"),
        c_min_if_fC_0_5=("c_dry_if_fC_0_5", "min"),
        c_max_if_fC_0_5=("c_dry_if_fC_0_5", "max"),
        plots_with_calendar_year_overlap=("any_calendar_year_overlap", "sum"),
    )
    pair_columns = [
        "PFT", "sites.sitename", "plot.name", "FAO.ecozone",
        "measurement.ID_npp", "measurement.ID_agb", "variable.name_npp", "variable.name_agb",
        "mean_npp", "mean_agb", "stand.age_npp", "stand.age_agb",
        "dominant.veg_npp", "dominant.veg_agb", "date_npp", "start.date_npp", "end.date_npp",
        "date_agb", "start.date_agb", "end.date_agb", "time_status", "same_reported_age",
        "citation.ID_npp", "citation.ID_agb", "loaded.from_npp", "loaded.from_agb",
        "D.precedence_npp", "D.precedence_agb", "flag.suspicious_npp", "flag.suspicious_agb",
        "C.conversion.factor_npp", "C.conversion.factor_agb", "ratio_carbon_years", "c_dry_if_fC_0_5",
    ]
    pairs[pair_columns].to_csv(output_dir / "BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_PAIRS_20261005.csv", index=False)
    plots.to_csv(output_dir / "BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_PLOT_RATIOS_20261005.csv", index=False)
    summary.to_csv(output_dir / "BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_SUMMARY_20261005.csv", index=False)
    print(json.dumps({"pair_rows": len(pairs), "summary": summary.to_dict(orient="records")}, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
