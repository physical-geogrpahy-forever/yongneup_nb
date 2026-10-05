from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
ZIP = BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip"
WORK = Path("/tmp/pb4_pft8_competition_sweep")
OUT = BASE / "results" / "pft8_shallow_competition_sweep_20261006"

THRESHOLDS = (2.5, 3.0, 3.5)
DEPTHS = (0.01,0.02,0.03,0.04,0.05,0.06,0.08,0.10,0.12,0.15,0.20,0.30)
AGES = (5.0,4.0,3.0,2.7,2.5,2.3,2.2,2.0)

OLD = """      if (wdom.eq.7) then
       if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""


def sh(args, cwd=None):
    print("+", " ".join(map(str, args)), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def patch_candidate(root: Path, th: float):
    src = root / "fortran_src" / "biome4_original_4_2b2.f"
    if not src.exists():
        raise RuntimeError(f"missing source: {src}")
    txt = src.read_text(encoding="latin-1")
    if OLD not in txt:
        raise RuntimeError("PFT7 competition block not found")
    ths = f"{th:.1f}"
    new = f"""      if (wdom.eq.7) then
c PB4 shallow-soil PFT8 competition candidate.
c Not an original BIOME4 v4.2b2 rule.
       if (grasspft.eq.8.and.grassnpp.gt.0.0.and.
     >     grasslai.ge.2.0.and.woodylai.lt.{ths}) then
        optpft=grasspft
       else if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""
    src.write_text(txt.replace(OLD, new, 1), encoding="latin-1")

    (root / "PFT8_SHALLOW_COMPETITION_CANDIDATE.md").write_text(
        "# PFT8 shallow competition candidate\n\n"
        f"PFT7 branch extension: grasspft=8, grass NPP > 0, "
        f"grass LAI >= 2.0, woody LAI < {ths}.\n\n"
        "This is a PB4 candidate extension, not an original BIOME4 rule.\n",
        encoding="utf-8",
    )


def run_candidate(th: float) -> pd.DataFrame:
    td = WORK / f"lai_{th:.1f}"
    td.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(td)
    root = next(td.glob("PB4Studio*"))
    patch_candidate(root, th)

    for p in (root / "fortran_src").glob("*"):
        if p.suffix in {".so", ".o", ".mod"}:
            p.unlink()

    outcsv = OUT / f"PFT8_LAI_{th:.1f}.csv"
    cmd = [
        sys.executable,
        "tools/mckenzie2003_depth_sensitivity.py",
        "--climate",
        "embedded_inputs/yongneup_exact20m/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "--elevation-m",
        "1162.08",
        "--depths",
        *[str(x) for x in DEPTHS],
        "--ages",
        *[str(x) for x in AGES],
        "--threads",
        "2",
        "--output",
        str(outcsv),
    ]
    sh(cmd, cwd=root)
    return pd.read_csv(outcsv)


def main():
    shutil.rmtree(WORK, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)

    summaries = []
    details = []
    for th in THRESHOLDS:
        df = run_candidate(th)
        if "variant" in df.columns:
            df = df[df["variant"].astype(str).eq("mckenzie2003")].copy()

        for age, g in df.groupby("target_age_ka"):
            p8 = g[g["optpft"].eq(8)]
            summaries.append(
                {
                    "woody_lai_threshold": th,
                    "age_ka": float(age),
                    "n_depths": len(g),
                    "n_pft8_depths": len(p8),
                    "pft8_depth_min_m": p8["depth_m"].min() if len(p8) else None,
                    "pft8_depth_max_m": p8["depth_m"].max() if len(p8) else None,
                }
            )

        for _, row in df.iterrows():
            if float(row["depth_m"]) in {0.03,0.04,0.05,0.06,0.08,0.10}:
                details.append(
                    {
                        "woody_lai_threshold": th,
                        "age_ka": row["target_age_ka"],
                        "depth_m": row["depth_m"],
                        "optpft": row["optpft"],
                        "pft7_npp": row.get("pft07_npp"),
                        "pft7_lai": row.get("pft07_lai"),
                        "pft8_npp": row.get("pft08_npp"),
                        "pft8_lai": row.get("pft08_lai"),
                        "whc_total_mm": row.get("whc_total_mm"),
                    }
                )

    s = pd.DataFrame(summaries)
    d = pd.DataFrame(details)
    s.to_csv(OUT / "PFT8_THRESHOLD_SUMMARY.csv", index=False)
    d.to_csv(OUT / "PFT8_THRESHOLD_KEY_DEPTHS.csv", index=False)

    md = [
        "# PFT8 shallow competition threshold sweep",
        "",
        "Candidate extension is applied only in the PFT7 competition branch.",
        "Condition: grasspft=8, grass NPP>0, grass LAI>=2.0, woody LAI<threshold.",
        "This is a PB4 candidate rule, not original BIOME4.",
        "",
        "## Summary",
        "",
        s.to_markdown(index=False),
        "",
        "## Key depths",
        "",
        d.to_markdown(index=False),
    ]
    (OUT / "PFT8_THRESHOLD_SWEEP_KO.md").write_text("\n".join(md), encoding="utf-8")
    print(s.to_string(index=False))


if __name__ == "__main__":
    main()
