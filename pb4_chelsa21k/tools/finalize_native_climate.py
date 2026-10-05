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

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
OLD_SHA = "bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09"
ROOT_NAME = "PB4Studio_v6.6.3_CHELSA21K"
TMP_CLEAN = Path("/tmp/pb4_final_clean")
TMP_TEST = Path("/tmp/pb4_final_test")
FINAL_ZIP = Path("/tmp/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip")
RUN_LOG = Path("/tmp/final_native_climate_run.log")
PATCH_FILE = Path("/tmp/native_climate_final.patch")


def sh(args, cwd=None, env=None, stdout=None):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True, stdout=stdout)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct_old() -> Path:
    sh([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO)
    z = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    got = sha256(z)
    if got != OLD_SHA:
        raise SystemExit(f"old canonical SHA mismatch: {got} != {OLD_SHA}")
    return z


def patch_tree(old_zip: Path) -> Path:
    shutil.rmtree(TMP_CLEAN, ignore_errors=True)
    TMP_CLEAN.mkdir(parents=True)
    with zipfile.ZipFile(old_zip) as z:
        z.extractall(TMP_CLEAN)
    root = TMP_CLEAN / ROOT_NAME
    if not root.is_dir():
        raise SystemExit(f"package root missing: {root}")

    backend = root / "pb4studio" / "biome4_backend.py"
    before = backend.read_text(encoding="utf-8")
    lines = before.splitlines()
    target = "    if variant in {BIOME4_VARIANT_ORIGINAL, BIOME4_VARIANT_MCKENZIE2003}:"
    hits = [i for i, line in enumerate(lines) if line == target]
    if len(hits) != 1:
        raise SystemExit(f"expected one PFT5/PFT6 climate tuning block; found {len(hits)}")

    i = hits[0]
    j = i + 1
    while j < len(lines):
        line = lines[j]
        if line.strip():
            indent = len(line) - len(line.lstrip(" "))
            if indent <= 4:
                break
        j += 1

    removed = "\n".join(lines[i:j])
    if "old5" not in removed or "old6" not in removed:
        raise SystemExit("target block did not contain both PFT5 and PFT6 tuning")

    replacement = [
        "    # PB4 CHELSA21K production policy (2026-10-05):",
        "    # retain native BIOME4 v4.2b2 PFT5/PFT6 climate limits.",
        "    # McKenzie/Jackson finite-depth soil-water/root coupling remains active;",
        "    # climate-sieve tuning is intentionally not applied.",
    ]
    after = "\n".join(lines[:i] + replacement + lines[j:]) + "\n"
    backend.write_text(after, encoding="utf-8")

    if "old5 = " in after or "old6 = " in after:
        raise SystemExit("legacy PFT5/PFT6 tuning assignments remain")
    for token in [
        "BIOME4-SD reference-derived root-depth adapter",
        "pb4_soildepth",
        "rtop_eff",
        "rbot_eff",
    ]:
        if token not in after:
            raise SystemExit(f"required McKenzie/Jackson coupling token missing: {token}")

    climate = (root / "pb4studio" / "climate.py").read_text(encoding="utf-8")
    if "0.51" not in climate:
        raise SystemExit("51% majority classification rule missing")

    version_file = root / "pb4studio" / "__init__.py"
    version_text = version_file.read_text(encoding="utf-8")
    new_version = "6.6.3-CHELSA21K-envicloud-nolapse-nativeclimate"
    updated = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        f"__version__ = '{new_version}'",
        version_text,
        count=1,
    )
    if updated == version_text:
        raise SystemExit("package version string was not updated")
    version_file.write_text(updated, encoding="utf-8")

    note = root / "NATIVE_CLIMATE_FINAL_2026-10-05.md"
    note.write_text(
        """# PB4Studio CHELSA21K native-climate production decision

This package is the 2026-10-05 production revision for Yongneup wetland ecology,
palaeoecology, palaeoclimate, and biogeomorphology modelling.

Production policy:
- CHELSA-TraCE21k/EnviCloud forcing, 21-0 ka BP, 0.1 kyr interval
- BIOME4 v4.2b2 native PFT5/PFT6 climate limits retained
- McKenzie soil-depth/AWC coupling retained
- Jackson-style finite-depth PFT root accessibility retained
- symmetric 51% majority rule for reduced broadleaf/conifer classification retained
- dynamic Pelletier vegetation-geomorphology coupling retained

A full 21-0 ka ablation showed that removing the PFT5/PFT6 climate tuning leaves
Jang et al. (2011) corrected 1% validation unchanged:
static 24/62 = 38.71%, dynamic 55/62 = 88.71%.

The previous tuned-climate package SHA-256 was:
bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09
It remains recoverable from Git history but is no longer the canonical production package.
""",
        encoding="utf-8",
    )

    import difflib
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(True),
            after.splitlines(True),
            fromfile="biome4_backend.py.tunedClimate",
            tofile="biome4_backend.py.nativeClimate",
        )
    )
    PATCH_FILE.write_text(diff, encoding="utf-8")
    return root


def run_full_regression(clean_root: Path):
    import pandas as pd

    shutil.rmtree(TMP_TEST, ignore_errors=True)
    shutil.copytree(TMP_CLEAN, TMP_TEST)
    root = TMP_TEST / ROOT_NAME
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "4")
    with RUN_LOG.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(
            [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            log.write(line)
        rc = p.wait()
        if rc != 0:
            raise SystemExit(f"full 21-0 ka regression failed with exit code {rc}")

    out = root / "outputs_CHELSA21K"
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    summaries = []
    zones = []
    for mode, expected in [("static", 24), ("dynamic", 55)]:
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(
            lambda r: r[target[str(r["record_id"])][1]], axis=1
        )
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        n = len(df)
        c = int(df["correct_1pct"].sum())
        if n != 62 or c != expected:
            raise SystemExit(
                f"{mode} final regression failed: {c}/{n}, expected {expected}/62"
            )
        summaries.append(
            {
                "model": "PB4-McKenzie-nativeClimate-FINAL",
                "mode": mode,
                "n": n,
                "correct_n": c,
                "accuracy_pct": 100 * c / n,
                "threshold_fraction": 0.01,
            }
        )
        for rid, g in df.groupby(df["record_id"].astype(str), sort=False):
            zones.append(
                {
                    "mode": mode,
                    "record_id": rid,
                    "target_class": target[rid][0],
                    "n": len(g),
                    "correct_n": int(g["correct_1pct"].sum()),
                    "accuracy_pct": 100 * float(g["correct_1pct"].mean()),
                    "target_fraction_min": float(g["target_fraction"].min()),
                    "target_fraction_max": float(g["target_fraction"].max()),
                }
            )
        keep = [
            "record_id",
            "model_ka_bp",
            "valid_basin_cell_count",
            "basin_count_conifer",
            "basin_count_broadleaf",
            "basin_count_mixed",
            "basin_count_herbaceous",
            "target_class",
            "target_fraction",
            "correct_1pct",
        ]
        df[keep].to_csv(
            out / f"FINAL_NATIVECLIMATE_{mode}_JANG1PCT_ROWS.csv",
            index=False,
            encoding="utf-8-sig",
        )

    pd.DataFrame(summaries).to_csv(
        out / "FINAL_NATIVECLIMATE_JANG1PCT_SUMMARY.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(zones).to_csv(
        out / "FINAL_NATIVECLIMATE_JANG1PCT_BY_ZONE.csv",
        index=False,
        encoding="utf-8-sig",
    )
    provenance = {
        "execution_status": "new_full_21ka_final_regression",
        "model_version": "6.6.3-CHELSA21K-envicloud-nolapse-nativeclimate",
        "climate": "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "period_ka_bp": "21.0-0.0",
        "interval_kyr": 0.1,
        "retained": [
            "McKenzie AWC",
            "Jackson finite-depth roots",
            "51% majority reduced classification",
            "dynamic Pelletier coupling",
        ],
        "native_restored": ["PFT5 climate limits", "PFT6 climate limits"],
        "validation": "Jang 2011 corrected reduced mapping, n=62, 1% basin presence",
        "expected_and_observed": {"static": "24/62", "dynamic": "55/62"},
    }
    (out / "FINAL_NATIVECLIMATE_PROVENANCE.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(pd.DataFrame(summaries).to_string(index=False))
    print(pd.DataFrame(zones).to_string(index=False))
    return out


def build_zip(clean_root: Path) -> str:
    fixed = (2026, 10, 5, 0, 0, 0)
    with zipfile.ZipFile(
        FINAL_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as z:
        for p in sorted(clean_root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(TMP_CLEAN).as_posix()
            info = zipfile.ZipInfo(rel, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            z.writestr(
                info,
                p.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    return sha256(FINAL_ZIP)


def update_repo(new_sha: str, outputs: Path):
    model_dir = BASE / "model"
    model_dir.mkdir(parents=True, exist_ok=True)
    canonical = model_dir / "PB4Studio_v6.6.3_CHELSA21K.zip"
    alias = model_dir / "PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip"
    shutil.copy2(FINAL_ZIP, canonical)
    shutil.copy2(FINAL_ZIP, alias)
    if sha256(canonical) != new_sha or sha256(alias) != new_sha:
        raise SystemExit("copied model ZIP hash mismatch")

    payload = BASE / "payload"
    payload.mkdir(parents=True, exist_ok=True)
    for p in payload.glob("PB4Studio_v6.6.3_CHELSA21K.zip.b64.part*"):
        p.unlink()
    encoded = base64.b64encode(FINAL_ZIP.read_bytes()).decode("ascii")
    chunk = 120000
    for k, i in enumerate(range(0, len(encoded), chunk), 1):
        (payload / f"PB4Studio_v6.6.3_CHELSA21K.zip.b64.part{k:03d}").write_text(
            encoded[i : i + chunk], encoding="ascii"
        )

    rec = BASE / "reconstruct_pb4.py"
    text = rec.read_text(encoding="utf-8")
    text = text.replace(OLD_SHA, new_sha)
    rec.write_text(text, encoding="utf-8")

    sums = BASE / "SHA256SUMS.txt"
    old = sums.read_text(encoding="utf-8").splitlines()
    keep = [
        x
        for x in old
        if "PB4Studio_v6.6.3_CHELSA21K.zip" not in x
        and "NATIVECLIMATE_FINAL" not in x
    ]
    lines = [
        f"{new_sha}  model/PB4Studio_v6.6.3_CHELSA21K.zip",
        f"{new_sha}  model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip",
    ] + keep
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8")

    dst = BASE / "results" / "native_climate_final_20261005"
    dst.mkdir(parents=True, exist_ok=True)
    for name in [
        "FINAL_NATIVECLIMATE_JANG1PCT_SUMMARY.csv",
        "FINAL_NATIVECLIMATE_JANG1PCT_BY_ZONE.csv",
        "FINAL_NATIVECLIMATE_static_JANG1PCT_ROWS.csv",
        "FINAL_NATIVECLIMATE_dynamic_JANG1PCT_ROWS.csv",
        "FINAL_NATIVECLIMATE_PROVENANCE.json",
    ]:
        shutil.copy2(outputs / name, dst / name)
    shutil.copy2(PATCH_FILE, dst / "NATIVE_CLIMATE_FINAL.patch")
    shutil.copy2(RUN_LOG, dst / "FINAL_NATIVECLIMATE_21KA_RUN.log")

    decision = f"""# PB4 CHELSA21K final production decision — 2026-10-05

## 결정

최종 production 모델은 **PB4-McKenzie-nativeClimate**로 채택한다.

- BIOME4 v4.2b2의 PFT5/PFT6 기후제약을 원본 그대로 유지
- McKenzie 토심별 AWC coupling 유지
- Jackson 계열 PFT별 finite-depth root accessibility 유지
- native mixed biome의 broadleaf/conifer reduced classification은 대칭적 **51% 과반 규칙** 유지
- dynamic Pelletier 식생-지형 coupling 유지

## 근거

동일 CHELSA-TraCE21k/EnviCloud 21-0 ka forcing으로 PFT5/PFT6 기후튜닝만 제거하여 21-0 ka 전체를 새로 실행했다.

Jang et al. (2011) 원문 식생대 reduced mapping, n=62, 유역 1% 출현 기준:

| 모델 | static | dynamic |
|---|---:|---:|
| 이전 tunedClimate | 24/62 = 38.71% | 55/62 = 88.71% |
| 최종 nativeClimate | 24/62 = 38.71% | 55/62 = 88.71% |

따라서 PFT5/PFT6 기후튜닝은 검증 정확도 향상에 필요하지 않았다. 최종 모델에서는 불필요한 기후 niche 조정을 제거한다.

95_03 dynamic의 broadleaf 비율은 31개 시점 모두 1%를 넘으며 범위는 약 1.3423-3.3557%이다.

## 무결성

이 결정 이전 tuned-climate canonical ZIP SHA-256:
`{OLD_SHA}`

최종 native-climate canonical ZIP SHA-256:
`{new_sha}`

과거 tuned-climate 패키지는 Git 이력으로 복구 가능하지만 더 이상 production 기준본이 아니다.
"""
    (dst / "FINAL_MODEL_DECISION_KO.md").write_text(decision, encoding="utf-8")

    readme = BASE / "README.md"
    r = readme.read_text(encoding="utf-8")
    section = f"""

## 2026-10-05 production model: native BIOME4 climate limits

PFT5/PFT6 climate tuning only was removed and the full 21-0 ka CHELSA21K run was repeated. Jang 2011 corrected 1% validation was unchanged: static **24/62 = 38.71%**, dynamic **55/62 = 88.71%**.

The canonical package is now `PB4-McKenzie-nativeClimate`: McKenzie AWC, finite-depth PFT root coupling, the symmetric 51% majority reduced-class rule, and dynamic Pelletier coupling are retained, while PFT5/PFT6 climate limits are the native BIOME4 v4.2b2 limits.

- Final package: `model/PB4Studio_v6.6.3_CHELSA21K.zip`
- Explicit final alias: `model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`
- Final decision/results: `results/native_climate_final_20261005/`
- Canonical SHA-256: `{new_sha}`
"""
    if "## 2026-10-05 production model: native BIOME4 climate limits" not in r:
        r += section
    readme.write_text(r, encoding="utf-8")

    model_doc = BASE / "PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md"
    m = model_doc.read_text(encoding="utf-8")
    section2 = f"""

## 14. 2026-10-05 최종 production 결정: native BIOME4 climate limits

PFT5/PFT6 기후제약 보정만 제거하고 CHELSA21K 21-0 ka 전체를 새로 실행했다. McKenzie AWC, PFT별 finite-depth root accessibility, 51% 과반 reduced-class 규칙, dynamic Pelletier coupling은 그대로 유지했다.

Jang et al. (2011) 원문 식생대, n=62, 유역 1% 기준에서 결과는 이전 tunedClimate와 완전히 동일했다.

- static: **24/62 = 38.71%**
- dynamic: **55/62 = 88.71%**
- dynamic 95_03: **31/31**
- 95_03 broadleaf fraction: 약 **1.3423-3.3557%**

따라서 PFT5/PFT6 기후튜닝은 정확도 향상에 불필요하다고 판정하고 최종 production 모델에서 제거했다. 최종 모델은 **PB4-McKenzie-nativeClimate**이며, BIOME4 v4.2b2의 원래 PFT 기후 niche를 유지하면서 통합 모델에 필요한 토심-AWC-뿌리-지형 coupling만 추가한다.

최종 canonical ZIP SHA-256: `{new_sha}`

상세 자료: `results/native_climate_final_20261005/`
"""
    if "## 14. 2026-10-05 최종 production 결정" not in m:
        m += section2
    model_doc.write_text(m, encoding="utf-8")

    sh([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO)
    reconstructed = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    if sha256(reconstructed) != new_sha:
        raise SystemExit("new payload reconstruction mismatch")
    reconstructed.unlink()


def main():
    old_zip = reconstruct_old()
    clean_root = patch_tree(old_zip)
    outputs = run_full_regression(clean_root)
    new_sha = build_zip(clean_root)
    update_repo(new_sha, outputs)
    print(f"FINAL_SHA256={new_sha}", flush=True)


if __name__ == "__main__":
    main()
