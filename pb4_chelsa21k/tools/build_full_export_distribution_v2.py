#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"anchor not found: {label}")
    return text.replace(old, new, 1)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-zip", required=True)
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--exporter", required=True)
    args=ap.parse_args()

    src=Path(args.source_zip).resolve()
    work=Path(args.work_dir).resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    with zipfile.ZipFile(src) as z:
        z.extractall(work)
    roots=[p for p in work.iterdir() if p.is_dir() and p.name.startswith("PB4Studio")]
    if len(roots)!=1:
        raise RuntimeError(f"expected one PB4Studio root, got {roots}")
    root=roots[0]

    # Post-processing exporter.
    shutil.copy2(Path(args.exporter), root/"tools"/"export_all_outputs.py")

    # 1) Force every 0.1-kyr model time to be a snapshot output.
    runp=root/"tools"/"run_yongneup_21ka_chelsa_selfcontained.py"
    s=runp.read_text(encoding="utf-8")
    old="time=TimeConfig(start_ka=21.0,end_ka=0.0,interval_kyr=0.1,snapshot_ka=(21.0,20.0,15.0,10.0,5.9,5.0,4.2,4.0,3.0,2.0,1.0,0.0)),"
    new="time=TimeConfig(start_ka=21.0,end_ka=0.0,interval_kyr=0.1,snapshot_ka=tuple(round(21.0-0.1*i,1) for i in range(211))),"
    s=replace_once(s,old,new,"all 211 snapshots")
    runp.write_text(s,encoding="utf-8")

    # 2) Add non-invasive per-time diagnostics to runner.
    rp=root/"pb4studio"/"runner.py"
    s=rp.read_text(encoding="utf-8")

    s=replace_once(
        s,
        "    summary_rows: List[Dict[str, object]] = []\n    snapshot_rows: List[Dict[str, object]] = []\n",
        "    summary_rows: List[Dict[str, object]] = []\n"
        "    snapshot_rows: List[Dict[str, object]] = []\n"
        "    forcing_rows: List[Dict[str, object]] = []\n",
        "forcing rows init",
    )

    anchor='''        row.update({
            "case": output_subdir,
            "geomorph_dynamic": dynamic_on,
            "biome4_variant": str(run_config.science.biome4_variant),
        })
'''
    insert='''        row.update({
            "case": output_subdir,
            "geomorph_dynamic": dynamic_on,
            "biome4_variant": str(run_config.science.biome4_variant),
        })

        # FULL_EXPORT diagnostics only. These read already-computed arrays and do
        # not alter BIOME4 or geomorphic state.
        def _pb4_stats(name, arr):
            a = np.asarray(arr, dtype="float64")
            if a.shape != igrid.shape:
                return
            m = igrid.land & np.isfinite(a)
            v = a[m]
            row[f"mean_{name}"] = float(np.mean(v)) if v.size else float("nan")
            row[f"sd_{name}"] = float(np.std(v)) if v.size else float("nan")
            row[f"min_{name}"] = float(np.min(v)) if v.size else float("nan")
            row[f"max_{name}"] = float(np.max(v)) if v.size else float("nan")

        for _name, _key in [
            ("lai", "lai_node"),
            ("aet_mm_yr", "aet_node"),
            ("wetness", "wetness_node"),
            ("runoff_mm_yr", "runoff_node"),
            ("firedays", "firedays_node"),
            ("greendays", "greendays_node"),
            ("gdd0", "gdd0_node"),
            ("gdd5", "gdd5_node"),
            ("tcm_C", "tcm_node"),
            ("whc_total_dynamic_mm", "whc_total_dynamic_mm"),
        ]:
            if _key in veg:
                _pb4_stats(_name, veg[_key])

        _ann_temp = np.nanmean(np.asarray(temp, dtype="float64"), axis=0)
        _ann_prec = np.nansum(np.asarray(prec, dtype="float64"), axis=0)
        _ann_cloud = np.nanmean(np.asarray(cloud, dtype="float64"), axis=0)
        _pb4_stats("annual_mean_temp_C", _ann_temp)
        _pb4_stats("annual_precip_mm", _ann_prec)
        _pb4_stats("annual_mean_cloud_pct", _ann_cloud)
        _pb4_stats("absolute_min_temp_C", tmin)
        row["co2_ppm"] = float(co2)

        _aet_ann = np.asarray(veg.get("aet_node", np.full(igrid.shape, np.nan)), dtype="float64")
        _peff = _ann_prec - _aet_ann
        _pb4_stats("annual_effective_precip_mm", _peff)

        # PFT diagnostics: basin mean values and constraint-pass fractions.
        for _p in range(1, 14):
            for _kind, _suffix in [
                ("npp", "mod_npp_node"),
                ("lai", "mod_lai_node"),
                ("aet", "aet_node"),
                ("wetness", "wetness_node"),
                ("firedays", "firedays_node"),
                ("greendays", "greendays_node"),
            ]:
                _k=f"pft{_p:02d}_{_suffix}"
                if _k in veg:
                    _a=np.asarray(veg[_k],dtype="float64")
                    _m=igrid.land & np.isfinite(_a)
                    _v=_a[_m]
                    row[f"pft{_p:02d}_{_kind}_mean"] = float(np.mean(_v)) if _v.size else float("nan")
            _k=f"pft{_p:02d}_constraint_pass_node"
            if _k in veg:
                _a=np.asarray(veg[_k],dtype="float64")
                _m=igrid.land & np.isfinite(_a)
                _v=_a[_m]
                row[f"pft{_p:02d}_constraint_pass_fraction"] = float(np.mean(_v>0)) if _v.size else float("nan")

        # Monthly climate/AET table. Values are basin means; precipitation and
        # AET retain their original monthly mm totals.
        for _mi in range(12):
            _tm=np.asarray(temp[_mi],dtype="float64")
            _pm=np.asarray(prec[_mi],dtype="float64")
            _cm=np.asarray(cloud[_mi],dtype="float64")
            _ak=f"aet_month_{_mi+1:02d}_node"
            _am=np.asarray(veg.get(_ak,np.full(igrid.shape,np.nan)),dtype="float64")
            _mask=igrid.land
            forcing_rows.append({
                "case": output_subdir,
                "geomorph_dynamic": dynamic_on,
                "ka_bp": float(ka),
                "month": int(_mi+1),
                "temperature_C_mean": float(np.nanmean(_tm[_mask])),
                "precipitation_mm_mean": float(np.nanmean(_pm[_mask])),
                "cloud_pct_mean": float(np.nanmean(_cm[_mask])),
                "aet_mm_mean": float(np.nanmean(_am[_mask])),
                "co2_ppm": float(co2),
            })
'''
    s=replace_once(s,anchor,insert,"summary diagnostics")

    old_snap='''            if "lai_node" in veg:
                snapshot_fields["lai"] = np.asarray(veg["lai_node"], dtype="float32")
            if "bgc_rootspace_node" in veg:
'''
    new_snap='''            if "lai_node" in veg:
                snapshot_fields["lai"] = np.asarray(veg["lai_node"], dtype="float32")
            for _out_name, _veg_key in [
                ("aet_mm_yr", "aet_node"),
                ("wetness", "wetness_node"),
                ("runoff_mm_yr", "runoff_node"),
                ("firedays", "firedays_node"),
                ("greendays", "greendays_node"),
                ("gdd0", "gdd0_node"),
                ("gdd5", "gdd5_node"),
                ("tcm_C", "tcm_node"),
                ("whc_total_dynamic_mm", "whc_total_dynamic_mm"),
            ]:
                if _veg_key in veg:
                    snapshot_fields[_out_name] = np.asarray(veg[_veg_key], dtype="float32")
            snapshot_fields["annual_mean_temp_C"] = np.nanmean(np.asarray(temp,dtype="float64"),axis=0).astype("float32")
            snapshot_fields["annual_precip_mm"] = np.nansum(np.asarray(prec,dtype="float64"),axis=0).astype("float32")
            snapshot_fields["annual_mean_cloud_pct"] = np.nanmean(np.asarray(cloud,dtype="float64"),axis=0).astype("float32")
            snapshot_fields["absolute_min_temp_C"] = np.asarray(tmin,dtype="float32")
            snapshot_fields["co2_ppm"] = np.full(igrid.shape,float(co2),dtype="float32")
            if "aet_node" in veg:
                snapshot_fields["annual_effective_precip_mm"] = (
                    np.nansum(np.asarray(prec,dtype="float64"),axis=0)
                    - np.asarray(veg["aet_node"],dtype="float64")
                ).astype("float32")
            if "bgc_rootspace_node" in veg:
'''
    s=replace_once(s,old_snap,new_snap,"snapshot extra fields")

    out_anchor='''    pd.DataFrame(summary_rows).to_csv(res_dir / "summary_timeseries.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(snapshot_rows).to_csv(res_dir / "snapshot_summary.csv", index=False, encoding="utf-8-sig")
'''
    out_new='''    pd.DataFrame(summary_rows).to_csv(res_dir / "summary_timeseries.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(snapshot_rows).to_csv(res_dir / "snapshot_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(forcing_rows).to_csv(res_dir / "monthly_forcing_timeseries.csv", index=False, encoding="utf-8-sig")
'''
    s=replace_once(s,out_anchor,out_new,"monthly forcing output")
    rp.write_text(s,encoding="utf-8")

    # 3) Ensure Excel dependency for user-side export.
    req=root/"requirements.txt"
    lines=[x.strip() for x in req.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not any(x.lower().startswith("openpyxl") for x in lines):
        lines.append("openpyxl>=3.1")
    req.write_text("\n".join(lines)+"\n",encoding="utf-8")

    # 4) One-click runner.
    (root/"RUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat").write_text(
        "@echo off\r\n"
        "setlocal\r\n"
        "cd /d %~dp0\r\n"
        "echo [1/2] Running PB4 Yongneup 21 ka, all 211 time steps...\r\n"
        "python tools\\run_yongneup_21ka_chelsa_selfcontained.py\r\n"
        "if errorlevel 1 goto :fail\r\n"
        "echo [2/2] Exporting Excel, CSV and figures...\r\n"
        "python tools\\export_all_outputs.py --root . --outputs outputs_CHELSA21K\r\n"
        "if errorlevel 1 goto :fail\r\n"
        "echo DONE. See outputs_CHELSA21K\\FULL_EXPORT\r\n"
        "pause\r\nexit /b 0\r\n"
        ":fail\r\necho FAILED. Check the console output.\r\npause\r\nexit /b 1\r\n",
        encoding="utf-8",
    )

    (root/"README_FULL_EXPORT_KO.txt").write_text(
        "PB4Studio v6.6.3 CHELSA21K U008 FULL EXPORT v2\n"
        "================================================\n\n"
        "과학 설정은 canonical U=0.08 m/kyr production과 동일하며 출력 계측만 추가했습니다.\n\n"
        "실행:\n"
        "1) FIRST_RUN_SETUP.bat 최초 1회\n"
        "2) RUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat\n\n"
        "기록 범위:\n"
        "- 21.0-0.0 ka BP, 0.1 kyr 간격, 총 211 시점\n"
        "- static/dynamic 모두 211 시점 summary\n"
        "- static/dynamic 모두 211 시점 raw snapshot 폴더\n"
        "- 각 raw snapshot: 고도, 토심, NPP, LAI, AET, EEMT, AGB*, PFT/식생, 수분, runoff, 기후요약 등 GeoTIFF와 cell_values.csv\n"
        "- monthly_forcing_timeseries.csv: 211 x 12개월의 T/P/cloud/AET/CO2\n"
        "- FULL_EXPORT Excel: 주요 변수 + 모든 summary 열 + monthly forcing + validation + run config + manifest\n\n"
        "주의: 추가 저장 기능은 이미 계산된 배열을 기록하는 후처리 계측이며 과학 계산식을 변경하지 않습니다.\n",
        encoding="utf-8",
    )
    print(root)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
