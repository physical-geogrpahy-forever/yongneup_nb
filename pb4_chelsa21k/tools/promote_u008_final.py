from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
MODEL = BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip"
FINAL = BASE / "results" / "final_integrated_20261006"
PARKDIR = BASE / "validation" / "park2021"
OLD_SHA = "796faeae61fa00ca31512d3e087d6134dbdd01428beea760d79d184fa6481f86"
WORK = Path("/tmp/pb4_u008_promote")
BASELINE = Path("/tmp/U020_BASELINE.zip")
NEWZIP = Path("/tmp/PB4Studio_v6.6.3_CHELSA21K_U008_FINAL.zip")
REPORT = Path("/tmp/U008_REPORT.json")
RUNLOG = Path("/tmp/U008_FINAL_21KA_RUN.log")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare() -> Path:
    if sha256(MODEL) != OLD_SHA:
        raise SystemExit(f"Unexpected baseline canonical SHA: {sha256(MODEL)}")
    shutil.copy2(MODEL, BASELINE)
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(BASELINE) as z:
        z.extractall(WORK)
    roots = [p for p in WORK.iterdir() if p.is_dir() and p.name.startswith("PB4Studio")]
    if len(roots) != 1:
        raise SystemExit(f"Expected one package root, got {roots}")
    root = roots[0]

    p = root / "pb4studio" / "pelletier_geomorph.py"
    s = p.read_text(encoding="utf-8")
    old = "    uplift_m_per_kyr: float = 0.20"
    if old not in s:
        raise SystemExit("Expected U=0.20 default not found")
    p.write_text(s.replace(old, "    uplift_m_per_kyr: float = 0.08", 1), encoding="utf-8")

    p = root / "pb4studio" / "config.py"
    s = p.read_text(encoding="utf-8")
    old = "(동해안 융기율 참고값, 0.2 m/kyr = 0.2 mm/yr)."
    new = "(태백산맥 장기 삭박율 기반 regional forcing, 0.08 m/kyr = 0.08 mm/yr)."
    if old not in s:
        raise SystemExit("Expected old uplift help text not found")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

    (root / "UPLIFT_U008_FINAL_2026-10-06.md").write_text(
        "# Final uplift setting\n\n"
        "- Production uplift: U = 0.08 m kyr^-1 = 80 mm kyr^-1.\n"
        "- Lee et al. (2024), Earth Surface Dynamics 12, 1091-1120, used 80 mm kyr^-1 "
        "as a regional uplift forcing chosen to equal the ca. 22 Ma-to-present Taebaek Mountain exhumation rate.\n"
        "- This is a regional model forcing, not a direct Yongneup uplift measurement.\n"
        "- Previous canonical U=0.20 m kyr^-1 is archived for provenance.\n",
        encoding="utf-8",
    )

    shutil.rmtree(root / "outputs_CHELSA21K", ignore_errors=True)
    Path("/tmp/PB4_U008_ROOT.txt").write_text(str(root), encoding="utf-8")
    return root


def run_model(root: Path) -> None:
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "4"
    cmd = [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"]
    with RUNLOG.open("w", encoding="utf-8") as f:
        p = subprocess.run(cmd, cwd=root, env=env, stdout=f, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        print(RUNLOG.read_text(encoding="utf-8", errors="replace")[-8000:])
        raise SystemExit(f"21 ka runner failed: {p.returncode}")


def pftcount(row: pd.Series, p: int) -> float:
    return float(row.get(f"reich_lai_sapwood_pft{p:02d}_count", 0.0))


def model_row(df: pd.DataFrame, ka: float) -> pd.Series:
    hit = df.loc[np.isclose(df.ka_bp.astype(float), float(ka))]
    if len(hit) != 1:
        raise SystemExit(f"Missing unique model row at {ka} ka")
    return hit.iloc[0]


def rebuild_science(root: Path) -> dict:
    out = root / "outputs_CHELSA21K"
    frames = []
    by_mode = {}
    for mode in ("static", "dynamic"):
        d = pd.read_csv(out / f"model_{mode}" / "summary_timeseries.csv", encoding="utf-8-sig")
        if len(d) != 211:
            raise SystemExit(f"{mode}: expected 211 rows, got {len(d)}")
        by_mode[mode] = d.copy()
        z = d.copy()
        z.insert(0, "mode", mode)
        z.insert(1, "source_csv", f"model_{mode}/summary_timeseries.csv")
        frames.append(z)
    pd.concat(frames, ignore_index=True).to_csv(
        FINAL / "FINAL_AGB_21KA_TIMESERIES.csv", index=False, encoding="utf-8-sig"
    )

    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    parts = []
    sums = []
    for mode in ("static", "dynamic"):
        v = pd.read_csv(out / f"model_{mode}" / "validation_per_output_time.csv", encoding="utf-8-sig")
        v = v[v.record_id.astype(str).isin(target)].copy()
        v["target_class"] = v.record_id.astype(str).map(lambda x: target[x][0])
        v["target_count"] = v.apply(lambda r: r[target[str(r.record_id)][1]], axis=1)
        v["target_fraction"] = v.target_count / v.valid_basin_cell_count
        v["correct_1pct"] = v.target_fraction >= 0.01 - 1e-15
        keep = [
            "record_id", "model_ka_bp", "valid_basin_cell_count",
            "basin_count_conifer", "basin_count_broadleaf", "basin_count_mixed",
            "basin_count_herbaceous", "target_class", "target_fraction", "correct_1pct",
        ]
        q = v[keep].copy()
        q.insert(0, "mode", mode)
        parts.append(q)
        sums.append({
            "model": "PB4-FINAL-nativeClimate-BIOME4AGB-U008",
            "mode": mode,
            "n": len(v),
            "correct_n": int(v.correct_1pct.sum()),
            "accuracy_pct": 100.0 * float(v.correct_1pct.mean()),
            "threshold_fraction": 0.01,
        })
    pd.concat(parts, ignore_index=True).to_csv(
        FINAL / "FINAL_JANG1PCT_ROWS.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(sums).to_csv(
        FINAL / "FINAL_JANG1PCT_SUMMARY.csv", index=False, encoding="utf-8-sig"
    )
    if [(x["mode"], x["correct_n"], x["n"]) for x in sums] != [
        ("static", 24, 62), ("dynamic", 55, 62)
    ]:
        raise SystemExit(f"Jang regression changed: {sums}")

    ag = []
    for mode in ("dynamic", "static"):
        d = by_mode[mode]
        c = "reich_lai_sapwood_agb_mean_kg_m2"
        modern = float(d.loc[np.isclose(d.ka_bp, 0.0), c].iloc[0])
        ag.append({
            "mode": mode,
            "n_timesteps": len(d),
            "time_mean_agb_kg_m2": float(d[c].mean()),
            "min_time_mean_agb_kg_m2": float(d[c].min()),
            "max_time_mean_agb_kg_m2": float(d[c].max()),
            "absolute_max_agb_kg_m2": float(d["reich_lai_sapwood_agb_max_kg_m2"].max()),
            "modern_0ka_agb_kg_m2": modern,
            "modern_0ka_agb_t_ha": modern * 10.0,
        })
    pd.DataFrame(ag).to_csv(FINAL / "FINAL_AGB_SUMMARY.csv", index=False, encoding="utf-8-sig")

    park = pd.read_csv(PARKDIR / "PARK2021_ZONE2_100YR_HOLDOUT.csv", encoding="utf-8-sig")
    scold, dcold, dtemp, dnpp, dagb = [], [], [], [], []
    for ka in park.ka_bp:
        rs = model_row(by_mode["static"], ka)
        rd = model_row(by_mode["dynamic"], ka)

        def cold_fraction(r):
            cold = sum(pftcount(r, p) for p in (5, 6, 7))
            temp = sum(pftcount(r, p) for p in (2, 3, 4))
            return cold / (cold + temp) if cold + temp else np.nan

        fs, fd = cold_fraction(rs), cold_fraction(rd)
        scold.append(fs)
        dcold.append(fd)
        dtemp.append(1.0 - fd if np.isfinite(fd) else np.nan)
        dnpp.append(float(rd["mean_npp"]))
        dagb.append(float(rd["reich_lai_sapwood_agb_mean_kg_m2"]))
    park["static_model_coldtree_fraction"] = scold
    park["dynamic_model_coldtree_fraction"] = dcold
    park["dynamic_model_temperate_deciduous_fraction"] = dtemp
    park["dynamic_npp"] = dnpp
    park["dynamic_agb_kg_m2"] = dagb
    park.to_csv(PARKDIR / "PARK2021_ZONE2_100YR_HOLDOUT.csv", index=False, encoding="utf-8-sig")

    def sp(a, b):
        z = spearmanr(np.asarray(a, float), np.asarray(b, float), nan_policy="omit")
        return float(z.statistic), float(z.pvalue)

    pc2_dyn = sp(park.park_pc2, park.dynamic_model_coldtree_fraction)
    pc2_sta = sp(park.park_pc2, park.static_model_coldtree_fraction)
    br_dyn = sp(park.pollen_broadleaf_fraction_woody, park.dynamic_model_temperate_deciduous_fraction)
    br_sta = sp(park.pollen_broadleaf_fraction_woody, 1.0 - park.static_model_coldtree_fraction)

    evt = by_mode["dynamic"]
    evt = evt[(evt.ka_bp >= 2.2 - 1e-9) & (evt.ka_bp <= 2.7 + 1e-9)]
    open_count = sum(
        float(evt[f"reich_lai_sapwood_pft{p:02d}_count"].sum())
        for p in range(8, 14)
        if f"reich_lai_sapwood_pft{p:02d}_count" in evt.columns
    )

    dyn = by_mode["dynamic"]
    report = {
        "uplift_m_per_kyr": 0.08,
        "uplift_mm_per_kyr": 80.0,
        "jang": {"static": "24/62", "dynamic": "55/62"},
        "dynamic": {
            "mean_elev_21ka": float(dyn.iloc[0].mean_elevation_m),
            "mean_elev_0ka": float(dyn.iloc[-1].mean_elevation_m),
            "delta_mean_elev_m": float(dyn.iloc[-1].mean_elevation_m - dyn.iloc[0].mean_elevation_m),
            "mean_soil_21ka": float(dyn.iloc[0].mean_soil_depth_m),
            "mean_soil_0ka": float(dyn.iloc[-1].mean_soil_depth_m),
            "delta_mean_soil_m": float(dyn.iloc[-1].mean_soil_depth_m - dyn.iloc[0].mean_soil_depth_m),
            "time_mean_npp": float(dyn.mean_npp.mean()),
            "time_mean_eemt": float(dyn.mean_eemt.mean()),
            "time_mean_agb": float(dyn.reich_lai_sapwood_agb_mean_kg_m2.mean()),
        },
        "park": {
            "pc2_dynamic_rho": pc2_dyn[0], "pc2_dynamic_p": pc2_dyn[1],
            "pc2_static_rho": pc2_sta[0], "pc2_static_p": pc2_sta[1],
            "broad_dynamic_rho": br_dyn[0], "broad_dynamic_p": br_dyn[1],
            "broad_static_rho": br_sta[0], "broad_static_p": br_sta[1],
            "dynamic_tempdec_mean": float(park.dynamic_model_temperate_deciduous_fraction.mean()),
            "dynamic_tempdec_min": float(park.dynamic_model_temperate_deciduous_fraction.min()),
            "dynamic_tempdec_max": float(park.dynamic_model_temperate_deciduous_fraction.max()),
            "open_pft_8_13_total_cells_2p2_2p7ka": open_count,
            "n_windows": int(len(park)),
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(RUNLOG, FINAL / "FINAL_21KA_RUN.log")
    shutil.copy2(REPORT, FINAL / "UPLIFT_U008_RESULT_20261006.json")
    return report


def build_zip(root: Path) -> str:
    fixed = (2026, 10, 6, 0, 0, 0)
    with zipfile.ZipFile(NEWZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(WORK).as_posix()
            info = zipfile.ZipInfo(rel, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return sha256(NEWZIP)


def replace_exact(path: Path, old: str, new: str) -> None:
    s = path.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit(f"Expected text not found in {path}: {old[:100]}")
    path.write_text(s.replace(old, new, 1), encoding="utf-8")


def update_repo(newsha: str, report: dict) -> None:
    archive = BASE / "model" / "archive" / "PB4Studio_v6.6.3_CHELSA21K_U020_PRE_UFIX.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        shutil.copy2(BASELINE, archive)
    if sha256(archive) != OLD_SHA:
        raise SystemExit("U020 archive hash mismatch")

    aliases = [
        BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip",
        BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip",
        BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip",
    ]
    for dst in aliases:
        shutil.copy2(NEWZIP, dst)
        if sha256(dst) != newsha:
            raise SystemExit(f"Hash mismatch: {dst}")

    payload = BASE / "payload"
    for p in payload.glob("PB4Studio_v6.6.3_CHELSA21K.zip.b64.part*"):
        p.unlink()
    enc = base64.b64encode(NEWZIP.read_bytes()).decode("ascii")
    for k, i in enumerate(range(0, len(enc), 120000), 1):
        (payload / f"PB4Studio_v6.6.3_CHELSA21K.zip.b64.part{k:03d}").write_text(
            enc[i:i + 120000], encoding="ascii"
        )

    rp = BASE / "reconstruct_pb4.py"
    replace_exact(rp, OLD_SHA, newsha)

    sums = BASE / "SHA256SUMS.txt"
    lines = sums.read_text(encoding="utf-8").splitlines()
    rel_aliases = {
        "model/PB4Studio_v6.6.3_CHELSA21K.zip",
        "model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip",
        "model/PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip",
    }
    archive_rel = "model/archive/PB4Studio_v6.6.3_CHELSA21K_U020_PRE_UFIX.zip"
    out, seen = [], set()
    for line in lines:
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[1] in rel_aliases:
            out.append(f"{newsha}  {parts[1]}")
            seen.add(parts[1])
        elif len(parts) == 2 and parts[1] == archive_rel:
            continue
        else:
            out.append(line)
    if seen != rel_aliases:
        raise SystemExit(f"Missing canonical aliases in SHA list: {rel_aliases - seen}")
    out.append(f"{OLD_SHA}  {archive_rel}")
    sums.write_text("\n".join(out) + "\n", encoding="utf-8")

    prov = FINAL / "FINAL_PROVENANCE.json"
    d = json.loads(prov.read_text(encoding="utf-8"))
    d["previous_u020_canonical_sha256"] = OLD_SHA
    d["final_sha256"] = newsha
    d["model_version"] = "6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008"
    d["uplift_m_per_kyr"] = 0.08
    d["uplift_basis"] = (
        "Lee et al. (2024), 80 mm/kyr regional forcing chosen to equal "
        "ca. 22 Ma-to-present Taebaek Mountain exhumation rate"
    )
    d["uplift_interpretation"] = "regional model forcing; not a direct Yongneup uplift measurement"
    d["park2021"] = (
        "independent holdout completed from supplied Supplementary pollen/PCA/temperature; "
        "excluded from tuning and Jang score"
    )
    prov.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mp = BASE / "manuscript" / "FINAL_METHODS_MANUSCRIPT_DRAFT_20261006_KO.md"
    old = (
        "Pelletier et al. (2013)의 원 실험에서는 \\(U=0.05\\ {\\rm m\\,kyr^{-1}}\\)을 사용하였다. "
        "본 연구에서는 동해안 중부의 장기적인 후기 제4기 융기율을 참고하여 "
        "\\(U=0.20\\ {\\rm m\\,kyr^{-1}}\\)을 일정한 regional forcing으로 사용하였다. "
        "Park et al. (2017)은 고성에서 삼척까지 동해안 중부의 해안단구를 검토하고 당시 해수면을 고려했을 때 "
        "MIS 5 이후의 융기율을 약 0.16-0.28 m kyr\\(^{-1}\\)로 제시하였다. "
        "따라서 0.20 m kyr\\(^{-1}\\)은 이 범위 안에 위치한다. 다만 이 값은 용늪 자체에서 직접 측정한 융기율이 "
        "아니라 인접 동해안 중부의 장기 지각융기를 대표하기 위해 적용한 지역값이다."
    )
    new = (
        "Pelletier et al. (2013)의 원 실험에서는 \\(U=0.05\\ {\\rm m\\,kyr^{-1}}\\)을 사용하였다. "
        "본 연구에서는 \\(U=0.08\\ {\\rm m\\,kyr^{-1}}\\), 즉 80 mm kyr\\(^{-1}\\)를 일정한 regional forcing으로 사용하였다. "
        "Lee et al. (2024)은 한반도 태백산맥의 약 22 Ma 이후 장기 삭박 및 exhumation rate와 동일하도록 "
        "landscape-evolution model의 regional uplift를 80 mm kyr\\(^{-1}\\)로 설정하였다. "
        "본 연구도 장기 지형발달의 regional background forcing으로 이 값을 채택하였다. "
        "이는 용늪에서 직접 측정된 지각융기율이 아니며, 장기 삭박 및 exhumation rate를 regional uplift forcing의 "
        "대표값으로 사용하는 모델 가정이다."
    )
    replace_exact(mp, old, new)
    s = mp.read_text(encoding="utf-8").replace(OLD_SHA, newsha)
    oldref = (
        "Park, C.-S., Kim, Y.-H., Nam, W.-H., & Lee, G.-R. (2017). Formative age of coastal terraces "
        "and uplift rate in the East Coast of South Korea. *Journal of the Korean Geomorphological Association, 24*, 43-55."
    )
    newref = (
        "Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). "
        "Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into "
        "the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*, 1091-1120. "
        "https://doi.org/10.5194/esurf-12-1091-2024"
    )
    if oldref in s:
        s = s.replace(oldref, newref)
    mp.write_text(s, encoding="utf-8")

    cp = BASE / "manuscript" / "FINAL_METHODS_CANONICAL_20261006_KO.md"
    replace_exact(
        cp,
        "| \\(U\\) | 0.05 m kyr\\(^{-1}\\) | **0.20 m kyr\\(^{-1}\\)** |",
        "| \\(U\\) | 0.05 m kyr\\(^{-1}\\) | **0.08 m kyr\\(^{-1}\\)** |",
    )
    oldpara = (
        "따라서 \\(S_c=1.50\\)과 \\(U=0.20\\)은 Pelletier et al. (2013)의 원 연구값이라고 쓰면 안 된다. "
        "\\(S_c=1.50\\)은 용늪 20 m real-DEM 수치수렴시험을 거쳐 채택된 모델별 수치설정이다. "
        "\\(U=0.20\\ {\\rm m\\,kyr^{-1}}\\)은 Park et al. (2017)이 고성-삼척의 동해안 중부 해안단구에서 제시한 "
        "약 0.16-0.28 m kyr\\(^{-1}\\)의 후기 제4기 융기율 범위 안에 놓이므로 지역 참고값으로 사용할 수 있다. "
        "다만 이 값은 용늪 자체에서 직접 측정한 융기율이 아니므로, 본 연구에서는 동해안 중부의 장기 지각융기를 대표하는 "
        "일정한 regional forcing으로 취급한다."
    )
    newpara = (
        "따라서 \\(S_c=1.50\\)과 \\(U=0.08\\)은 Pelletier et al. (2013)의 원 연구값이라고 쓰면 안 된다. "
        "\\(S_c=1.50\\)은 용늪 20 m real-DEM 수치수렴시험을 거쳐 채택된 모델별 수치설정이다. "
        "\\(U=0.08\\ {\\rm m\\,kyr^{-1}}\\)은 Lee et al. (2024)이 태백산맥의 약 22 Ma 이후 장기 삭박 및 "
        "exhumation rate와 동일하도록 landscape-evolution model의 regional uplift로 채택한 80 mm kyr\\(^{-1}\\)를 따른다. "
        "이는 용늪 자체의 직접 측정값이 아니라 regional background forcing을 위한 모델 가정이다."
    )
    replace_exact(cp, oldpara, newpara)
    s = cp.read_text(encoding="utf-8")
    oldref2 = (
        "Park, C.-S., Kim, Y.-H., Nam, W.-H., & Lee, G.-R. (2017). Formative age of coastal terraces "
        "and uplift rate in the East Coast of South Korea. Journal of the Korean Geomorphological Association, 24(4), 43-55."
    )
    if oldref2 in s:
        s = s.replace(oldref2, newref.replace("*", ""))
    cp.write_text(s, encoding="utf-8")

    sp = BASE / "manuscript" / "FINAL_METHODS_STRUCTURE_SUMMARY_20261005_KO.md"
    replace_exact(
        sp,
        "\\(U=0.20\\ {\\rm m\\,kyr^{-1}}\\)은 Park et al. (2017)이 고성-삼척 동해안 중부에서 제시한 MIS 5 이후 "
        "0.16-0.28 m kyr\\(^{-1}\\)의 regional uplift 범위 안에 놓인다. 다만 용늪 자체의 직접 측정값이 아니라 인접 "
        "동해안 중부를 대표하는 constant regional forcing으로 기술한다.",
        "\\(U=0.08\\ {\\rm m\\,kyr^{-1}}\\)은 Lee et al. (2024)이 태백산맥의 약 22 Ma 이후 장기 삭박 및 "
        "exhumation rate와 동일하도록 사용한 80 mm kyr\\(^{-1}\\) regional uplift 설정을 따른다. 용늪 자체의 직접 "
        "측정값이 아니라 regional background forcing을 위한 모델 가정으로 기술한다.",
    )

    ap = BASE / "manuscript" / "METHODS_ORIGINAL_SOURCE_AUDIT_20261006_KO.md"
    replace_exact(
        ap,
        "| \\(U\\) | Pelletier 원 연구는 0.05 m kyr-1 | 용늪 production은 0.20 m kyr-1이나 project source에는 지역 참고값이라는 주석만 존재 | 문헌 보강 필요 |",
        "| \\(U\\) | Pelletier 원 연구는 0.05 m kyr-1. Lee et al. (2024)은 태백산맥 약 22 Ma 이후 장기 삭박 및 "
        "exhumation rate와 동일한 80 mm kyr-1를 regional uplift로 채택 | 용늪 production은 0.08 m kyr-1. "
        "용늪 직접 측정값이 아니라 regional background forcing을 위한 모델 가정 | 확인 |",
    )
    s = ap.read_text(encoding="utf-8")
    if "Lee et al. (2024): https://doi.org/10.5194/esurf-12-1091-2024" not in s:
        s = s.replace(
            "- Pelletier et al. (2013): https://doi.org/10.1002/jgrf.20046",
            "- Pelletier et al. (2013): https://doi.org/10.1002/jgrf.20046\n"
            "- Lee et al. (2024): https://doi.org/10.5194/esurf-12-1091-2024",
        )
    ap.write_text(s, encoding="utf-8")

    sap = BASE / "manuscript" / "FINAL_METHODS_SOURCE_AUDIT_20261006_KO.md"
    s = sap.read_text(encoding="utf-8")
    s = s.replace("U=0.20\\ {\\rm m\\,kyr^{-1}}", "U=0.08\\ {\\rm m\\,kyr^{-1}}")
    s = s.replace(
        "Park et al. (2017)은 고성-삼척 동해안 중부에서 당시 해수면을 고려한 MIS 5 이후 융기율을 "
        "0.16-0.28 m kyr\\(^{-1}\\)로 정리하였다. 따라서 0.20은 이 범위에 포함된다.",
        "Lee et al. (2024)은 landscape-evolution model의 regional uplift를 80 mm kyr\\(^{-1}\\)로 설정했으며, "
        "이 값을 태백산맥의 약 22 Ma 이후 장기 삭박 및 exhumation rate와 동일하게 선택했다고 명시하였다. "
        "용늪에서는 이 0.08 m kyr\\(^{-1}\\)를 regional background forcing으로 채택하며, 용늪 직접 측정 융기율로 해석하지 않는다.",
    )
    oldref3 = (
        "Park, C.-S., Kim, Y.-H., Nam, W.-H., & Lee, G.-R. (2017). Formative age of coastal terraces "
        "and uplift rate in the East Coast of South Korea. *Journal of the Korean Geomorphological Association, 24*, 43-55."
    )
    if oldref3 in s:
        s = s.replace(oldref3, newref)
    s = s.replace("- 동해안 중부 regional uplift 문헌", "- 태백산맥 장기 삭박 및 exhumation 기반 regional uplift 문헌")
    sap.write_text(s, encoding="utf-8")

    pk = report["park"]
    (FINAL / "PARK2021_HOLDOUT_RESULT_20261006_KO.md").write_text(
        f"""# Park et al. (2021) 독립 holdout 검증 결과

작성일: 2026-10-06
대상 모델: **PB4-FINAL-nativeClimate-BIOME4AGB-U008**
최종 canonical SHA-256: `{newsha}`

## 자료 및 원칙

사용자가 제공한 Park et al. (2021) Supplementary Excel의 pollen, PCA, temperature reconstruction을 사용하였다. 주 정량구간은 16-69 cm의 53 pollen samples이며, 원 연대에 따라 가장 가까운 100년 PB4 output window에 배정하여 17개 window로 집계하였다. 시료 사이 보간은 하지 않았고 이 자료를 모델 재보정에 사용하지 않았다.

## PC2 cold-warm signal

- dynamic: Spearman rho = **{pk['pc2_dynamic_rho']:.3f}**, p = **{pk['pc2_dynamic_p']:.5g}**, n = 17
- static: Spearman rho = **{pk['pc2_static_rho']:.3f}**, p = **{pk['pc2_static_p']:.5g}**, n = 17

## broadleaf-conifer signal

- dynamic: Spearman rho = **{pk['broad_dynamic_rho']:.3f}**, p = **{pk['broad_dynamic_p']:.5g}**, n = 17
- static: Spearman rho = **{pk['broad_static_rho']:.3f}**, p = **{pk['broad_static_p']:.5g}**, n = 17
- dynamic temperate-deciduous fraction mean = **{pk['dynamic_tempdec_mean']:.6f}**
- range = **{pk['dynamic_tempdec_min']:.6f}-{pk['dynamic_tempdec_max']:.6f}**

## 2738-2206 cal yr BP open-vegetation event

2.2-2.7 ka의 dynamic PB4에서 PFT8-PFT13 dominant-cell 총계는 **{pk['open_pft_8_13_total_cells_2p2_2p7ka']:.0f}**이다.

## 판정

Park et al. (2021)은 Jang accuracy score에 합치지 않는 독립 holdout이다. U를 0.08 m kyr^-1로 교정한 production 결과로 위 통계를 다시 산출하였다.
""",
        encoding="utf-8",
    )

    ag = pd.read_csv(FINAL / "FINAL_AGB_SUMMARY.csv", encoding="utf-8-sig")
    dynag = ag[ag["mode"] == "dynamic"].iloc[0]
    staag = ag[ag["mode"] == "static"].iloc[0]
    g = report["dynamic"]
    (FINAL / "FINAL_INTEGRATED_DECISION_KO.md").write_text(
        f"""# PB4 final integrated production result

Final SHA-256: {newsha}

## Scientific configuration

- BIOME4 v4.2b2 native PFT climate limits
- McKenzie AWC and finite-depth root coupling
- BIOME4-derived AGB*
- Pelletier geomorphic coupling with kd=0.033 EEMT + 0.05 AGB*
- regional uplift U=0.08 m kyr^-1 = 80 mm kyr^-1, Lee et al. (2024) 기반
- U는 용늪 직접 측정값이 아니라 regional background forcing을 위한 모델 가정

## Primary Jang validation

- static: 24/62 = 38.7097%
- dynamic: 55/62 = 88.7097%

## 21 ka dynamic geomorphic change

- mean elevation: {g['mean_elev_21ka']:.6f} -> {g['mean_elev_0ka']:.6f} m
- change: {g['delta_mean_elev_m']:+.6f} m
- mean soil depth: {g['mean_soil_21ka']:.6f} -> {g['mean_soil_0ka']:.6f} m
- change: {g['delta_mean_soil_m']:+.6f} m

## AGB*

- dynamic time mean: {dynag.time_mean_agb_kg_m2:.9f} kg m^-2
- dynamic modern 0 ka: {dynag.modern_0ka_agb_kg_m2:.9f} kg m^-2
- static time mean: {staag.time_mean_agb_kg_m2:.9f} kg m^-2
- static modern 0 ka: {staag.modern_0ka_agb_kg_m2:.9f} kg m^-2

## Park et al. (2021)

- PC2 vs dynamic cold-tree fraction: rho={pk['pc2_dynamic_rho']:.3f}, p={pk['pc2_dynamic_p']:.5g}
- PC2 vs static cold-tree fraction: rho={pk['pc2_static_rho']:.3f}, p={pk['pc2_static_p']:.5g}
- broadleaf pollen vs dynamic temperate-deciduous fraction: rho={pk['broad_dynamic_rho']:.3f}, p={pk['broad_dynamic_p']:.5g}
- Park 자료는 독립 holdout이며 모델 재보정에 사용하지 않음
""",
        encoding="utf-8",
    )

    (FINAL / "UPLIFT_U008_CORRECTION_20261006_KO.md").write_text(
        f"""# PB4 uplift U correction audit

- 2026-08-20 한국지형학회 발표 확정값: **80 mm kyr^-1 = 0.08 m kyr^-1**
- 근거: Lee et al. (2024), Earth Surface Dynamics 12, 1091-1120
- 이전 canonical 실제 기본값: 0.20 m kyr^-1
- 교정 production: **0.08 m kyr^-1**
- 이전 U020 SHA-256: `{OLD_SHA}`
- 교정 U008 SHA-256: `{newsha}`

Jang static은 24/62, dynamic은 55/62로 변하지 않았다. 반면 dynamic 21 ka 평균고도 변화는 U020에서 +3.256468 m였고 U008에서는 {g['delta_mean_elev_m']:+.6f} m이다. 따라서 U는 식생 검증점수를 바꾸지 않았지만 지형 결과에는 실질적인 영향을 주므로 package와 Methods를 함께 교정하였다.

80 mm kyr^-1은 용늪에서 직접 관측한 지각융기율이 아니다. Lee et al. (2024)이 태백산맥의 약 22 Ma 이후 장기 삭박 및 exhumation rate에 맞추어 regional uplift forcing으로 사용한 값을 채택한 모델 가정이다.
""",
        encoding="utf-8",
    )

    for p in (BASE / "manuscript").glob("*.md"):
        txt = p.read_text(encoding="utf-8")
        if re.search(r"U\s*=\s*0\.20|U=0\.20", txt):
            raise SystemExit(f"Stale U020 remains in manuscript: {p}")

    subprocess.run([sys.executable, str(BASE / "reconstruct_pb4.py")], check=True, cwd=REPO)
    rebuilt = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    if sha256(rebuilt) != newsha:
        raise SystemExit("Reconstructed package hash mismatch")
    rebuilt.unlink()


def main() -> None:
    root = prepare()
    run_model(root)
    report = rebuild_science(root)
    newsha = build_zip(root)
    update_repo(newsha, report)
    print("=== U008 PROMOTION COMPLETE ===")
    print("SHA256", newsha)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
