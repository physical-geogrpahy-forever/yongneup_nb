"""Benchmark the Ise parameter transfer on existing ForC diagnostic pairs.

Inputs are the selected, provenance-preserving NPP_1_C/biomass_ag_C pairs
from ForC commit 407c520e6350917bca42e6bf7d5031dbcc551362. This script
fits no parameters. Multiple records from one plot are not independent:
their prediction/observation ratios are summarized by the plot median.

Usage: python audit_ise2010_applicability.py PAIRS.csv OUTPUT.json
"""

import csv
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from ise2010_static_agb import static_agb


def run(pair_path):
    pair_path = Path(pair_path)
    with pair_path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 44, "Unexpected diagnostic data selection; re-audit provenance"
    scored = []
    for row in rows:
        assert row["variable.name_npp"] == "NPP_1_C"
        assert row["variable.name_agb"] == "biomass_ag_C"
        assert "Luyssaert_2007_cbob" in row["loaded.from_npp"]
        assert "Luyssaert_2007_cbob" in row["loaded.from_agb"]
        assert float(row["stand.age_npp"]) >= 100
        assert float(row["stand.age_agb"]) >= 100
        pft = int(row["PFT"])
        # Variable dictionary units are Mg C ha-1 yr-1 and Mg C ha-1.
        npp_gC = float(row["mean_npp"]) * 100
        observed_dry = float(row["mean_agb"]) * 0.1 / 0.5
        predicted_dry = static_agb(npp_gC, pft)["agb_dry_kg_m2"]
        ratio = predicted_dry / observed_dry
        # Independently check that the carbon fraction cancels in the ratio.
        model_carbon_years = static_agb(1, pft)["agb_dry_kg_m2"] * 500
        expected_ratio = model_carbon_years / (float(row["mean_agb"]) / float(row["mean_npp"]))
        assert abs(ratio - expected_ratio) <= 1e-12 * max(1, abs(ratio))
        scored.append({
            "pft": pft,
            "site": row["sites.sitename"], "plot": row["plot.name"],
            "measurement_ID_npp": row["measurement.ID_npp"],
            "measurement_ID_agb": row["measurement.ID_agb"],
            "dominant_vegetation": row["dominant.veg_npp"],
            "time_status": row["time_status"],
            "same_reported_age": row["same_reported_age"] == "True",
            "npp_gC_m2_yr": npp_gC,
            "observed_agb_kg_dry_m2_if_fC_0_5": observed_dry,
            "predicted_agb_kg_dry_m2_if_fC_0_5": predicted_dry,
            "predicted_over_observed": ratio,
        })

    summaries = {}
    plot_scores = []
    for subset in ("all_selected", "calendar_year_overlap", "overlap_and_same_age"):
        groups = defaultdict(list)
        for row in scored:
            if subset != "all_selected" and row["time_status"] != "calendar_year_overlap":
                continue
            if subset == "overlap_and_same_age" and not row["same_reported_age"]:
                continue
            groups[row["pft"], row["site"], row["plot"]].append(row["predicted_over_observed"])
        records = []
        for (pft, site, plot), values in groups.items():
            records.append({
                "subset": subset, "pft": pft, "site": site, "plot": plot,
                "pair_rows": len(values),
                "plot_median_predicted_over_observed": statistics.median(values),
            })
        plot_scores.extend(records)
        summaries[subset] = []
        for pft in (4, 5, 6, 7):
            ratios = [r["plot_median_predicted_over_observed"] for r in records if r["pft"] == pft]
            assert ratios
            summaries[subset].append({
                "pft": pft, "plots": len(ratios),
                "median_predicted_over_observed": statistics.median(ratios),
                "mean_absolute_percent_error_of_plot_ratios": statistics.mean(abs(x - 1) for x in ratios) * 100,
                "minimum_predicted_over_observed": min(ratios),
                "maximum_predicted_over_observed": max(ratios),
            })
    assert sum(r["plots"] for r in summaries["all_selected"]) == 35
    assert sum(r["plots"] for r in summaries["calendar_year_overlap"]) == 31
    assert sum(r["plots"] for r in summaries["overlap_and_same_age"]) == 29
    return {
        "application_decision": "do_not_adopt_unadjusted_transferred_coefficients_as_validated_project_parameters",
        "model_source_doi": "10.1029/2010JG001326",
        "forc_commit": "407c520e6350917bca42e6bf7d5031dbcc551362",
        "input_pairs_file": pair_path.name,
        "input_pairs_sha256": hashlib.sha256(pair_path.read_bytes()).hexdigest(),
        "input_pair_rows": len(rows),
        "fit_performed": False,
        "method": "median pair prediction/observation ratio per plot, then equal plot weight per PFT",
        "maturity_note": "both reported ages >=100; 999 is a mature-forest flag, not literal measured age",
        "caution": "diagnostic mature stands are not certified undisturbed mathematical equilibria; small PFT7 sample",
        "summaries": summaries, "plot_scores": plot_scores, "pair_scores": scored,
    }


if __name__ == "__main__":
    report = run(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"summaries": report["summaries"], "application_decision": report["application_decision"]}, indent=2))
