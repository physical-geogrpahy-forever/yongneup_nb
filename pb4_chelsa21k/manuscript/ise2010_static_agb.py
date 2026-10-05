"""Equilibrium leaf + aboveground stem biomass from total NPP and BIOME4 PFT.

Source: Ise et al. (2010), doi:10.1029/2010JG001326,
Table 1, Appendix A equations A10-A15, and equations 10-11.

This transfers the paper's TEMPERATE/BOREAL pooled VISIT parameterization
to BIOME4 PFT4/5 and PFT6/7 respectively. It does not supply four distinct
PFT calibrations and is not native BIOME4 code or a site validation.
NPP: g C m-2 yr-1. AGB: kg dry matter m-2, for the model's leaf+stem pools.
Carbon fraction 0.5 is an explicit conversion assumption, not fitted here.
"""

from __future__ import annotations

import argparse
import json
import math
from types import MappingProxyType

PARAMETERS = MappingProxyType({
    "temperate": MappingProxyType({
        "ff": 0.198, "fs": 0.500,
        "kgf": 0.498, "kgs": 0.145, "kgr": 0.243,
        "kf": 1.08, "ks": 0.0234, "kr": 0.288,
    }),
    "boreal": MappingProxyType({
        "ff": 0.134, "fs": 0.500,
        "kgf": 0.466, "kgs": 0.118, "kgr": 0.214,
        "kf": 0.702, "ks": 0.0108, "kr": 0.137,
    }),
})
PFT_TO_GROUP = MappingProxyType({4: "temperate", 5: "temperate", 6: "boreal", 7: "boreal"})


def static_agb(npp: float, pft: int, carbon_fraction: float = 0.5) -> dict:
    """Compute equilibrium live aboveground biomass in the paper's pools.

    The paper allocates EPP (GPP minus maintenance respiration), then
    subtracts organ-specific growth respiration. Therefore ff/fs themselves
    MUST NOT be treated as fractions of total NPP.
    """
    if isinstance(pft, bool) or not isinstance(pft, int) or pft not in PFT_TO_GROUP:
        raise ValueError("pft must be one of the BIOME4 forest PFT integers 4, 5, 6, 7")
    npp = float(npp)
    carbon_fraction = float(carbon_fraction)
    if not math.isfinite(npp) or npp < 0:
        raise ValueError("npp must be finite and >= 0 in g C m-2 yr-1")
    if not math.isfinite(carbon_fraction) or not 0 < carbon_fraction <= 1:
        raise ValueError("carbon_fraction must be finite and in (0, 1]")

    group = PFT_TO_GROUP[pft]
    p = PARAMETERS[group]
    # A10-A15: net component production per unit EPP.
    q_leaf = p["ff"] * (1 - p["kgf"])
    q_stem = (1 - p["ff"]) * p["fs"] * (1 - p["kgs"])
    q_root = (1 - p["ff"]) * (1 - p["fs"]) * (1 - p["kgr"])
    q_total = q_leaf + q_stem + q_root
    a_leaf, a_stem, a_root = (q / q_total for q in (q_leaf, q_stem, q_root))

    leaf_c = npp * a_leaf / p["kf"]
    stem_c = npp * a_stem / p["ks"]
    root_c = npp * a_root / p["kr"]
    conversion = 1000 * carbon_fraction
    coefficient = (a_leaf / p["kf"] + a_stem / p["ks"]) / conversion
    return {
        "pft": pft,
        "parameter_group": group,
        "npp_gC_m2_yr": npp,
        "carbon_fraction_assumed": carbon_fraction,
        "npp_fraction_leaf": a_leaf,
        "npp_fraction_aboveground_stem": a_stem,
        "npp_fraction_root": a_root,
        "leaf_carbon_gC_m2": leaf_c,
        "aboveground_stem_carbon_gC_m2": stem_c,
        "root_carbon_gC_m2_excluded_from_agb": root_c,
        "agb_dry_kg_m2": (leaf_c + stem_c) / conversion,
        "coefficient_kgDM_per_gC_per_year": coefficient,
        "source_doi": "10.1029/2010JG001326",
        "scope": "transferred temperate/boreal pooled equilibrium; not four separate PFT calibrations",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npp", type=float, required=True)
    parser.add_argument("--pft", type=int, choices=tuple(PFT_TO_GROUP), required=True)
    parser.add_argument("--carbon-fraction", type=float, default=0.5)
    args = parser.parse_args()
    try:
        result = static_agb(args.npp, args.pft, args.carbon_fraction)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
