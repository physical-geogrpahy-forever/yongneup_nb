# -*- coding: utf-8 -*-
"""
biome4_backend.py — BIOME4 v4.2b2 Fortran 배치 백엔드.

이 배포판의 과학 실행 경로는 ``original`` 하나만 허용한다. 토심은 Python 측에서
BIOME4 원래 0–0.3 m / 0.3–1.5 m 토양층의 WHC로만 변환되며, NPP·LAI·FVC에
별도의 토심 계수를 곱하지 않는다.

의도적 생태학적 climate-sieve 변경은 두 가지다. PFT5는 산자부 12-3에서
확정한 reference trial 조건(TCM >= -19 °C, GDD5 >= 900)을 사용한다. PFT6 BoNE는
Sitch et al. (2003)의 LPJ PFT bioclimatic limits(TCM -32.5~-2 °C, GDD5>=600,
TWM<=23 °C)를 사용한다. 토심 결과에 맞추기 위한 NPP·LAI·FVC 또는 physiology
튜닝은 없다.

PB4Studio 결합에 필요한 월별 AET와 PFT 진단값을 Python으로 전달하기 위한
출력 대입문 계측은 유지한다. 레거시 variant 코드는 과거 결과 재현용으로 소스에
남아 있을 수 있으나 GUI/runner의 과학 실행 경로에서는 선택할 수 없다.
"""
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

# biome4.f / biome4_batch_wrapper.f90 이 위치한 폴더. GUI/CLI 초기화 시점에
# 반드시 설정해야 한다 (예: 설치 폴더 내 fortran_src/).
FORTRAN_SOURCE_DIR: Optional[Path] = None

BIOME4_VARIANT_MODIFIED = "modified"  # legacy source retained but disabled in this release
BIOME4_VARIANT_ORIGINAL = "original"
BIOME4_VARIANT_MUSO_ROOTZONE = "muso_rootzone"  # legacy source retained but disabled
BIOME4_VARIANT_BGC_HYBRID = "bgc_hybrid"  # legacy source retained but disabled
BIOME4_VARIANT_MCKENZIE2003 = "mckenzie2003"
BIOME4_VARIANTS = {BIOME4_VARIANT_ORIGINAL, BIOME4_VARIANT_MCKENZIE2003}


def normalize_biome4_variant(value: str | None) -> str:
    """Normalize and validate the strict-reference release BIOME4 path."""
    variant = str(value or BIOME4_VARIANT_MCKENZIE2003).strip().lower()
    aliases = {
        "4.2b2": BIOME4_VARIANT_ORIGINAL,
        "original_4.2b2": BIOME4_VARIANT_ORIGINAL,
        "mckenzie": BIOME4_VARIANT_MCKENZIE2003,
        "mckenzie2003": BIOME4_VARIANT_MCKENZIE2003,
        "biome4_sd": BIOME4_VARIANT_MCKENZIE2003,
    }
    variant = aliases.get(variant, variant)
    if variant not in BIOME4_VARIANTS:
        raise ValueError(
            f"BIOME4 variant {value!r} is disabled in hotfix10l strict-reference release. "
            f"Allowed: {sorted(BIOME4_VARIANTS)}."
        )
    return variant


def _variant_nvars(variant: str) -> int:
    v = normalize_biome4_variant(variant)
    if v == BIOME4_VARIANT_ORIGINAL:
        return 50
    if v in {BIOME4_VARIANT_MUSO_ROOTZONE, BIOME4_VARIANT_BGC_HYBRID, BIOME4_VARIANT_MCKENZIE2003}:
        return 51
    return 59


def _variant_source_filename(variant: str) -> str:
    v = normalize_biome4_variant(variant)
    if v in {BIOME4_VARIANT_ORIGINAL, BIOME4_VARIANT_MUSO_ROOTZONE, BIOME4_VARIANT_BGC_HYBRID, BIOME4_VARIANT_MCKENZIE2003}:
        return "biome4_original_4_2b2.f"
    return "biome4.f"


def _variant_wrapper_filename(variant: str) -> str:
    v = normalize_biome4_variant(variant)
    if v == BIOME4_VARIANT_ORIGINAL:
        return "biome4_batch_wrapper_original.f90"
    if v == BIOME4_VARIANT_MUSO_ROOTZONE:
        return "biome4_batch_wrapper_muso_rootzone.f90"
    if v == BIOME4_VARIANT_BGC_HYBRID:
        return "biome4_batch_wrapper_bgc_hybrid.f90"
    if v == BIOME4_VARIANT_MCKENZIE2003:
        return "biome4_batch_wrapper_mckenzie2003.f90"
    return "biome4_batch_wrapper.f90"


def _resolve_fortran_source_dir() -> Path:
    """Return the configured or packaged BIOME4 source directory.

    ``runner.run`` can be used directly without first launching the GUI.  The
    previous implementation only initialized ``FORTRAN_SOURCE_DIR`` in the GUI
    entry point, so a clean CLI/library installation failed on its first
    compilation.  Resolve the ordinary source/package layout here as a safe
    fallback while still honoring an explicit caller override.
    """
    candidates = []
    if FORTRAN_SOURCE_DIR is not None:
        candidates.append(Path(FORTRAN_SOURCE_DIR))

    module_path = Path(__file__).resolve()
    candidates.extend([
        module_path.parents[1] / "fortran_src",  # source tree / PyInstaller data
        module_path.parent / "fortran_src",      # alternative package layout
    ])

    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)
        # Minimal original-core/hybrid builds ship only the BIOME4 4.2b2 source.
        # Legacy/full builds may also carry biome4.f.
        if ((resolved / "biome4_original_4_2b2.f").is_file()
                or (resolved / "biome4.f").is_file()):
            return resolved

    shown = ", ".join(str(p) for p in candidates) or "(후보 없음)"
    raise FileNotFoundError(
        "BIOME4 Fortran 원본 폴더를 찾지 못했습니다. "
        "FORTRAN_SOURCE_DIR를 BIOME4 원본 소스가 있는 폴더로 지정하십시오. "
        f"확인한 후보: {shown}"
    )


def configure_openmp_runtime(num_threads: int | None = None) -> int:
    """Configure OpenMP runtime variables for the Fortran batch backend.

    This only affects the current Python/Jupyter process.  It does not
    permanently edit the Windows PATH or system environment.
    """
    if num_threads is None:
        raw = os.environ.get("BIOME4_OPENMP_THREADS") or os.environ.get("OMP_NUM_THREADS") or "16"
        try:
            num_threads = int(raw)
        except Exception:
            num_threads = 16
    num_threads = max(1, int(num_threads))
    os.environ["OMP_NUM_THREADS"] = str(num_threads)
    os.environ.setdefault("OMP_DYNAMIC", "FALSE")
    # A conservative default; avoids excessive spin-waiting on Windows.
    os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
    return num_threads


_DLL_DIRECTORY_HANDLES = []

BIOME4_FULL_BIOME_NAMES = {
    1: "Tropical evergreen forest",
    2: "Tropical semi-deciduous forest",
    3: "Tropical deciduous forest/woodland",
    4: "Temperate deciduous forest",
    5: "Temperate conifer forest",
    6: "Warm mixed forest",
    7: "Cool mixed forest",
    8: "Cool conifer forest",
    9: "Cold mixed forest",
    10: "Evergreen taiga/montane forest",
    11: "Deciduous taiga/montane forest",
    12: "Tropical savanna",
    13: "Tropical xerophytic shrubland",
    14: "Temperate xerophytic shrubland",
    15: "Temperate sclerophyll woodland",
    16: "Temperate broad-leaved savanna",
    17: "Open conifer woodland",
    18: "Boreal parkland",
    19: "Tropical grassland",
    20: "Temperate grassland",
    21: "Desert",
    22: "Steppe tundra",
    23: "Shrub tundra",
    24: "Dwarf shrub tundra",
    25: "Prostrate shrub tundra",
    26: "Cushion-forbs, lichen and moss",
    27: "Barren",
    28: "Land ice",
}

BIOME4_TO_VALIDATION_CLASS_ID = {
    1: 3, 2: 2, 3: 2, 4: 2,
    5: 4, 6: 7, 7: 7, 8: 4, 9: 7, 10: 4, 11: 4,
    12: 6, 13: 5, 14: 5, 15: 6, 16: 6, 17: 6, 18: 6,
    19: 1, 20: 1, 21: 0, 22: 1, 23: 5, 24: 5, 25: 5, 26: 1,
    27: 0, 28: 0,
}

VALIDATION_CLASS_ID_TO_LABEL = {
    0: "unassigned_or_no_valid_vegetation",
    1: "herbaceous",
    2: "deciduous_broadleaf_forest",
    3: "evergreen_broadleaf_forest",
    4: "conifer_forest",
    5: "shrubland",
    6: "woodland_or_savanna",
    7: "mixed_forest",
}


def _candidate_gfortran_dirs():
    """Return explicit runtime/compiler directories without mutating PATH.

    Windows has a 32767-character environment variable limit. Earlier versions
    prepended DLL folders to PATH on every BIOME4 call, which eventually made
    PATH too long.  This function only collects candidate directories; it does
    not write to os.environ["PATH"].
    """
    dirs = []
    for key in ("GFORTRAN_DIR",):
        val = os.environ.get(key)
        if val:
            dirs.append(Path(val))
    exe = os.environ.get("GFORTRAN_EXE")
    if exe:
        dirs.append(Path(exe).expanduser().resolve().parent)
    for p in [
        Path(r"C:\msys64\ucrt64\bin"),
        Path(r"C:\msys64\mingw64\bin"),
    ]:
        dirs.append(p)
    try:
        gf = shutil.which("gfortran")
        if gf:
            dirs.append(Path(gf).resolve().parent)
    except Exception:
        pass
    out, seen = [], set()
    for d in dirs:
        try:
            dd = Path(d).resolve()
        except Exception:
            continue
        key = str(dd).lower()
        if key in seen:
            continue
        seen.add(key)
        if dd.exists() and dd.is_dir():
            out.append(dd)
    return out


def _find_gfortran_exe() -> str:
    """Find gfortran without relying on repeated PATH mutation."""
    explicit = os.environ.get("GFORTRAN_EXE")
    if explicit:
        p = Path(explicit)
        if p.exists() and p.is_file():
            return str(p.resolve())
    env_dir = os.environ.get("GFORTRAN_DIR")
    if env_dir:
        p = Path(env_dir) / ("gfortran.exe" if os.name == "nt" else "gfortran")
        if p.exists() and p.is_file():
            return str(p.resolve())
    for d in _candidate_gfortran_dirs():
        p = d / ("gfortran.exe" if os.name == "nt" else "gfortran")
        if p.exists() and p.is_file():
            return str(p.resolve())
    gf = shutil.which("gfortran")
    if gf:
        return gf
    raise RuntimeError(
        "gfortran is required for the Fortran batch backend. "
        "Set GFORTRAN_EXE to the full gfortran.exe path or GFORTRAN_DIR to its bin directory."
    )


def _add_runtime_dll_dirs(extra_dirs=None) -> None:
    """Make MSYS2/MinGW runtime DLLs visible without growing PATH.

    Do NOT prepend to PATH here. This function is called every BIOME4 batch run;
    mutating PATH here causes Windows ValueError once PATH exceeds 32767 chars.
    os.add_dll_directory handles DLL lookup on modern Windows/Python.
    """
    dirs = []
    if extra_dirs:
        dirs.extend([Path(d) for d in extra_dirs if d])
    dirs.extend(_candidate_gfortran_dirs())

    seen = set()
    for d in dirs:
        try:
            d = Path(d).resolve()
        except Exception:
            continue
        if not d.exists() or not d.is_dir():
            continue
        key = str(d).lower()
        if key in seen:
            continue
        seen.add(key)
        if os.name == "nt" and hasattr(os, "add_dll_directory"):
            try:
                _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(str(d)))
            except Exception:
                pass



def _dedupe_path_entries(entries):
    """Return existing path entries de-duplicated, preserving order."""
    out = []
    seen = set()
    for entry in entries:
        if entry is None:
            continue
        s = str(entry).strip().strip('"')
        if not s:
            continue
        try:
            # Preserve raw string when resolution fails, but normalize if possible.
            key = str(Path(s).resolve()).lower()
        except Exception:
            key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def _build_subprocess_env_for_gfortran(gfortran_exe: str) -> dict:
    """Build a short, deterministic subprocess environment for gfortran.

    We intentionally do not mutate os.environ['PATH'] in the Python process because
    repeated BIOME4 calls can exceed Windows' 32767-character PATH limit.  However,
    gfortran itself needs the MSYS2/MinGW runtime DLL directory visible when the
    compiler subprocess starts.  Therefore only the subprocess receives a compact
    PATH consisting of:
      1) the directory containing gfortran.exe,
      2) explicit MSYS2 candidate directories,
      3) de-duplicated original PATH entries, truncated before Windows' limit.
    """
    env = os.environ.copy()
    forced = []
    try:
        forced.append(str(Path(gfortran_exe).resolve().parent))
    except Exception:
        pass
    forced.extend(str(d) for d in _candidate_gfortran_dirs())
    original = os.environ.get('PATH', '')
    original_entries = original.split(os.pathsep) if original else []
    entries = _dedupe_path_entries(forced + original_entries)
    # Keep a conservative margin below Windows' environment variable limit.
    max_len = 30000 if os.name == 'nt' else 200000
    kept = []
    current_len = 0
    for e in entries:
        add_len = len(e) + (1 if kept else 0)
        if current_len + add_len > max_len:
            break
        kept.append(e)
        current_len += add_len
    env['PATH'] = os.pathsep.join(kept)
    if os.name == 'nt' and len(env['PATH']) > 32700:
        raise RuntimeError(f"Subprocess PATH still too long for Windows: {len(env['PATH'])} characters")
    return env

def _find_file(filename: str, explicit_path: Optional[str] = None) -> Path:
    candidates = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    module_dir = _resolve_fortran_source_dir()
    candidates.extend([
        module_dir / filename,
        module_dir / "BIOME4-main" / filename,
    ])
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    raise FileNotFoundError(f"Could not find {filename}. Place it beside this module or pass explicit path.")


def _patch_fortran_source(src: Path, dst: Path, biome4_variant: str = BIOME4_VARIANT_ORIGINAL) -> None:
    """Create the compilable batch source without changing ecological equations.

    All variants receive output-only instrumentation required by the Python
    coupling: monthly AET and PFT diagnostics. The climate-sieve patches retain
    the reference-based PFT5 TCM/GDD5 limits and the Sitch-2003 PFT6 BoNE
    limits.  The Yongneup production variant (mckenzie2003) additionally limits
    the native BIOME4 PFT competition set (PFT2--13; PFT1 remains disabled by
    the original BIOME4 v4.2b2 source itself). No soil-depth NPP/LAI/FVC
    multiplier is added.
    """
    variant = normalize_biome4_variant(biome4_variant)
    text = src.read_bytes().decode("latin-1")

    # hotfix10n6: use the reference-trial PFT5 occurrence limits fixed in
    # 산자부 12-3 (TCM >= -19 C, GDD5 >= 900), while retaining the published
    # Sitch et al. PFT6 BoNE limits introduced in hotfix10n5.
    #
    # The obsolete PFT6 warmest-month relaxation is replaced with the published Sitch et al.
    # (2003) BoNE climatic occurrence sieve used by LPJ:
    #   TCM -32.5 <= TCM < -2 C; GDD5 >= 600; TWM <= 23 C.
    # No soil-depth response, PFT override, or palaeovegetation-fitted coefficient.
    # PB4 CHELSA21K production policy (2026-10-05):
    # retain native BIOME4 v4.2b2 PFT5/PFT6 climate limits.
    # McKenzie/Jackson finite-depth soil-water/root coupling remains active;
    # climate-sieve tuning is intentionally not applied.
    # hotfix10n10: restore the native BIOME4 v4.2b2 competition set for the
    # 120 ka production run. The original source already disables PFT1
    # (Tropical Evergreen) with pfts(1)=0; no additional PFTs are force-disabled.
    # Thus PFT2--13 may enter competition whenever their native/reference
    # climate constraints are satisfied. PFT5 and PFT6 retain the explicit
    # reference climate-sieve patches above.

    if variant == BIOME4_VARIANT_MCKENZIE2003:
        # BIOME4-SD reference-derived root-depth adapter.
        # McKenzie et al. (2003): f(z)=exp(-z/Xi), PAWC is profile AWC
        # integrated with this root-density scaling term.
        # BIOME4 v4.2b2: pftpar(pft,6) is the fraction of roots in the top
        # 30 cm and explicitly cites Jackson et al. Jackson et al. (1996):
        # Y(d)=1-beta**d. These exponential forms are analytically equivalent,
        # fixing Xi from native r30 with no fitted/calibrated coefficient:
        # Xi=-0.30/log(1-r30) [m].
        text = text.replace(
            "      real vars_in(50)\n      real output(500)",
            "      real vars_in(51)\n      real output(500)\n"
            "      real pb4_soildepth",
            1,
        )
        text = text.replace(
            "      iopt=nint(vars_in(46))\n",
            "      iopt=nint(vars_in(46))\n"
            "      pb4_soildepth=max(0.0,vars_in(51))\n",
            1,
        )
        text = text.replace(
            "       subroutine findnpp(pfts,pft,optlai,optnpp,wst,dtemp,sun,\n"
            "     >  temp,dprec,dmelt,dpet,dayl,k,pftpar,optdata,dphen,co2,p,tsoil,\n"
            "     >  realout,numofpfts)",
            "       subroutine findnpp(pfts,pft,optlai,optnpp,wst,dtemp,sun,\n"
            "     >  temp,dprec,dmelt,dpet,dayl,k,pftpar,optdata,dphen,co2,p,tsoil,\n"
            "     >  realout,pb4_soildepth,numofpfts)",
            1,
        )
        text = text.replace(
            "       real wst,k(12),pftpar(25,25)\n",
            "       real wst,k(12),pftpar(25,25),pb4_soildepth\n",
            1,
        )
        text = text.replace(
            "     >  dphen,co2,p,tsoil,realout,numofpfts)\n",
            "     >  dphen,co2,p,tsoil,realout,pb4_soildepth,numofpfts)\n",
            1,
        )
        text = text.replace(
            "     > k,pftpar,pft,dayl,dtemp,inv,dphen,co2,p,tsoil,realin)\n",
            "     > k,pftpar,pft,dayl,dtemp,inv,dphen,co2,p,tsoil,realin,\n"
            "     > pb4_soildepth)\n",
        )
        text = text.replace(
            "       subroutine growth(npp,maxlai,annp,sun,temp,dprec,dmelt,\n"
            "     >  dpet,k,pftpar,pft,dayl,dtemp,outv,dphen,co2,p,tsoil,realin)",
            "       subroutine growth(npp,maxlai,annp,sun,temp,dprec,dmelt,\n"
            "     >  dpet,k,pftpar,pft,dayl,dtemp,outv,dphen,co2,p,tsoil,realin,\n"
            "     >  pb4_soildepth)",
            1,
        )
        text = text.replace(
            "       real sun(12),temp(12),root,c4pot\n",
            "       real sun(12),temp(12),root,c4pot\n"
            "       real pb4_soildepth,root0,xi,rd,rtop_eff,rbot_eff\n",
            1,
        )
        root_marker = "       root      = pftpar(pft,6)\n"
        root_patch = '''       root      = pftpar(pft,6)\n\nc      McKenzie2003/Jackson1996 reference-derived finite soil-depth weights.\nc      BIOME4 root is Jackson-et-al. cumulative root fraction in top 0.30 m.\nc      Jackson: Y(d)=1-beta**d. McKenzie: f(z)=exp(-z/Xi).\nc      Xi is fixed analytically: Xi=-0.30/log(1-r30); no calibration.\nc      rd is limited to BIOME4's native 1.5 m hydraulic profile.\n       root0=root\n       rd=min(max(pb4_soildepth,0.0),1.5)\n       if ((root0.gt.0.0).and.(root0.lt.1.0)) then\n        xi=-0.30/log(1.0-root0)\n       else\n        xi=1.0e-6\n       end if\n       if (rd.gt.0.0) then\n        rtop_eff=1.0-exp(-min(rd,0.30)/xi)\n        if (rd.gt.0.30) then\n         rbot_eff=exp(-0.30/xi)-exp(-rd/xi)\n        else\n         rbot_eff=0.0\n        end if\n       else\n        rtop_eff=0.0\n        rbot_eff=0.0\n       end if\n'''
        if root_marker not in text:
            raise RuntimeError("Could not locate BIOME4 PFT root assignment for McKenzie2003 patch.")
        text = text.replace(root_marker, root_patch, 1)
        text = text.replace(
            "     > (dprec,dmelt,dpet,root,k,maxfvc,pft,phentype,wst,\n",
            "     > (dprec,dmelt,dpet,rtop_eff,rbot_eff,k,maxfvc,pft,phentype,wst,\n",
            1,
        )
        text = text.replace(
            "       subroutine hydrology\n"
            "     >  (dprec,dmelt,deq,root,k,maxfvc,pft\n",
            "       subroutine hydrology\n"
            "     >  (dprec,dmelt,deq,rtop_eff,rbot_eff,k,maxfvc,pft\n",
            1,
        )
        text = text.replace(
            "       real w(2),root,fvc,k(12),aet,r1(2),emax\n",
            "       real w(2),rtop_eff,rbot_eff,fvc,k(12),aet,r1(2),emax\n",
            1,
        )
        text = text.replace(
            "       wr =  root*w(1) + (1.-root)*w(2)\n",
            "       wr = rtop_eff*w(1) + rbot_eff*w(2)\n",
            1,
        )
        text = text.replace(
            "        r1(1) =      root  * (w(1)/wr)\n"
            "        r1(2) =  (1.-root) * (w(2)/wr)       \n",
            "        r1(1) = rtop_eff * (w(1)/wr)\n"
            "        r1(2) = rbot_eff * (w(2)/wr)\n",
            1,
        )

    if variant in {BIOME4_VARIANT_MUSO_ROOTZONE, BIOME4_VARIANT_BGC_HYBRID}:
        # Biome-BGCMuSo multilayer_rootDepth() principle, adapted to the
        # native two-layer BIOME4 hydrology.  MuSo limits maximum rooting depth
        # to min(actual soil depth, PFT root-zone maximum) and normalizes an
        # exponential root distribution over the existing root zone. Here the
        # native BIOME4 profile maximum (1.5 m) is retained, and the exponential
        # shape is derived from each BIOME4 PFT's original Jackson-et-al.
        # fraction of roots in the top 30 cm. Therefore the extension exactly
        # recovers original BIOME4 at soil depth >= 1.5 m and adds no fitted
        # palaeovegetation coefficient.
        text = text.replace(
            "      real vars_in(50)\n      real output(500)",
            "      real vars_in(51)\n      real output(500)\n"
            "      real pb4_soildepth",
            1,
        )
        text = text.replace(
            "      iopt=nint(vars_in(46))\n",
            "      iopt=nint(vars_in(46))\n"
            "      pb4_soildepth=max(0.0,vars_in(51))\n",
            1,
        )
        # Pass soil depth through the call stack rather than an OpenMP
        # THREADPRIVATE COMMON block. GCC 16 / MinGW native-TLS can emit
        # `.tls_common` for threadprivate COMMON blocks, which some Windows
        # assembler combinations reject. A normal scalar dummy argument is
        # naturally thread-local in the parallel batch wrapper and avoids TLS.
        text = text.replace(
            "       real meanKlit,meanKsoil\n",
            "       real meanKlit,meanKsoil\n"
            "       real pb4_soildepth,root0,alpha,rd,topterm,botterm\n"
            "       real bottomthick,bottommid\n",
            1,
        )
        text = text.replace(
            "       subroutine findnpp(pfts,pft,optlai,optnpp,wst,dtemp,sun,\n"
            "     >  temp,dprec,dmelt,dpet,dayl,k,pftpar,optdata,dphen,co2,p,tsoil,\n"
            "     >  realout,numofpfts)",
            "       subroutine findnpp(pfts,pft,optlai,optnpp,wst,dtemp,sun,\n"
            "     >  temp,dprec,dmelt,dpet,dayl,k,pftpar,optdata,dphen,co2,p,tsoil,\n"
            "     >  realout,pb4_soildepth,numofpfts)",
            1,
        )
        text = text.replace(
            "       real wst,k(12),pftpar(25,25)\n",
            "       real wst,k(12),pftpar(25,25),pb4_soildepth\n",
            1,
        )
        text = text.replace(
            "     >  dphen,co2,p,tsoil,realout,numofpfts)\n",
            "     >  dphen,co2,p,tsoil,realout,pb4_soildepth,numofpfts)\n",
            1,
        )
        text = text.replace(
            "     > k,pftpar,pft,dayl,dtemp,inv,dphen,co2,p,tsoil,realin)\n",
            "     > k,pftpar,pft,dayl,dtemp,inv,dphen,co2,p,tsoil,realin,\n"
            "     > pb4_soildepth)\n",
        )
        text = text.replace(
            "       subroutine growth(npp,maxlai,annp,sun,temp,dprec,dmelt,\n"
            "     >  dpet,k,pftpar,pft,dayl,dtemp,outv,dphen,co2,p,tsoil,realin)",
            "       subroutine growth(npp,maxlai,annp,sun,temp,dprec,dmelt,\n"
            "     >  dpet,k,pftpar,pft,dayl,dtemp,outv,dphen,co2,p,tsoil,realin,\n"
            "     >  pb4_soildepth)",
            1,
        )
        root_marker = "       root      = pftpar(pft,6)\n"
        root_patch = """       root      = pftpar(pft,6)

c      MuSo-style finite-root-zone adaptation.
c      rd = min(actual soil depth, native BIOME4 1.5 m profile).
c      alpha is derived from the original top-30-cm root fraction so that
c      rd=1.5 m reproduces the original BIOME4 root parameter exactly.
       root0=root
       rd=min(max(pb4_soildepth,0.0),1.5)
       if (rd.le.0.30) then
        root=1.0
       else if (rd.lt.1.5) then
        alpha=-2.0*log(((1.0/root0)-1.0)/4.0)
        bottomthick=rd-0.30
        bottommid=0.30+0.5*bottomthick
        topterm=alpha*(0.30/rd)*exp(-alpha*(0.15/rd))
        botterm=alpha*(bottomthick/rd)*exp(-alpha*(bottommid/rd))
        if ((topterm+botterm).gt.0.0) then
         root=topterm/(topterm+botterm)
        else
         root=root0
        end if
       else
        root=root0
       end if
"""
        if root_marker not in text:
            raise RuntimeError("Could not locate BIOME4 PFT root assignment for MuSo root-zone patch.")
        text = text.replace(root_marker, root_patch, 1)

    if variant == BIOME4_VARIANT_BGC_HYBRID:
        text = text.replace(
            "      real sumagnpp,delag,wtagnpp\n",
            "      real sumagnpp,delag,wtagnpp\n"
            "      real pb4_rootspace(13),pb4_bgclai(13)\n"
            "      real pb4_root0,pb4_alpha,pb4_rd,pb4_den\n"
            "      real bgc_turn,bgc_rleaf,bgc_sleaf,bgc_crstem\n"
            "      real bgc_sla,bgc_leafalloc,bgc_leafc\n"
            "      real kang_nppfac,kang_laifac\n", 1)
        marker = (
            "c------------------------------------------------------------------------------\n"
            "c      Select dominant plant type/s on the basis of modelled optimal NPP & LAI:\n"
        )
        if marker not in text:
            raise RuntimeError("Could not locate BIOME4 competition marker for BGC hybrid patch.")
        bgc_block = """c------------------------------------------------------------------------------
c      PB4 hotfix10c: hotfix10b rollback + Kang-guided ENF depth response.
c      Non-ENF PFTs keep hotfix10b retained-root-space support.
c      ENF PFT5/6 replace the generic root-volume penalty with an independent
c      depth response derived from the PB4 MuSo7 ENF adapter using the official
c      BIOME-BGC ENF parameterization, motivated by Kang et al. (2016).
c      Anchor GPP retention: 0.05-0.10m .857; 0.20m .987; 0.50m .997; >=1m 1.0.
c      Anchor LAI retention: 0.05-0.10m .802; 0.20m .978; 0.50m .995; >=1m 1.0.
c      Piecewise-linear interpolation only; no pollen-validation fitting.
       do pft=1,numofpfts
        pb4_root0=pftpar(pft,6)
        pb4_rd=min(max(pb4_soildepth,0.0),1.5)
        if (pb4_rd.le.0.0) then
         pb4_rootspace(pft)=0.0
        else if (pb4_rd.ge.1.5) then
         pb4_rootspace(pft)=1.0
        else
         pb4_alpha=-2.0*log(((1.0/pb4_root0)-1.0)/4.0)
         pb4_den=1.0-exp(-pb4_alpha)
         if (pb4_den.gt.0.0) then
          pb4_rootspace(pft)=(1.0-exp(-pb4_alpha*
     >      (pb4_rd/1.5)))/pb4_den
         else
          pb4_rootspace(pft)=pb4_rd/1.5
         end if
        end if
        pb4_rootspace(pft)=min(max(pb4_rootspace(pft),0.0),1.0)
        kang_nppfac=1.0
        kang_laifac=1.0
        if ((pft.eq.5).or.(pft.eq.6)) then
         if (pb4_rd.le.0.0) then
          kang_nppfac=0.0
          kang_laifac=0.0
         else if (pb4_rd.lt.0.05) then
c         No ENF-adapter result exists below 5 cm.  Interpolate to zero at
c         zero effective soil depth rather than holding a non-zero forest
c         productivity at H -> 0.
          kang_nppfac=(pb4_rd/0.05)*0.857
          kang_laifac=(pb4_rd/0.05)*0.802
         else if (pb4_rd.le.0.10) then
          kang_nppfac=0.857
          kang_laifac=0.802
         else if (pb4_rd.lt.0.20) then
          kang_nppfac=0.857+(pb4_rd-0.10)/0.10*(0.987-0.857)
          kang_laifac=0.802+(pb4_rd-0.10)/0.10*(0.978-0.802)
         else if (pb4_rd.lt.0.50) then
          kang_nppfac=0.987+(pb4_rd-0.20)/0.30*(0.997-0.987)
          kang_laifac=0.978+(pb4_rd-0.20)/0.30*(0.995-0.978)
         else if (pb4_rd.lt.1.00) then
          kang_nppfac=0.997+(pb4_rd-0.50)/0.50*(1.0-0.997)
          kang_laifac=0.995+(pb4_rd-0.50)/0.50*(1.0-0.995)
         else
          kang_nppfac=1.0
          kang_laifac=1.0
         end if
         pb4_rootspace(pft)=kang_nppfac
        end if
        optnpp(pft)=optnpp(pft)*pb4_rootspace(pft)
        if ((pft.eq.5).or.(pft.eq.6)) then
         optlai(pft)=optlai(pft)*kang_laifac
        end if
        pb4_bgclai(pft)=999.0
        if (pft.eq.3) then
c        EBF EPC: turnover=.5, root:leaf=1, stem:leaf=1, croot:stem=.3, SLA=12
         bgc_turn=0.5
         bgc_rleaf=1.0
         bgc_sleaf=1.0
         bgc_crstem=0.3
         bgc_sla=12.0
        else if (pft.eq.4) then
c        DBF EPC: turnover=1, root:leaf=1, stem:leaf=2.2, croot:stem=.23, SLA=30
         bgc_turn=1.0
         bgc_rleaf=1.0
         bgc_sleaf=2.2
         bgc_crstem=0.23
         bgc_sla=30.0
        else if ((pft.eq.5).or.(pft.eq.6)) then
c        ENF EPC: turnover=.25, root:leaf=1, stem:leaf=2.2, croot:stem=.3, SLA=12
         bgc_turn=0.25
         bgc_rleaf=1.0
         bgc_sleaf=2.2
         bgc_crstem=0.3
         bgc_sla=12.0
        else if (pft.eq.8) then
c        C3 EPC: turnover=1, root:leaf=2, no stem/croot, SLA=45
         bgc_turn=1.0
         bgc_rleaf=2.0
         bgc_sleaf=0.0
         bgc_crstem=0.0
         bgc_sla=45.0
        else
         bgc_turn=0.0
         bgc_rleaf=0.0
         bgc_sleaf=0.0
         bgc_crstem=0.0
         bgc_sla=0.0
        end if
        if ((bgc_turn.gt.0.0).and.(optnpp(pft).gt.0.0)) then
         bgc_leafalloc=1.0/(1.0+bgc_rleaf+
     >     bgc_sleaf*(1.0+bgc_crstem))
         bgc_leafc=(optnpp(pft)/1000.0)*bgc_leafalloc/bgc_turn
         pb4_bgclai(pft)=max(0.0,bgc_leafc*bgc_sla)
         optlai(pft)=min(optlai(pft),pb4_bgclai(pft))
        end if
       end do

"""
        text = text.replace(marker, bgc_block + marker, 1)
        call_marker = (
            "       call competition2\n"
            "     > (optnpp,optlai,wetness,tmin,tprec,pfts,optdata,output,diagmode,\n"
            "     >  biome,numofpfts,gdd0,gdd5,tcm,pftpar,soil)\n"
        )
        if call_marker not in text:
            raise RuntimeError("Could not locate competition2 call for BGC diagnostic export.")
        post_call = (
            "\n       do pft=1,numofpfts\n"
            "        output(472+pft)=pb4_rootspace(pft)\n"
            "        output(485+pft)=pb4_bgclai(pft)\n"
            "       end do\n"
        )
        text = text.replace(call_marker, call_marker + post_call, 1)

    # Disable hydro.dat repeated writes. These are diagnostics only and create
    # IO/race-condition overhead when BIOME4 is called many times.
    text = text.replace("       open(37,file='hydro.dat',status='unknown')", "c      open(37,file='hydro.dat',status='unknown')")
    text = text.replace("        write(37,*)month,output(412+month),output(424+month),dom", "c       write(37,*)month,output(412+month),output(424+month),dom")

    # The unmodified 4.2b2 core calculates monthly AET internally but does not
    # expose it. Add output assignments only; the hydrology calculation itself
    # is untouched. Modified PB4-BIOME4 already contains these lines.
    if "outv(460+m)=nint(meanaet(m)*days(m)*100.)" not in text:
        marker = "       outv(184+m)=nint(runoffmo(m))\n"
        if marker not in text:
            raise RuntimeError("Could not locate BIOME4 monthly runoff output block for AET instrumentation.")
        text = text.replace(
            marker,
            marker + "       outv(460+m)=nint(meanaet(m)*days(m)*100.)\n",
            1,
        )

    if "monthly AET total, mm month-1" not in text:
        marker = (
            "       do pos=185,196\n"
            "        output(pos)=optdata(dom,pos)  !monthly runoff\n"
            "       end do\n"
        )
        if marker not in text:
            raise RuntimeError("Could not locate BIOME4 monthly runoff copy block for AET instrumentation.")
        text = text.replace(
            marker,
            marker
            + "\n       do pos=461,472\n"
            + "        output(pos)=real(optdata(dom,pos))/100.0  !monthly AET total, mm month-1\n"
            + "       end do\n",
            1,
        )

    marker = "       output(454)=gdd5                !gdd5\n"
    extra = """

c      Extra diagnostic outputs added by PB4Studio batch instrumentation.
c      These assignments expose existing BIOME4 state; they do not alter
c      vegetation, hydrology, competition, or biome classification equations.
c      output(243:255): PFT annual mean soil wetness * 10
c      output(261:273): PFT annual AET, mm yr-1
c      output(275:287): PFT fire days
c      output(288:300): PFT green days
c      output(327:339): PFT constraint pass flag pfts(pft)
c      output(455): wdom; output(456): grasspft; output(457): subpft
       do pft=1,numofpfts
        output(242+pft)=nint(wetness(pft)*10.)
        output(260+pft)=optdata(pft,3)
        output(274+pft)=optdata(pft,199)
        output(287+pft)=optdata(pft,200)
        output(326+pft)=pfts(pft)
       end do
       output(455)=wdom
       output(456)=grasspft
       output(457)=subpft
"""
    if marker in text and "output(326+pft)=pfts(pft)" not in text:
        text = text.replace(marker, marker + extra, 1)
    elif "output(326+pft)=pfts(pft)" not in text:
        raise RuntimeError("Could not locate BIOME4 final diagnostic output block.")

    # Make the selected implementation explicit in the generated source header.
    if variant == BIOME4_VARIANT_ORIGINAL:
        header = "C PB4Studio compile variant: original BIOME4 4.2b2 + output-only instrumentation\n"
    elif variant == BIOME4_VARIANT_MCKENZIE2003:
        header = "C PB4Studio compile variant: BIOME4-SD McKenzie2003 + Jackson1996 root-depth adapter\n"
    elif variant == BIOME4_VARIANT_MUSO_ROOTZONE:
        header = "C PB4Studio compile variant: BIOME4 4.2b2 + MuSo finite root-zone\n"
    elif variant == BIOME4_VARIANT_BGC_HYBRID:
        header = "C PB4Studio compile variant: BIOME4 4.2b2 + reduced-order Biome-BGC hybrid\n"
    else:
        header = "C PB4Studio compile variant: modified PB4-BIOME4\n"
    dst.write_text(header + text, encoding="latin-1", errors="strict")


def _write_batch_wrapper(dst: Path, biome4_variant: str = BIOME4_VARIANT_ORIGINAL) -> None:
    variant = normalize_biome4_variant(biome4_variant)
    src = _resolve_fortran_source_dir() / _variant_wrapper_filename(variant)
    if src.exists():
        dst.write_bytes(src.read_bytes())
        return
    nvars = _variant_nvars(variant)
    dst.write_text(
        f"""subroutine biome4_batch(ncell, vars_in_all, output_all) bind(C, name="biome4_batch")
  use, intrinsic :: iso_c_binding, only: c_int, c_float
  implicit none
  integer(c_int), value :: ncell
  real(c_float), intent(in) :: vars_in_all({nvars}, ncell)
  real(c_float), intent(out) :: output_all(500, ncell)
  integer :: i
  real :: vars_in({nvars})
  real :: output(500)
!$omp parallel do default(none) shared(ncell, vars_in_all, output_all) private(i, vars_in, output) schedule(dynamic, 32)
  do i = 1, ncell
     vars_in(:) = vars_in_all(:, i)
     output(:) = 0.0
     call biome4(vars_in, output)
     output_all(:, i) = output(:)
  end do
!$omp end parallel do
end subroutine biome4_batch
""",
        encoding="utf-8",
    )


def compile_biome4_batch(
    source_path: Optional[str] = None,
    wrapper_path: Optional[str] = None,
    build_dir: Optional[str] = None,
    force: bool = False,
    biome4_variant: str = BIOME4_VARIANT_ORIGINAL,
) -> Path:
    variant = normalize_biome4_variant(biome4_variant)
    source_dir = _resolve_fortran_source_dir()
    src = _find_file(_variant_source_filename(variant), source_path)
    bdir = Path(build_dir or (source_dir / f"_biome4_fortran_batch_build_{variant}"))
    bdir.mkdir(parents=True, exist_ok=True)
    patched = bdir / f"biome4_{variant}_batch_instrumented.f"
    wrapper = bdir / f"biome4_batch_wrapper_{variant}.f90"
    # Use a unique DLL name on forced recompiles. On Windows, an already-loaded
    # DLL is locked by the Python process, so overwriting the same path can fail.
    env_key = f"BIOME4_BATCH_DLL_BASENAME_{variant.upper()}"
    dll_base = os.environ.get(env_key, f"biome4_batch_pb4_{variant}")
    if force:
        dll_base = f"{dll_base}_{os.getpid()}_{int(time.time())}"
    lib = bdir / ((dll_base + ".dll") if os.name == "nt" else ("lib" + dll_base + ".so"))

    if force or not lib.exists():
        _patch_fortran_source(src, patched, biome4_variant=variant)
        if wrapper_path:
            wrapper.write_bytes(Path(wrapper_path).read_bytes())
        else:
            _write_batch_wrapper(wrapper, biome4_variant=variant)
        _add_runtime_dll_dirs()
        gfortran = _find_gfortran_exe()
        omp_threads = configure_openmp_runtime()
        if os.name == "nt":
            cmd = [gfortran, "-shared", "-O3", "-fopenmp", "-frecursive", "-std=legacy", str(patched), str(wrapper), "-o", str(lib)]
        else:
            cmd = [gfortran, "-shared", "-fPIC", "-O3", "-fopenmp", "-frecursive", "-std=legacy", str(patched), str(wrapper), "-o", str(lib)]
        print(f"[BIOME4 {variant} batch compile] OpenMP enabled, OMP_NUM_THREADS={omp_threads}")
        log_path = bdir / f"compile_biome4_batch_{variant}.log"
        env = _build_subprocess_env_for_gfortran(gfortran)
        with open(log_path, "w", encoding="utf-8", errors="replace") as log:
            log.write("VARIANT: " + variant + "\n")
            log.write("COMMAND: " + " ".join(str(x) for x in cmd) + "\n")
            log.write("GFORTRAN: " + str(gfortran) + "\n")
            log.write("BUILD_DIR: " + str(bdir) + "\n")
            log.write("SUBPROCESS_PATH_LENGTH: " + str(len(env.get("PATH", ""))) + "\n")
            log.write("SUBPROCESS_PATH_HEAD: " + env.get("PATH", "")[:2000] + "\n")
            log.write("\n--- compiler output ---\n")
            log.flush()
            proc = subprocess.run(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                cwd=str(bdir),
            )
        if proc.returncode != 0 or not lib.exists():
            tail = log_path.read_text(errors="replace").splitlines()[-160:]
            raise RuntimeError("gfortran batch compilation failed:\n" + "\n".join(tail))
    return lib


class Biome4FortranBatchCore:
    def __init__(self, lib_path: str | Path, nvars: int = 50, biome4_variant: str = BIOME4_VARIANT_ORIGINAL):
        self.variant = normalize_biome4_variant(biome4_variant)
        self.nvars = int(nvars)
        self.openmp_threads = configure_openmp_runtime()
        self.lib_path = Path(lib_path).resolve()
        if not self.lib_path.exists():
            raise FileNotFoundError(f"Compiled BIOME4 batch DLL not found: {self.lib_path}")
        _add_runtime_dll_dirs([self.lib_path.parent])
        try:
            self.lib = ctypes.CDLL(str(self.lib_path))
        except OSError as exc:
            raise OSError(
                "Failed to load compiled BIOME4 batch DLL. This usually means a dependent "
                "MSYS2/gfortran runtime DLL is not visible to Python. Set GFORTRAN_DIR or add "
                "the folder containing gfortran.exe to PATH.\n"
                f"DLL: {self.lib_path}\nOriginal error: {exc}"
            ) from exc
        self._sub = getattr(self.lib, "biome4_batch")
        self._sub.argtypes = [
            ctypes.c_int,
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags="F_CONTIGUOUS"),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags="F_CONTIGUOUS"),
        ]
        self._sub.restype = None

    def run_vars(self, vars_in_all: np.ndarray) -> np.ndarray:
        arr = np.asarray(vars_in_all, dtype=np.float32, order="F")
        if arr.ndim != 2 or arr.shape[0] != self.nvars:
            raise ValueError(
                f"vars_in_all for BIOME4 {self.variant} must have shape "
                f"({self.nvars}, ncell); got {arr.shape}"
            )
        arr = np.asfortranarray(arr, dtype=np.float32)
        ncell = int(arr.shape[1])
        out = np.zeros((500, ncell), dtype=np.float32, order="F")
        self._sub(ctypes.c_int(ncell), arr, out)
        return out


def load_or_compile_batch_core(
    source_path: Optional[str] = None,
    wrapper_path: Optional[str] = None,
    build_dir: Optional[str] = None,
    force: bool = False,
    biome4_variant: str = BIOME4_VARIANT_ORIGINAL,
) -> Biome4FortranBatchCore:
    variant = normalize_biome4_variant(biome4_variant)
    lib = compile_biome4_batch(
        source_path=source_path,
        wrapper_path=wrapper_path,
        build_dir=build_dir,
        force=force,
        biome4_variant=variant,
    )
    return Biome4FortranBatchCore(lib, nvars=_variant_nvars(variant), biome4_variant=variant)

def _prepare_sun_percent(light_monthly: np.ndarray, light_input_kind: str = "cloud_percent") -> np.ndarray:
    arr = np.asarray(light_monthly, dtype=np.float64)
    finite = arr[np.isfinite(arr)]
    if finite.size and np.nanmax(finite) <= 1.5:
        arr = arr * 100.0
    kind = str(light_input_kind).lower().strip()
    if kind in {"sun", "sun_percent", "sunshine", "sunshine_percent"}:
        sun = arr
    elif kind in {"cloud", "cloud_percent", "cloudiness", "cloudiness_percent", "cld"}:
        sun = 100.0 - arr
    else:
        raise ValueError(f"Unknown light_input_kind: {light_input_kind!r}")
    return np.clip(sun, 0.0, 100.0)


def build_vars_in_all_from_grid(
    temp_monthly_C,
    prec_monthly_mm,
    light_monthly,
    tmin_C,
    co2_ppm,
    soil_arrays: Dict[str, np.ndarray],
    lat_grid,
    land_mask,
    elevation_m=None,
    lon_grid=None,
    pressure_pa=None,
    light_input_kind="cloud_percent",
    pressure_from_elevation_func=None,
    soil_canopy_params=None,
    biome4_variant: str = BIOME4_VARIANT_ORIGINAL,
) -> Tuple[np.ndarray, np.ndarray, Tuple[int, int]]:
    """Build BIOME4 vars_in_all array from raster inputs.

    Returns
    -------
    vars_in_all : float32 Fortran array, shape (50, ncell) for original or (59, ncell) for modified
    idxs : flat indices of valid cells
    shape : original raster shape
    """
    variant = normalize_biome4_variant(biome4_variant)
    land = np.asarray(land_mask, dtype=bool)
    nrows, ncols = land.shape
    Ntot = nrows * ncols
    finite = land.ravel().copy()
    temp = np.asarray(temp_monthly_C, dtype=np.float64).reshape(12, -1)
    prec = np.asarray(prec_monthly_mm, dtype=np.float64).reshape(12, -1)
    light = np.asarray(light_monthly, dtype=np.float64).reshape(12, -1)
    sun = _prepare_sun_percent(light, light_input_kind)
    tmin = np.asarray(tmin_C, dtype=np.float64).ravel()
    lat = np.asarray(lat_grid, dtype=np.float64).ravel()
    finite &= np.all(np.isfinite(temp), axis=0)
    finite &= np.all(np.isfinite(prec), axis=0)
    finite &= np.all(np.isfinite(sun), axis=0)
    finite &= np.isfinite(tmin) & np.isfinite(lat)
    for key in ["perc_top_mm_hr", "perc_bottom_mm_hr", "whc_top_mm", "whc_bottom_mm"]:
        finite &= np.isfinite(np.asarray(soil_arrays[key], dtype=np.float64).ravel())
    _soil_depth_key = "soil_depth_m" if "soil_depth_m" in soil_arrays else (
        "soil_depth_m_used_for_biome4" if "soil_depth_m_used_for_biome4" in soil_arrays else None
    )
    if _soil_depth_key is None:
        raise KeyError(
            "V23 strict soil-depth coupling requires soil_arrays['soil_depth_m'] "
            "or soil_arrays['soil_depth_m_used_for_biome4']; refusing constant 2 m fallback."
        )
    finite &= np.isfinite(np.asarray(soil_arrays[_soil_depth_key], dtype=np.float64).ravel())
    idxs = np.where(finite)[0]
    ncell = int(idxs.size)
    if ncell == 0:
        raise ValueError("No valid cells for BIOME4 Fortran batch.")

    vars_in = np.zeros((_variant_nvars(variant), ncell), dtype=np.float32, order="F")
    vars_in[0, :] = lat[idxs].astype(np.float32)
    co2_arr = np.asarray(co2_ppm, dtype=np.float64)
    if co2_arr.size == 1:
        vars_in[1, :] = np.float32(float(co2_arr.reshape(-1)[0]))
    else:
        vars_in[1, :] = co2_arr.reshape(-1)[idxs].astype(np.float32)
    if pressure_pa is not None:
        press = np.asarray(pressure_pa, dtype=np.float64).ravel()[idxs]
    elif elevation_m is not None and pressure_from_elevation_func is not None:
        elev = np.asarray(elevation_m, dtype=np.float64).ravel()[idxs]
        press = np.array([pressure_from_elevation_func(float(z) if np.isfinite(z) else 0.0) for z in elev], dtype=np.float64)
    else:
        press = np.full(ncell, 101325.0, dtype=np.float64)
    vars_in[2, :] = press.astype(np.float32)
    vars_in[3, :] = tmin[idxs].astype(np.float32)
    vars_in[4:16, :] = temp[:, idxs].astype(np.float32)
    vars_in[16:28, :] = prec[:, idxs].astype(np.float32)
    vars_in[28:40, :] = sun[:, idxs].astype(np.float32)
    vars_in[40, :] = np.asarray(soil_arrays["perc_top_mm_hr"], dtype=np.float64).ravel()[idxs].astype(np.float32)
    vars_in[41, :] = np.asarray(soil_arrays["perc_bottom_mm_hr"], dtype=np.float64).ravel()[idxs].astype(np.float32)
    vars_in[42, :] = np.maximum(
        np.asarray(soil_arrays["whc_top_mm"], dtype=np.float64).ravel()[idxs], 0.0
    ).astype(np.float32)
    vars_in[43, :] = np.maximum(
        np.asarray(soil_arrays["whc_bottom_mm"], dtype=np.float64).ravel()[idxs], 0.0
    ).astype(np.float32)
    vars_in[45, :] = 0.0
    if lon_grid is not None:
        lon = np.asarray(lon_grid, dtype=np.float64).ravel()[idxs]
    else:
        lon = np.zeros(ncell, dtype=np.float64)
    vars_in[48, :] = lon.astype(np.float32)
    vars_in[49, :] = 1.0

    if variant in {BIOME4_VARIANT_MUSO_ROOTZONE, BIOME4_VARIANT_BGC_HYBRID, BIOME4_VARIANT_MCKENZIE2003}:
        # 51st slot: actual cell soil depth (m); BGC hybrid also uses it for retained root-space.
        # WHC remains in native slots 43-44.
        vars_in[50, :] = np.maximum(
            np.asarray(soil_arrays[_soil_depth_key], dtype=np.float64).ravel()[idxs],
            0.0,
        ).astype(np.float32)

    if variant == BIOME4_VARIANT_MODIFIED:
        # Active PB4 soil-depth canopy response parameters. The original 4.2b2
        # choice stops at vars_in(50) and therefore bypasses these extensions.
        p = soil_canopy_params or {}
        defaults = {
            "tree_fvc_d50": 1.5,
            "herb_fvc_d50": 0.7,
            "fvc_access_shape": 2.0,
            "fvc_access_min": 0.54,
            "tree_lai_d50": 1.6,
            "herb_lai_d50": 0.7,
            "lai_cap_shape": 2.0,
            "lai_cap_min": 0.7,
        }
        names = [
            "tree_fvc_d50", "herb_fvc_d50", "fvc_access_shape", "fvc_access_min",
            "tree_lai_d50", "herb_lai_d50", "lai_cap_shape", "lai_cap_min",
        ]
        for j, name in enumerate(names):
            vars_in[50 + j, :] = np.float32(float(p.get(name, defaults[name])))

        # Cell-specific soil depth is the final active extension slot: Fortran
        # vars_in(59), Python zero-based row 58.
        vars_in[58, :] = np.maximum(
            np.asarray(soil_arrays[_soil_depth_key], dtype=np.float64).ravel()[idxs],
            0.0,
        ).astype(np.float32)

    return vars_in, idxs, (nrows, ncols)

def parse_output_all_to_grid(output_all: np.ndarray, idxs: np.ndarray, shape: Tuple[int, int], soil_arrays=None, pressure_pa_flat=None, biome4_variant: str = BIOME4_VARIANT_ORIGINAL) -> Dict[str, object]:
    """Convert BIOME4 output_all(500,ncell) to VeSLEM-style grid dictionary."""
    variant = normalize_biome4_variant(biome4_variant)
    out = np.asarray(output_all, dtype=np.float64)
    nrows, ncols = shape
    Ntot = nrows * ncols
    ncell = int(len(idxs))

    def arr_float(fill=np.nan):
        return np.full(Ntot, fill, dtype=np.float64)
    def arr_i(fill=0, dtype="int16"):
        return np.full(Ntot, fill, dtype=dtype)

    biome = np.rint(out[0]).astype(np.int16)
    mapped = np.array([BIOME4_TO_VALIDATION_CLASS_ID.get(int(b), 0) for b in biome], dtype=np.int16)
    optpft = np.rint(out[11]).astype(np.int16)
    wdom = np.rint(out[454]).astype(np.int16) if out.shape[0] > 454 else optpft.copy()
    grasspft = np.rint(out[455]).astype(np.int16) if out.shape[0] > 455 else np.zeros(ncell, dtype=np.int16)
    subpft = np.rint(out[456]).astype(np.int16) if out.shape[0] > 456 else np.zeros(ncell, dtype=np.int16)

    d = {}
    d["biome4_full_id_node"] = arr_i(-1); d["biome4_full_id_node"][idxs] = biome
    d["biome4_mapped_validation_class_id_node"] = arr_i(0); d["biome4_mapped_validation_class_id_node"][idxs] = mapped
    d["biome4_original_mixed_forest_node"] = arr_i(0, dtype="int8"); d["biome4_original_mixed_forest_node"][idxs] = np.isin(biome, [6,7,9]).astype(np.int8)
    d["npp_node"] = arr_float(); d["npp_node"][idxs] = out[2]
    d["lai_node"] = arr_float(); d["lai_node"][idxs] = out[1] / 100.0
    d["wetness_node"] = arr_float(); d["wetness_node"][idxs] = out[9] / 10.0
    d["runoff_node"] = arr_float(); d["runoff_node"][idxs] = out[10]
    d["optpft_node"] = arr_i(0); d["optpft_node"][idxs] = optpft
    d["wdom_node"] = arr_i(0); d["wdom_node"][idxs] = wdom
    d["grasspft_node"] = arr_i(0); d["grasspft_node"][idxs] = grasspft
    d["subpft_node"] = arr_i(0); d["subpft_node"][idxs] = subpft
    d["firedays_node"] = arr_float(); d["firedays_node"][idxs] = out[198]
    d["greendays_node"] = arr_float(); d["greendays_node"][idxs] = out[199]
    d["gdd0_node"] = arr_float(); d["gdd0_node"][idxs] = out[452]
    d["gdd5_node"] = arr_float(); d["gdd5_node"][idxs] = out[453]
    d["tcm_node"] = arr_float(); d["tcm_node"][idxs] = out[451]
    # Patched v4 Fortran exposes dominant-PFT monthly AET totals in output(461:472),
    # i.e. Python zero-based out[460:472]. Units: mm month-1.
    for m in range(1, 13):
        key = f"aet_month_{m:02d}_node"
        d[key] = arr_float()
        if out.shape[0] > 459 + m:
            d[key][idxs] = out[459 + m]


    pft_npp = np.zeros((14, ncell), dtype=np.float64)
    pft_lai = np.zeros((14, ncell), dtype=np.float64)
    pft_aet = np.zeros((14, ncell), dtype=np.float64)
    pft_wet = np.zeros((14, ncell), dtype=np.float64)
    pft_fire = np.zeros((14, ncell), dtype=np.float64)
    pft_green = np.zeros((14, ncell), dtype=np.float64)
    pft_pass = np.zeros((14, ncell), dtype=np.int8)

    for p in range(1, 14):
        pft_npp[p] = out[299 + p]
        pft_lai[p] = out[312 + p]
        pft_wet[p] = out[241 + p] / 10.0
        pft_aet[p] = out[259 + p]
        pft_fire[p] = out[273 + p]
        pft_green[p] = out[286 + p]
        pft_pass[p] = np.rint(out[325 + p]).astype(np.int8)

        rootspace_vals = (np.clip(out[471 + p], 0.0, 1.0)
            if variant == BIOME4_VARIANT_BGC_HYBRID else np.ones(ncell, dtype=np.float64))
        raw_npp_vals = np.divide(pft_npp[p], rootspace_vals, out=np.zeros_like(pft_npp[p]), where=rootspace_vals > 1e-12)
        for prefix, vals in [
            ("pft%02d_raw_npp_node" % p, raw_npp_vals),
            ("pft%02d_mod_npp_node" % p, pft_npp[p]),
            ("pft%02d_raw_lai_node" % p, pft_lai[p]),
            ("pft%02d_mod_lai_node" % p, pft_lai[p]),
            ("pft%02d_aet_node" % p, pft_aet[p]),
            ("pft%02d_wetness_node" % p, pft_wet[p]),
            ("pft%02d_firedays_node" % p, pft_fire[p]),
            ("pft%02d_greendays_node" % p, pft_green[p]),
        ]:
            a = arr_float(); a[idxs] = vals; d[prefix] = a.reshape(shape)
        a = arr_i(0, dtype="int8"); a[idxs] = pft_pass[p]; d[f"pft{p:02d}_constraint_pass_node"] = a.reshape(shape)
        if variant == BIOME4_VARIANT_BGC_HYBRID:
            rs = np.clip(out[471 + p], 0.0, 1.0)
            bl = out[484 + p]
            a = arr_float(); a[idxs] = rs; d[f"pft{p:02d}_bgc_rootspace_node"] = a.reshape(shape)
            a = arr_float(); a[idxs] = np.where(bl < 900.0, bl, np.nan); d[f"pft{p:02d}_bgc_lai_cap_node"] = a.reshape(shape)

    # Group diagnostics used by previous VeSLEM export routines.
    conifer = pft_npp[5] + pft_npp[6] + pft_npp[7]
    broadleaf = pft_npp[3] + pft_npp[4]
    dec_broad = pft_npp[4]
    ev_broad = pft_npp[1] + pft_npp[2] + pft_npp[3]
    grass = pft_npp[8] + pft_npp[9] + pft_npp[12] + pft_npp[13]
    tree = pft_npp[1] + pft_npp[2] + pft_npp[3] + pft_npp[4] + pft_npp[5] + pft_npp[6] + pft_npp[7]
    total = tree + grass + pft_npp[10] + pft_npp[11]

    group_map = {
        "conifer_npp_node": conifer,
        "broadleaf_npp_node": broadleaf,
        "deciduous_broadleaf_npp_node": dec_broad,
        "evergreen_broadleaf_npp_node": ev_broad,
        "grass_pft_npp_node": grass,
        "tree_npp_total_node": tree,
        "total_pft_npp_node": total,
        "conifer_tree_share_node": np.divide(conifer, tree, out=np.full_like(conifer, np.nan), where=tree>0),
        "broadleaf_tree_share_node": np.divide(broadleaf, tree, out=np.full_like(broadleaf, np.nan), where=tree>0),
        "grass_total_share_node": np.divide(grass, total, out=np.full_like(grass, np.nan), where=total>0),
    }
    for k, vals in group_map.items():
        a = arr_float(); a[idxs] = vals; d[k] = a.reshape(shape)

    # Dominance diagnostics across PFT NPP.
    pft_stack = pft_npp[1:14, :]
    order = np.argsort(pft_stack, axis=0)
    dom_pft = order[-1, :] + 1
    sec_pft = order[-2, :] + 1
    dom_npp = pft_stack[dom_pft-1, np.arange(ncell)]
    sec_npp = pft_stack[sec_pft-1, np.arange(ncell)]
    for k, vals, dtype in [
        ("dominant_pft_by_npp_node", dom_pft, "int16"),
        ("second_pft_by_npp_node", sec_pft, "int16"),
    ]:
        a = arr_i(0, dtype=dtype); a[idxs] = vals.astype(a.dtype); d[k] = a.reshape(shape)
    for k, vals in [
        ("dominant_pft_npp_node", dom_npp),
        ("second_pft_npp_node", sec_npp),
        ("dominance_margin_npp_node", dom_npp - sec_npp),
    ]:
        a = arr_float(); a[idxs] = vals; d[k] = a.reshape(shape)

    # AET and alpha approximations. Dominant annual AET is taken from PFT-level AET if available.
    dom_aet = np.full(ncell, np.nan, dtype=np.float64)
    for j, p in enumerate(optpft):
        if 1 <= p <= 13:
            dom_aet[j] = pft_aet[p, j]
    d["aet_node"] = arr_float(); d["aet_node"][idxs] = dom_aet
    d["alpha_node"] = arr_float()  # PET is not exposed by original output; keep as NaN here.

    if soil_arrays is not None:
        if "whc_top_mm" in soil_arrays and "whc_bottom_mm" in soil_arrays:
            whc_total = np.asarray(soil_arrays["whc_top_mm"], dtype=np.float64).ravel() + np.asarray(soil_arrays["whc_bottom_mm"], dtype=np.float64).ravel()
            a = arr_float(); a[idxs] = whc_total[idxs]; d["whc_total_dynamic_mm"] = a.reshape(shape)
        _soil_depth_export_key = "soil_depth_m_used_for_biome4" if "soil_depth_m_used_for_biome4" in soil_arrays else (
            "soil_depth_m" if "soil_depth_m" in soil_arrays else None
        )
        if _soil_depth_export_key is not None:
            a = arr_float(); a[idxs] = np.asarray(soil_arrays[_soil_depth_export_key], dtype=np.float64).ravel()[idxs]
            d["soil_depth_m_used_for_biome4"] = a.reshape(shape)
            d["soil_depth_m"] = a.reshape(shape)
            d["soil_depth_backend_source"] = _soil_depth_export_key
    if pressure_pa_flat is not None:
        a = arr_float(); a[idxs] = np.asarray(pressure_pa_flat, dtype=np.float64).ravel()[idxs]; d["pressure_pa_node"] = a.reshape(shape)

    if variant == BIOME4_VARIANT_BGC_HYBRID:
        dom_rs = np.full(ncell, np.nan, dtype=np.float64)
        dom_bl = np.full(ncell, np.nan, dtype=np.float64)
        for j, pft_id in enumerate(optpft):
            if 1 <= pft_id <= 13:
                dom_rs[j] = np.clip(out[471 + pft_id, j], 0.0, 1.0)
                cap = out[484 + pft_id, j]
                if cap < 900.0:
                    dom_bl[j] = cap
        a = arr_float(); a[idxs] = dom_rs; d["bgc_rootspace_node"] = a.reshape(shape)
        a = arr_float(); a[idxs] = dom_bl; d["bgc_lai_cap_node"] = a.reshape(shape)

    # Reshape flat raster arrays.
    for k, v in list(d.items()):
        if isinstance(v, np.ndarray) and v.shape == (Ntot,):
            d[k] = v.reshape(shape)

    d["vegetation_core_mode"] = "biome4_fortran_batch"
    d["biome4_variant"] = variant
    d["biome4_backend"] = f"fortran_batch_{variant}"
    return d


_BATCH_CORES: Dict[Tuple[str, str, str], Biome4FortranBatchCore] = {}


def run_biome4_fortran_batch_grid(
    temp_monthly_C,
    prec_monthly_mm,
    cloud_percent_monthly,
    tmin_C,
    co2_ppm,
    soil_arrays,
    lat_grid,
    land_mask,
    elevation_m=None,
    lon_grid=None,
    light_input_kind="cloud_percent",
    source_path: Optional[str] = None,
    build_dir: Optional[str] = None,
    force_compile: bool = False,
    pressure_from_elevation_func=None,
    openmp_threads: Optional[int] = None,
    soil_canopy_params=None,
    biome4_variant: str = BIOME4_VARIANT_ORIGINAL,
) -> Dict[str, object]:
    """Run the selected BIOME4 core for all valid grid cells via OpenMP."""
    variant = normalize_biome4_variant(biome4_variant)
    if openmp_threads is not None:
        configure_openmp_runtime(int(openmp_threads))
    module_dir = _resolve_fortran_source_dir()
    source_file = Path(source_path or (module_dir / _variant_source_filename(variant))).resolve()
    build_path = Path(build_dir or (module_dir / f"_biome4_fortran_batch_build_{variant}")).resolve()
    cache_key = (variant, str(source_file), str(build_path))
    if cache_key not in _BATCH_CORES or force_compile:
        wrapper_file = module_dir / _variant_wrapper_filename(variant)
        _BATCH_CORES[cache_key] = load_or_compile_batch_core(
            source_path=str(source_file),
            wrapper_path=str(wrapper_file) if wrapper_file.exists() else None,
            build_dir=str(build_path),
            force=force_compile,
            biome4_variant=variant,
        )
    pressure_func = pressure_from_elevation_func
    vars_in, idxs, shape = build_vars_in_all_from_grid(
        temp_monthly_C=temp_monthly_C,
        prec_monthly_mm=prec_monthly_mm,
        light_monthly=cloud_percent_monthly,
        tmin_C=tmin_C,
        co2_ppm=co2_ppm,
        soil_arrays=soil_arrays,
        lat_grid=lat_grid,
        land_mask=land_mask,
        elevation_m=elevation_m,
        lon_grid=lon_grid,
        light_input_kind=light_input_kind,
        pressure_from_elevation_func=pressure_func,
        soil_canopy_params=soil_canopy_params,
        biome4_variant=variant,
    )
    out = _BATCH_CORES[cache_key].run_vars(vars_in)
    return parse_output_all_to_grid(
        out, idxs, shape, soil_arrays=soil_arrays, biome4_variant=variant
    )
