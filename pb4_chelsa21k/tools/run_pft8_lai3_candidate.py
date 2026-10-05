from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
SOURCE_ZIP = BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip"
EXPECTED_SOURCE_SHA = "a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34"

WORK = Path("/tmp/pb4_pft8_lai3_candidate")
RUN = Path("/tmp/pb4_pft8_lai3_candidate_run")
RESULTS = BASE / "results" / "pft8_lai3_candidate_20261006"
CANDIDATE_ZIP = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_PFT8_LAI3.zip"
ROOT_NAME = "PB4Studio_v6.6.3_CHELSA21K"

OLD = """      if (wdom.eq.7) then
       if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""

NEW = """      if (wdom.eq.7) then
c PB4 shallow-soil PFT8 competition extension.
c This is not an original BIOME4 v4.2b2 rule.
c The threshold is preselected from the historical Beyer depth response:
c PFT8 at 0.05 m and tree at 0.10 m, without fitting Park et al. (2021).
       if (grasspft.eq.8.and.grassnpp.gt.0.0.and.
     >     grasslai.ge.2.0.and.woodylai.lt.3.0) then
        optpft=grasspft
       else if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(args, cwd=None, env=None, log=None):
    print("+", " ".join(map(str, args)), flush=True)
    if log is None:
        subprocess.run(args, cwd=cwd, env=env, check=True)
        return
    with log.open("w", encoding="utf-8") as fh:
        p = subprocess.Popen(
            args, cwd=cwd, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            fh.write(line)
        rc = p.wait()
        if rc:
            raise SystemExit(rc)


def prepare() -> Path:
    if sha256(SOURCE_ZIP) != EXPECTED_SOURCE_SHA:
        raise SystemExit(f"source canonical SHA mismatch: {sha256(SOURCE_ZIP)}")

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(SOURCE_ZIP) as z:
        z.extractall(WORK)
    root = WORK / ROOT_NAME
    if not root.exists():
        root = next(WORK.glob("PB4Studio*"))

    src = root / "fortran_src" / "biome4_original_4_2b2.f"
    txt = src.read_text(encoding="latin-1")
    if OLD not in txt:
        raise SystemExit("PFT7 competition block not found")
    src.write_text(txt.replace(OLD, NEW, 1), encoding="latin-1")

    init = root / "pb4studio" / "__init__.py"
    itxt = init.read_text(encoding="utf-8")
    itxt2 = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        "__version__ = '6.6.3-CHELSA21K-PFT8-LAI3-CANDIDATE'",
        itxt,
        count=1,
    )
    if itxt2 == itxt:
        raise SystemExit("version patch failed")
    init.write_text(itxt2, encoding="utf-8")

    (root / "PFT8_LAI3_CANDIDATE_2026-10-06.md").write_text(
        """# PFT8 LAI3 candidate

Purpose: restore a narrow shallow-soil temperate-grass response under CHELSA
without changing BIOME4 PFT climate limits or physiological NPP equations.

Extension is only in the PFT7 competition branch:

- grasspft must be PFT8
- grass NPP > 0
- grass LAI >= 2.0
- PFT7 woody LAI < 3.0

Then PFT8 becomes dominant.

The woody LAI 3.0 threshold is not fitted to Park et al. (2021).
It was preselected because BIOME4 already uses LAI 3.0 as a canopy-state
breakpoint in the PFT4 competition branch, and the historical Beyer
depth response had PFT8 at 0.05 m but trees at 0.10 m. The 2.5/3.0/3.5
candidate sweep showed that 3.0 reproduces the narrow 0.04-0.05 m
transition while 2.5 produces no PFT8 and 3.5 expands PFT8 too deeply.

This is a PB4 model extension, not an original BIOME4 v4.2b2 rule.
""",
        encoding="utf-8",
    )

    for p in (root / "fortran_src").glob("*"):
        if p.suffix in {".so", ".o", ".mod"}:
            p.unlink()
    return root


def run_full(root: Path) -> Path:
    shutil.rmtree(RUN, ignore_errors=True)
    shutil.copytree(WORK, RUN)
    run_root = RUN / root.name
    RESULTS.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "4"
    sh(
        [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
        cwd=run_root,
        env=env,
        log=RESULTS / "PFT8_LAI3_21KA_RUN.log",
    )
    out = run_root / "outputs_CHELSA21K"
    if not out.exists():
        raise SystemExit("outputs_CHELSA21K missing")
    return out


def jang_summary(out: Path):
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    sums, rows = [], []
    for mode in ("static", "dynamic"):
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(lambda r: r[target[str(r["record_id"])][1]], axis=1)
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        sums.append({
            "mode": mode,
            "n": len(df),
            "correct_n": int(df["correct_1pct"].sum()),
            "accuracy_pct": 100 * float(df["correct_1pct"].mean()),
            "herbaceous_cells_sum": int(df["basin_count_herbaceous"].sum()),
            "herbaceous_cells_max": int(df["basin_count_herbaceous"].max()),
        })
        keep = [
            "record_id","model_ka_bp","valid_basin_cell_count",
            "basin_count_conifer","basin_count_broadleaf",
            "basin_count_mixed","basin_count_herbaceous",
            "target_class","target_fraction","correct_1pct"
        ]
        q = df[keep].copy()
        q.insert(0, "mode", mode)
        rows.append(q)
    return pd.DataFrame(sums), pd.concat(rows, ignore_index=True)


def find_timeseries(out: Path) -> pd.DataFrame:
    hits=[]
    for p in out.rglob("*.csv"):
        try:
            df=pd.read_csv(p,encoding="utf-8-sig")
        except Exception:
            continue
        if {"ka_bp","reich_lai_sapwood_pft08_count","reich_lai_sapwood_agb_mean_kg_m2"}.issubset(df.columns):
            hits.append((p,df))
    if not hits:
        raise SystemExit("candidate 21ka timeseries not found")
    p,df=max(hits,key=lambda x: len(x[1]))
    if len(df) not in {211,422}:
        print(f"warning: unexpected timeseries length {len(df)} at {p}")
    return df


def summarize_timeseries(ts: pd.DataFrame):
    rows=[]
    park=[]
    if "mode" not in ts.columns:
        raise SystemExit("timeseries mode column missing")
    for mode,g in ts.groupby("mode"):
        g=g.copy()
        p8=pd.to_numeric(g["reich_lai_sapwood_pft08_count"],errors="coerce").fillna(0)
        n=pd.to_numeric(g["n_cells"],errors="coerce")
        ages=pd.to_numeric(g["ka_bp"],errors="coerce")
        modern=g.loc[ages.abs().idxmin()]
        rows.append({
            "mode":mode,
            "n_timesteps":len(g),
            "pft8_timesteps_positive":int((p8>0).sum()),
            "pft8_max_cells":int(p8.max()),
            "pft8_max_fraction":float((p8/n).max()),
            "agb_time_mean_kg_m2":float(pd.to_numeric(g["reich_lai_sapwood_agb_mean_kg_m2"]).mean()),
            "agb_0ka_kg_m2":float(modern["reich_lai_sapwood_agb_mean_kg_m2"]),
        })
        q=g[(ages>=0.5)&(ages<=3.2)].copy()
        for _,r in q.iterrows():
            park.append({
                "mode":mode,
                "ka_bp":r["ka_bp"],
                "n_cells":r["n_cells"],
                "pft04_count":r.get("reich_lai_sapwood_pft04_count"),
                "pft06_count":r.get("reich_lai_sapwood_pft06_count"),
                "pft07_count":r.get("reich_lai_sapwood_pft07_count"),
                "pft08_count":r.get("reich_lai_sapwood_pft08_count"),
                "pft08_fraction":float(r.get("reich_lai_sapwood_pft08_count",0))/float(r["n_cells"]),
                "mean_npp":r.get("mean_npp"),
                "mean_agb_kg_m2":r.get("reich_lai_sapwood_agb_mean_kg_m2"),
            })
    return pd.DataFrame(rows), pd.DataFrame(park)


def build_zip(root: Path):
    CANDIDATE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    fixed=(2026,10,6,0,0,0)
    with zipfile.ZipFile(CANDIDATE_ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel=p.relative_to(WORK).as_posix()
            info=zipfile.ZipInfo(rel,date_time=fixed)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 & 0xFFFF)<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return sha256(CANDIDATE_ZIP)


def main():
    root=prepare()
    out=run_full(root)
    jang,jrows=jang_summary(out)
    ts=find_timeseries(out)
    tsum,park=summarize_timeseries(ts)

    RESULTS.mkdir(parents=True,exist_ok=True)
    jang.to_csv(RESULTS/"PFT8_LAI3_JANG_SUMMARY.csv",index=False,encoding="utf-8-sig")
    jrows.to_csv(RESULTS/"PFT8_LAI3_JANG_ROWS.csv",index=False,encoding="utf-8-sig")
    tsum.to_csv(RESULTS/"PFT8_LAI3_21KA_SUMMARY.csv",index=False,encoding="utf-8-sig")
    park.to_csv(RESULTS/"PFT8_LAI3_PARK_INTERVAL_PFT_COUNTS.csv",index=False,encoding="utf-8-sig")
    ts.to_csv(RESULTS/"PFT8_LAI3_21KA_TIMESERIES.csv",index=False,encoding="utf-8-sig")

    zsha=build_zip(root)
    provenance={
        "source_canonical_sha256":EXPECTED_SOURCE_SHA,
        "candidate_sha256":zsha,
        "candidate":"PFT8_LAI3",
        "rule":"if wdom=PFT7, grasspft=PFT8, grass NPP>0, grass LAI>=2.0, woody LAI<3.0 then optpft=PFT8",
        "park_used_for_threshold_fitting":False,
        "threshold_basis":"historical Beyer 0.05m grass vs 0.10m tree transition + existing BIOME4 LAI 3.0 canopy breakpoint",
    }
    (RESULTS/"PFT8_LAI3_PROVENANCE.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding="utf-8")

    md=[
        "# PFT8 LAI3 full 21 ka candidate",
        "",
        f"Candidate SHA-256: `{zsha}`",
        "",
        "## Jang 1% validation",
        "",
        jang.to_markdown(index=False),
        "",
        "## 21 ka PFT8 and AGB summary",
        "",
        tsum.to_markdown(index=False),
        "",
        "Park et al. (2021) was not used to fit the LAI 3.0 threshold.",
        "Park-interval PFT counts are exported for post-selection holdout evaluation.",
    ]
    (RESULTS/"PFT8_LAI3_CANDIDATE_RESULT_KO.md").write_text("\n".join(md),encoding="utf-8")

    print(jang.to_string(index=False))
    print(tsum.to_string(index=False))
    print("CANDIDATE_SHA256="+zsha)


if __name__=="__main__":
    main()
