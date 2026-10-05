from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
OUT = BASE / "results" / "pelletier_agb_candidate_20261005"
TMP = Path("/tmp/pb4_agb_audit")
EXPECTED_SHA = "eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    subprocess.run([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO, check=True)
    z = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    got = sha256(z)
    if got != EXPECTED_SHA:
        raise SystemExit(f"canonical SHA mismatch: {got}")

    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    with zipfile.ZipFile(z) as zz:
        zz.extractall(TMP)

    roots = [p for p in TMP.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise SystemExit(f"unexpected roots: {roots}")
    root = roots[0]

    patterns = [
        re.compile(r"agb", re.I),
        re.compile(r"biomass", re.I),
        re.compile(r"0\.010"),
        re.compile(r"s_agb", re.I),
        re.compile(r"eemt", re.I),
    ]
    rows = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".py", ".f", ".f90", ".md", ".txt"}:
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            if any(rx.search(line) for rx in patterns):
                rows.append((p.relative_to(root).as_posix(), i, line))

    OUT.mkdir(parents=True, exist_ok=True)
    report = OUT / "AGB_SOURCE_AUDIT.txt"
    with report.open("w", encoding="utf-8") as f:
        f.write("PB4-McKenzie-nativeClimate AGB source audit\n")
        f.write(f"canonical_sha256={got}\n")
        f.write(f"package_root={root.name}\n\n")
        for path, line_no, line in rows:
            f.write(f"{path}:{line_no}: {line}\n")

    # Focused context windows around AGB hits for safe patch design.
    focused = OUT / "AGB_SOURCE_CONTEXT.md"
    seen = set()
    with focused.open("w", encoding="utf-8") as f:
        f.write("# Current PB4 AGB source context\n\n")
        f.write(f"Canonical SHA-256: `{got}`\n\n")
        for path, line_no, line in rows:
            if not re.search(r"agb|biomass|0\.010|s_agb", line, re.I):
                continue
            key = (path, max(1, line_no - 12))
            if key in seen:
                continue
            seen.add(key)
            p = root / path
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            a = max(1, line_no - 12)
            b = min(len(lines), line_no + 12)
            f.write(f"## `{path}` lines {a}-{b}\n\n```text\n")
            for j in range(a, b + 1):
                f.write(f"{j:5d}: {lines[j-1]}\n")
            f.write("```\n\n")

    print(report.read_text(encoding="utf-8")[:30000])


if __name__ == "__main__":
    main()
