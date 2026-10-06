from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT_NAME = "PB4Studio_v6.6.3_CHELSA21K"
VERSION = "6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008"

ap = argparse.ArgumentParser(
    description="Audit/fix the PB4 U008 distribution without changing science equations."
)
ap.add_argument("--source-zip", required=True)
ap.add_argument("--output-zip", required=True)
ap.add_argument("--work-dir", default="")
ns = ap.parse_args()

SRC = Path(ns.source_zip).resolve()
OUT = Path(ns.output_zip).resolve()
WORK = (
    Path(ns.work_dir).resolve()
    if ns.work_dir
    else Path(tempfile.mkdtemp(prefix="pb4_u008_audit_"))
)
if WORK.exists() and ns.work_dir:
    shutil.rmtree(WORK)
WORK.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)
root = WORK / ROOT_NAME
if not root.is_dir():
    raise SystemExit(f"package root missing: {root}")


def rep(path: Path, old: str, new: str, count: int = 1) -> None:
    p = root / path
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise RuntimeError(f"anchor missing {path}: {old[:80]!r}")
    p.write_text(s.replace(old, new, count), encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Primary validation must be exactly the finalized Jang-2011 evaluation.
#    Park-2021 is an independent holdout and must not enter categorical score.
# ---------------------------------------------------------------------------
nat = root / "pb4studio/embedded_data/nationwide_validation.csv"
rows = list(csv.DictReader(nat.open(encoding="utf-8-sig", newline="")))
selected = []
fix = {
    "95_01": (
        1,
        "1",
        "deciduous_broadleaf_forest",
        "Jang 2011 corrected reduced mapping: cool-temperate central/montane deciduous broad-leaved forest -> broadleaf.",
    ),
    "95_02": (
        2,
        "2",
        "mixed_forest",
        "Jang 2011 corrected reduced mapping: cool-temperate northern/alti-montane mixed coniferous and deciduous broad-leaved forest -> mixed.",
    ),
    "95_03": (
        1,
        "1",
        "deciduous_broadleaf_forest",
        "Jang 2011 corrected reduced mapping: cool-temperate central/montane deciduous broad-leaved forest -> broadleaf.",
    ),
    "95_04": (
        2,
        "2",
        "mixed_forest",
        "Jang 2011 corrected reduced mapping: cool-temperate central/montane mixed deciduous broad-leaved and coniferous forest -> mixed.",
    ),
}
for r in rows:
    rid = str(r.get("record_id", ""))
    if rid not in fix:
        continue
    code, codes, label, note = fix[rid]
    r["expected_vegetation_code"] = str(code)
    r["accepted_reduced_codes"] = codes
    r["accepted_reduced_labels"] = label
    r["notes"] = note
    selected.append(r)

if [r["record_id"] for r in selected] != ["95_01", "95_02", "95_03", "95_04"]:
    raise RuntimeError([r["record_id"] for r in selected])

primary = root / "pb4studio/embedded_data/yongneup_jang2011_primary_validation.csv"
with primary.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(selected)
nat.unlink()

(root / "pb4studio/embedded_data/README_VALIDATION_KO.txt").write_text(
    "PB4 Yongneup production primary validation\n"
    "==========================================\n"
    "주 검증은 Jang et al. (2011) record 95_01~95_04만 사용합니다.\n"
    "corrected reduced mapping: 95_01=활엽수림(1), 95_02=혼효림(2), "
    "95_03=활엽수림(1), 95_04=혼효림(2).\n"
    "0.1 kyr 출력에서 평가수는 62입니다. 1% criterion의 최종 기준값은 "
    "static 24/62, dynamic 55/62입니다.\n"
    "Park et al. (2021)은 독립 holdout이며 이 categorical primary score에 합치지 않습니다.\n",
    encoding="utf-8",
)

rep(
    Path("pb4studio/runner.py"),
    'return Path(__file__).resolve().parent / "embedded_data" / "nationwide_validation.csv"',
    'return Path(__file__).resolve().parent / "embedded_data" / "yongneup_jang2011_primary_validation.csv"',
)

rep(
    Path("pb4studio/validation.py"),
    """    # IMPORTANT compatibility rule: the palaeovegetation threshold calculation
    # keeps the validated pre-hotfix4 denominator semantics. Explicit code 4
    # (무식생·나지) is visible in maps/coverage graphs but is not added to the
    # 0..3 palaeovegetation validation denominator. This prevents a visualization
    # fix from silently changing the established 66/86, 41/86, 39/86 results.
""",
    """    # Primary Yongneup validation denominator: mapped vegetation classes 0--3.
    # Explicit class 4 (non-vegetated/bare) remains visible in maps but is excluded
    # from the vegetation-presence denominator, matching the finalized Jang-2011
    # 1% basin-presence calculation (62 output-time evaluations).
""",
)

# ---------------------------------------------------------------------------
# 2. Standard report is for a 21 ka run, not the old 100 ka product.
# ---------------------------------------------------------------------------
rep(Path("pb4studio/standard_report.py"), "100/50/10/1 ka", "21/10/5/0 ka", 3)
rep(
    Path("pb4studio/standard_report.py"),
    "REPORT_AGES_KA: Tuple[float, ...] = (100.0, 50.0, 10.0, 1.0)",
    "REPORT_AGES_KA: Tuple[float, ...] = (21.0, 10.0, 5.0, 0.0)",
)
rep(
    Path("gui/tab_results.py"),
    "100/50/10/1 ka + time series + validation",
    "21/10/5/0 ka + time series + validation",
)
rep(Path("gui/tab_results.py"), "100·50·10·1 ka", "21·10·5·0 ka", 3)
rep(
    Path("tools/make_standard_result_figures.py"),
    "Use nearest saved snapshot when 100/50/10/1 ka is missing",
    "Use nearest saved snapshot when a 21/10/5/0 ka standard age is missing",
)
rep(
    Path("tools/make_standard_result_figures.py"),
    'default=str(ROOT / "outputs_hotfix10n10_selfcontained")',
    'default=str(ROOT / "outputs_CHELSA21K")',
)

# ---------------------------------------------------------------------------
# 3. GUI default raw snapshot export = every 0.1 kyr output time.
# ---------------------------------------------------------------------------
rep(Path("gui/state.py"), "snapshot_interval_ka: float = 5.0", "snapshot_interval_ka: float = 0.0")
rep(
    Path("gui/state.py"),
    "for age in (100.0, 50.0, 10.0, 1.0):",
    "for age in (21.0, 10.0, 5.0, 0.0):",
)
rep(
    Path("gui/tab_time_mode.py"),
    "self.snapshot_interval_spin.setValue(5.0)",
    "self.snapshot_interval_spin.setValue(0.0)",
)
rep(
    Path("gui/tab_time_mode.py"),
    'validation_group = QGroupBox("고식생 검증")',
    'validation_group = QGroupBox("고식생 검증 — Jang et al. (2011) 주 검증")',
)
rep(
    Path("gui/tab_time_mode.py"),
    'self.validation_accuracy_method_combo.addItem("출력시점(dt)별 일치율", userData="per_output_time")',
    'self.validation_accuracy_method_combo.addItem("주 검증: 출력시점(dt)별 일치율", userData="per_output_time")',
)
rep(
    Path("gui/tab_time_mode.py"),
    'self.validation_accuracy_method_combo.addItem("구간 내 최소 1회(dt) 출현율", userData="interval_any_dt")',
    'self.validation_accuracy_method_combo.addItem("보조: 구간 내 최소 1회(dt) 출현율", userData="interval_any_dt")',
)

# ---------------------------------------------------------------------------
# 4. Windows launchers and contract checker.
# ---------------------------------------------------------------------------
(root / "MAKE_STANDARD_RESULT_FIGURES.bat").write_text(
    r"""@echo off
setlocal
cd /d "%~dp0"
set "OUT=%~1"
if "%OUT%"=="" set "OUT=outputs_CHELSA21K"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\make_standard_result_figures.py "%OUT%"
) else (
  python tools\make_standard_result_figures.py "%OUT%"
)
if errorlevel 1 (
  echo.
  echo Standard result figure generation FAILED.
  pause
  exit /b 1
)
echo.
echo Finished. Figures are in %OUT%\standard_report
pause
""",
    encoding="utf-8",
)

(root / "RUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat").write_text(
    r"""@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)
echo [1/2] Running PB4 Yongneup 21 ka, all 211 time steps...
%PY% tools\run_yongneup_21ka_chelsa_selfcontained.py
if errorlevel 1 goto :fail
echo [2/2] Exporting Excel, CSV and figures...
%PY% tools\export_all_outputs.py --root . --outputs outputs_CHELSA21K
if errorlevel 1 goto :fail
echo DONE. See outputs_CHELSA21K\FULL_EXPORT
pause
exit /b 0
:fail
echo FAILED. Check the console output.
pause
exit /b 1
""",
    encoding="utf-8",
)

contract = r"""from pathlib import Path
import csv, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import pb4studio
from pb4studio.pelletier_geomorph import PelletierStrictConfig
from pb4studio.standard_report import REPORT_AGES_KA
EXPECTED='6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008'
assert pb4studio.__version__ == EXPECTED, (pb4studio.__version__, EXPECTED)
assert abs(PelletierStrictConfig().uplift_m_per_kyr-0.08)<1e-15
assert abs(PelletierStrictConfig().hillslope_critical_slope-1.50)<1e-15
assert tuple(REPORT_AGES_KA)==(21.0,10.0,5.0,0.0), REPORT_AGES_KA
p=ROOT/'pb4studio/embedded_data/yongneup_jang2011_primary_validation.csv'
rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
assert [r['record_id'] for r in rows]==['95_01','95_02','95_03','95_04']
assert [int(float(r['expected_vegetation_code'])) for r in rows]==[1,2,1,2]
assert not any(str(r['record_id']).startswith('92_') for r in rows)
runner=(ROOT/'pb4studio/runner.py').read_text(encoding='utf-8')
assert 'yongneup_jang2011_primary_validation.csv' in runner
fig=(ROOT/'pb4studio/figures.py').read_text(encoding='utf-8')
for token in ['set_xlim(21, 0)','color="firebrick", linewidth=1.6','color="royalblue", linewidth=1.4','frameon=False']:
    assert token in fig, token
for target in ['tools/run_yongneup_21ka_chelsa_selfcontained.py','tools/export_all_outputs.py','tools/make_standard_result_figures.py']:
    assert (ROOT/target).is_file(), target
print('PASS PB4 PACKAGE CONTRACT')
print('VERSION',EXPECTED)
print('PRIMARY_VALIDATION','Jang2011 corrected mapping n=62; Park2021 excluded')
print('REPORT_AGES_KA',REPORT_AGES_KA)
"""
(root / "tools/check_package_contract.py").write_text(contract, encoding="utf-8")

(root / "CHECK_CHELSA21K_CONTRACT.bat").write_text(
    r"""@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\check_package_contract.py
) else (
  python tools\check_package_contract.py
)
if errorlevel 1 pause
""",
    encoding="utf-8",
)

# ---------------------------------------------------------------------------
# 5. Plot scripts shipped in the ZIP must use paths that exist in the ZIP.
# ---------------------------------------------------------------------------
for fname in ["plot_mean_elevation.py", "plot_mean_soil_depth.py", "plot_mean_npp.py"]:
    p = root / "plots" / fname
    s = p.read_text(encoding="utf-8")
    s = s.replace(
        'DATA_PATH = ROOT / "results" / "final_integrated_20261006" / "FINAL_AGB_21KA_TIMESERIES.csv"',
        '''STATIC_PATH = ROOT / "outputs_CHELSA21K" / "model_static" / "summary_timeseries.csv"
DYNAMIC_PATH = ROOT / "outputs_CHELSA21K" / "model_dynamic" / "summary_timeseries.csv"''',
    )
    s = s.replace(
        'raw = pd.read_csv(DATA_PATH, encoding="utf-8-sig")\n'
        '    dynamic = raw[raw["mode"] == "dynamic"].sort_values("ka_bp", ascending=False)\n'
        '    static = raw[raw["mode"] == "static"].sort_values("ka_bp", ascending=False)',
        '''static = pd.read_csv(STATIC_PATH, encoding="utf-8-sig").sort_values("ka_bp", ascending=False)
    dynamic = pd.read_csv(DYNAMIC_PATH, encoding="utf-8-sig").sort_values("ka_bp", ascending=False)''',
    )
    p.write_text(s, encoding="utf-8")

p = root / "plots/plot_chelsa_climate.py"
s = p.read_text(encoding="utf-8").replace(
    'DATA_PATH = ROOT / "data" / "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"',
    'DATA_PATH = ROOT / "embedded_inputs" / "yongneup_exact20m" / "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"',
)
p.write_text(s, encoding="utf-8")

# ---------------------------------------------------------------------------
# 6. Clarify legacy serialization-only fields; production science unchanged.
# ---------------------------------------------------------------------------
p = root / "pb4studio/config.py"
s = p.read_text(encoding="utf-8")
s = s.replace(
    "    eemt_clip_min_mj_m2_yr: float = 1.0\n"
    "    eemt_clip_max_mj_m2_yr: float = 80.0\n",
    """    # Legacy serialization-only fields. Production EEMT is not clipped.
    eemt_clip_min_mj_m2_yr: float = 1.0
    eemt_clip_max_mj_m2_yr: float = 80.0
""",
)
s = s.replace(
    """    # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
    # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
    # not prognose standing AGB, so this legacy bridge is retained only to keep
    # the existing Pelletier runner operational. It is NOT part of the claimed
    # pure-BIOME4 vegetation response and remains explicitly unresolved for a
    # future reference-only AGB coupling.
""",
    """    # Legacy serialization-only NPP->AGB fields. Production kd uses the
    # Reich-LAI + Haxeltine/Prentice living-sapwood AGB* implemented in climate.py.
    # The 0.010*NPP quantity is retained only as a diagnostic comparison output.
""",
)
p.write_text(s, encoding="utf-8")

# ---------------------------------------------------------------------------
# 7. Remove stale/unused distribution baggage.
# ---------------------------------------------------------------------------
for q in [
    root / "embedded_inputs/yongneup",
    root / "fortran_src/_biome4_fortran_batch_build_mckenzie2003",
]:
    if q.exists():
        shutil.rmtree(q)

for q in [
    root / "embedded_inputs/yongneup_exact20m/climate_yongneup_128.25E_38.25N.csv",
    root / "embedded_inputs/yongneup_exact20m/yongneup_initial_grid_20m_exact.npz",
]:
    if q.exists():
        q.unlink()

for q in root.rglob("__pycache__"):
    shutil.rmtree(q, ignore_errors=True)
for q in root.rglob("*.pyc"):
    q.unlink(missing_ok=True)

(root / "README_FULL_EXPORT_KO.txt").write_text(
    f"""PB4Studio CHELSA21K U008 AUDITED FULL EXPORT
===============================================

버전
- {VERSION}
- regional uplift U = 0.08 m/kyr

실행
1. FIRST_RUN_SETUP.bat 최초 1회
2. START_PB4Studio.bat: GUI
3. RUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat: 21 ka 전체 실행 및 전체 출력

시간축/출력
- 21.0 ka BP -> 0.0 ka BP
- 0.1 kyr 간격, 총 211 시점
- GUI 기본도 매 스텝 snapshot 저장(스냅샷 간격 0)
- 표준 결과판 지도 시점: 21, 10, 5, 0 ka BP

주 고식생 검증
- Jang et al. (2011) 4개 record만 사용
- corrected reduced mapping: 95_01=활엽수림, 95_02=혼효림, 95_03=활엽수림, 95_04=혼효림
- 0.1 kyr output-time 평가 n=62
- 1% criterion 기준 최종 회귀값: static 24/62, dynamic 55/62
- Park et al. (2021)은 독립 holdout이며 주 정확도에 합산하지 않음

고도/토심/NPP 시계열 그림
- plot_chelsa_climate.py와 동일한 형식
- x축 21 -> 0 ka BP
- 동적모델 firebrick 1.6, 정적모델 royalblue 1.4
- 제목/grid 없음, 범례 좌상단 frame 없음, PNG 600 dpi

CHECK_CHELSA21K_CONTRACT.bat으로 패키지 계약을 점검할 수 있습니다.
""",
    encoding="utf-8",
)

for pat in [
    "66/86",
    "41/86",
    "39/86",
    "outputs_hotfix10n10_selfcontained",
    "test_chelsa21k_contract.py",
]:
    found = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".py", ".txt", ".md", ".bat"}:
            if pat in p.read_text(encoding="utf-8", errors="ignore"):
                found.append(str(p.relative_to(root)))
    if found:
        raise RuntimeError((pat, found))

if OUT.exists():
    OUT.unlink()
with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(root.rglob("*")):
        if p.is_file():
            z.write(p, (Path(ROOT_NAME) / p.relative_to(root)).as_posix())

print("OUT", OUT)
print("SHA", hashlib.sha256(OUT.read_bytes()).hexdigest())
