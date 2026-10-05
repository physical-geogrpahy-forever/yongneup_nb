# -*- coding: utf-8 -*-
"""
climate.py — 기후자료 로딩, BIOME4 결합, EEMT/AGB 계산, 스냅샷 출력.

yongneup_dynstat20m 패키지에서 검증된 코드를 그대로 옮겼다. 물리/통계 계산
로직은 손대지 않았고, 아래 두 가지만 새 아키텍처에 맞게 바꿨다:

    1) select_time_slices() 삭제 — 기존에는 cfg.time_slices_ka (없으면 기후
       파일의 전체 ka_bp 목록)를 썼지만, 새 소프트웨어는 사용자가 지정한
       TimeConfig(start_ka, end_ka, interval_kyr)에서 직접 시간 목록을
       만든다 (config.py: TimeConfig.snapshot_times_ka()).
    2) run_biome4_dynamic_step()이 PACKAGE_DIR 전역변수 대신
       biome4_backend.run_biome4_fortran_batch_grid()를 호출하도록 정리.

이 모듈의 함수들은 대부분 "cfg" 인자를 받는데, 이는 기존 YongneupConfig의
동일 필드명을 그대로 기대하는 얕은 호환 계층이다 — runner.py가
config.ScienceConfig로부터 이 속성들을 노출하는 경량 어댑터 객체를 만들어
넘긴다 (내부 로직을 다시 쓰는 대신, 검증된 코드를 그대로 재사용하기 위함).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import rasterio
from rasterio.crs import CRS

from . import biome4_backend
from .pelletier_geomorph import local_slope_and_costheta


# hotfix10n6 — Yongneup/Beyer temperature downscaling fixed in 산자부 12-3.
# The 0.5-degree Beyer panel (128.0–128.5 E, 38.0–38.5 N) has a FABDEM
# land-only mean terrain elevation of 590.4 m. Monthly lapse rates follow the
# Korean seasonal lapse-rate relationship used in the project, evaluated on
# the 15th day of each month (non-leap-year DOY).
YONGNEUP_BEYER_REFERENCE_ELEVATION_M = 590.4
_KOREA_MONTH15_DOY = np.asarray([15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349], dtype="float64")
KOREA_MONTHLY_LAPSE_RATE_C_PER_M = -(
    0.00688 + 0.0015 * np.cos(0.0172 * (_KOREA_MONTH15_DOY - 60.0))
)


def _apply_yongneup_panel590_temperature_downscaling(df: pd.DataFrame) -> pd.DataFrame:
    """Attach the fixed Yongneup/Beyer elevation-downscaling metadata.

    This is a project-specific production rule, not a generic environmental
    lapse fallback. The climate value is interpreted at the independently
    estimated mean terrain elevation of the source 0.5-degree panel (590.4 m),
    then each model cell is corrected month-by-month from its DEM elevation.
    """
    out = df.copy()
    months = pd.to_numeric(out["month"], errors="raise").astype(int).to_numpy()
    if np.any((months < 1) | (months > 12)):
        raise ValueError("Climate month must be in 1..12 for Yongneup monthly lapse correction.")
    out["reference_elevation_m"] = float(YONGNEUP_BEYER_REFERENCE_ELEVATION_M)
    out["lapse_rate_C_per_m"] = KOREA_MONTHLY_LAPSE_RATE_C_PER_M[months - 1]
    return out


def resolve_data_path(p, suffixes: Tuple[str, ...] = ("", ".tif", ".tiff", ".img", ".nc", ".csv")) -> Path:
    """입력 파일 경로를 찾는다. 확장자가 생략된 경우 흔한 확장자를 순서대로 시도한다.

    (원본의 resolve_data_path와 동일한 역할이지만, PACKAGE_DIR 기준 상대경로
    해석은 하지 않는다 — 새 아키텍처에서는 GUI 파일선택 다이얼로그가 항상
    절대경로를 주기 때문이다.)
    """
    base = Path(p)
    candidates = [base]
    if base.suffix == "":
        candidates.extend(Path(str(base) + s) for s in suffixes if s)
    for cand in candidates:
        if cand.exists():
            return cand
    raise FileNotFoundError("입력 자료 파일을 찾을 수 없습니다. 확인한 경로: " + ", ".join(str(c) for c in candidates))


def _find_first_name(names: Iterable[str], candidates: Iterable[str]) -> str | None:
    """Return the first case-insensitive match from candidates in names."""
    lower = {str(n).lower(): str(n) for n in names}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def _convert_time_to_ka_bp(values: np.ndarray, attrs: Dict[str, object] | None = None) -> np.ndarray:
    """Convert a NetCDF time/age coordinate to ka BP without CF-time decoding.

    `LateQuaternary_Environment.nc` uses a non-standard CF time unit such as
    `years since present`.  Xarray therefore must open the file with
    decode_times=False, and this helper converts the raw numeric time coordinate
    to positive ka BP.  Negative years since present, positive years before
    present, and already-ka coordinates are all handled explicitly.
    """
    vals = np.asarray(values, dtype="float64")
    attrs = attrs or {}
    units = str(attrs.get("units", "")).lower()
    name = str(attrs.get("long_name", "")).lower()
    standard_name = str(attrs.get("standard_name", "")).lower()
    label = " ".join([units, name, standard_name])

    # Coordinates already expressed in ka/kyr are treated as ka BP.  Use absolute
    # values so that files storing ages as negative values before present still
    # become positive ka BP.
    if "ka" in label or "kyr" in label:
        return np.abs(vals)

    # Beyer-style files commonly use `years since present`.  These are not CF
    # datetimes and should be interpreted as age offsets, not calendar years.
    if "since present" in units or "before present" in units or "bp" in label:
        return np.abs(vals) / 1000.0

    # Generic year/yr coordinates are interpreted as years BP when their range
    # is clearly Quaternary-scale.  For small ranges, keep the previous behavior
    # and convert years to kyr.
    if "year" in label or "yr" in label:
        return np.abs(vals) / 1000.0

    # If a coordinate extends far beyond 200, it is almost certainly years BP.
    if np.nanmax(np.abs(vals)) > 200.0:
        return np.abs(vals) / 1000.0

    return np.abs(vals)


def _extract_point_da(da, lon_value: float, lat_value: float):
    """Select the nearest lon/lat point from an xarray DataArray when possible."""
    coord_names = list(da.coords)
    dim_names = list(da.dims)
    lat_name = _find_first_name(coord_names + dim_names, ["lat", "latitude", "y"])
    lon_name = _find_first_name(coord_names + dim_names, ["lon", "longitude", "x"])
    out = da
    if lat_name is not None and lat_name in out.dims:
        out = out.sel({lat_name: float(lat_value)}, method="nearest")
    if lon_name is not None and lon_name in out.dims:
        lon_coord = np.asarray(out[lon_name].values, dtype="float64")
        lv = float(lon_value)
        if lon_coord.size and np.nanmax(lon_coord) > 180.0 and lv < 0.0:
            lv = lv % 360.0
        out = out.sel({lon_name: lv}, method="nearest")
    return out.squeeze(drop=True)


def _monthly_rows_from_dataarray(da, value_name: str) -> pd.DataFrame:
    """Convert a point-selected Beyer climate DataArray into ka/month/value rows.

    The original `LateQuaternary_Environment.nc` stores monthly variables as
    `(longitude, latitude, month, time)`.  After nearest lon/lat selection the
    expected remaining dimensions are `(month, time)` or `(time, month)`.  This
    function deliberately follows the older integrated-model logic: identify the
    time axis by name, identify the month axis either by name or by length 12,
    then move axes explicitly.  Xarray CF time decoding is not used because the
    file stores `time` as years since present.
    """
    arr = da.squeeze(drop=True)
    dims = list(arr.dims)
    coord_names = list(arr.coords)
    time_name = _find_first_name(dims + coord_names, ["ka_bp", "age_ka", "age", "time", "year", "years", "years_bp"])
    if time_name is None or time_name not in arr.dims:
        raise ValueError(f"Cannot identify the time/age dimension for {value_name}. dims={arr.dims}, coords={list(arr.coords)}")

    # The Beyer file has a `month` dimension, but some local NetCDF copies keep
    # the dimension while dropping it from coordinate metadata.  Therefore a
    # non-time dimension of length 12 is accepted as the monthly axis.
    month_name = _find_first_name(dims + coord_names, ["month", "months", "mon", "month_number"])
    if month_name not in arr.dims:
        month_name = None
    if month_name is None:
        candidates = [d for d in arr.dims if d != time_name and int(arr.sizes[d]) == 12]
        if candidates:
            month_name = candidates[0]

    tvals = np.asarray(arr[time_name].values, dtype="float64")
    ka_vals = _convert_time_to_ka_bp(tvals, dict(getattr(arr[time_name], "attrs", {})))

    rows = []
    if month_name is not None:
        # Drop any remaining singleton non-time/non-month dimensions.  If a
        # non-singleton extra dimension remains, lon/lat selection failed and the
        # error should be explicit.
        extra_dims = [d for d in arr.dims if d not in (time_name, month_name)]
        for d in extra_dims:
            if int(arr.sizes[d]) != 1:
                raise ValueError(f"Unexpected extra dimension for {value_name}: {arr.dims}, shape={arr.shape}")
        if extra_dims:
            arr = arr.squeeze(dim=extra_dims, drop=True)

        data = np.asarray(arr.transpose(time_name, month_name).values, dtype="float64")
        # Previous integrated-model behavior: the 12 stored monthly slices are
        # interpreted strictly by storage order as January..December.  Do not
        # reinterpret NetCDF month coordinate values here.  Some files expose
        # awkward month coordinate metadata, but the actual variable dimension is
        # already the 12-month BIOME4 sequence.
        if data.shape[1] != 12:
            raise ValueError(f"Monthly variable {value_name} has {data.shape[1]} stored monthly slices, expected 12. dims={arr.dims}, shape={arr.shape}")
        months = list(range(1, 13))
        for ti, ka in enumerate(ka_vals):
            for mi, month in enumerate(months):
                rows.append({"ka_bp": float(ka), "month": int(month), value_name: float(data[ti, mi])})
        out = pd.DataFrame(rows)
        return out.groupby(["ka_bp", "month"], as_index=False)[value_name].mean()

    # Annual variable fallback: repeat the single value for all 12 months.  This
    # is used for min_temperature if it is passed through this function, but the
    # main monthly variables should normally take the branch above.
    data = np.asarray(arr.transpose(time_name).values, dtype="float64").ravel()
    if len(data) != len(ka_vals):
        raise ValueError(f"{value_name} has no month axis and cannot be aligned to time. dims={arr.dims}, shape={arr.shape}")
    for ka, val in zip(ka_vals, data):
        for month in range(1, 13):
            rows.append({"ka_bp": float(ka), "month": month, value_name: float(val)})
    return pd.DataFrame(rows)


def _annual_rows_from_dataarray(da, value_name: str) -> pd.DataFrame:
    """Convert a point-selected annual DataArray into ka/month/value rows by repeating months."""
    arr = da.squeeze(drop=True)
    dims = list(arr.dims)
    time_name = _find_first_name(dims + list(arr.coords), ["ka_bp", "age_ka", "age", "time", "year", "years", "years_bp"])
    if time_name is None or time_name not in arr.dims:
        raise ValueError(f"Cannot identify the time/age dimension for {value_name}. dims={arr.dims}, coords={list(arr.coords)}")
    extra_dims = [d for d in arr.dims if d != time_name]
    for d in extra_dims:
        if int(arr.sizes[d]) != 1:
            raise ValueError(f"Unexpected extra dimension for annual {value_name}: {arr.dims}, shape={arr.shape}")
    if extra_dims:
        arr = arr.squeeze(dim=extra_dims, drop=True)
    tvals = np.asarray(arr[time_name].values, dtype="float64")
    ka_vals = _convert_time_to_ka_bp(tvals, dict(getattr(arr[time_name], "attrs", {})))
    vals = np.asarray(arr.transpose(time_name).values, dtype="float64").ravel()
    rows = []
    for ka, val in zip(ka_vals, vals):
        for month in range(1, 13):
            rows.append({"ka_bp": float(ka), "month": month, value_name: float(val)})
    return pd.DataFrame(rows)

def _normalise_climate_units(df: pd.DataFrame, ds=None, var_names: Dict[str, str] | None = None) -> pd.DataFrame:
    """Put NetCDF climate variables into the units expected by BIOME4."""
    out = df.copy()
    var_names = var_names or {}
    if "temp_C" in out.columns:
        units = ""
        if ds is not None and var_names.get("temp_C") in ds:
            units = str(ds[var_names["temp_C"]].attrs.get("units", "")).lower()
        if "k" == units.strip() or "kelvin" in units or np.nanmedian(out["temp_C"]) > 100.0:
            out["temp_C"] = out["temp_C"] - 273.15
    if "precip_mm" in out.columns:
        units = ""
        if ds is not None and var_names.get("precip_mm") in ds:
            units = str(ds[var_names["precip_mm"]].attrs.get("units", "")).lower()
        # Convert common flux/rate units to monthly totals.  If the file already
        # uses mm/month or mm, the values are left unchanged.
        month_days = out["month"].map({1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}).astype(float)
        if "kg" in units and "s" in units:
            out["precip_mm"] = out["precip_mm"] * 86400.0 * month_days
        elif "mm/day" in units or "mm d" in units or "mm/day" in units.replace(" ", ""):
            out["precip_mm"] = out["precip_mm"] * month_days
        elif units.strip() in ("m", "m/month", "meter", "metre"):
            out["precip_mm"] = out["precip_mm"] * 1000.0
    if "cloud_pct" in out.columns:
        units = ""
        if ds is not None and var_names.get("cloud_pct") in ds:
            units = str(ds[var_names["cloud_pct"]].attrs.get("units", "")).lower()
        if np.nanmax(out["cloud_pct"]) <= 1.5 or "fraction" in units:
            out["cloud_pct"] = out["cloud_pct"] * 100.0
        out["cloud_pct"] = out["cloud_pct"].clip(0.0, 100.0)
    return out


PACKAGED_CO2_PATH = Path(__file__).resolve().parent / "data" / "antarctica2015co2composite-noaa.txt"


def _load_packaged_bereiter2015_co2() -> Tuple[np.ndarray, np.ndarray]:
    """Load the packaged revised Antarctic composite CO2 record.

    Source: Bereiter et al. (2015) revised Antarctic composite as distributed
    by NOAA/NCEI (dataset DOI 10.25921/n8y4-bp27). Gas age is calendar yr BP
    (present=1950). No fitted/calibrated PB4 coefficient is involved.
    """
    if not PACKAGED_CO2_PATH.exists():
        raise FileNotFoundError(
            "Required packaged Bereiter et al. (2015) CO2 forcing is missing: "
            + str(PACKAGED_CO2_PATH)
        )
    ages = []
    vals = []
    for raw in PACKAGED_CO2_PATH.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.lower().startswith("age_gas"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            ages.append(float(parts[0]))
            vals.append(float(parts[1]))
        except ValueError:
            continue
    if len(ages) < 2:
        raise ValueError("Packaged Bereiter et al. (2015) CO2 record contains insufficient numeric rows.")
    x = np.asarray(ages, dtype="float64")
    y = np.asarray(vals, dtype="float64")
    good = np.isfinite(x) & np.isfinite(y)
    x, y = x[good], y[good]
    order = np.argsort(x)
    return x[order], y[order]


def _attach_packaged_bereiter2015_co2(df: pd.DataFrame) -> pd.DataFrame:
    """Attach the internal Bereiter-2015 CO2 forcing by linear interpolation.

    The project methodology specifies this record as a separate atmospheric
    forcing. Therefore it intentionally replaces any stale/fallback co2_ppm
    column in an extracted climate CSV. Ages outside the source record are
    rejected rather than extrapolated.
    """
    out = df.copy()
    x, y = _load_packaged_bereiter2015_co2()
    target_yr = np.asarray(out["ka_bp"], dtype="float64") * 1000.0
    if np.nanmin(target_yr) < np.nanmin(x) or np.nanmax(target_yr) > np.nanmax(x):
        raise ValueError(
            f"Requested climate ages ({np.nanmin(target_yr):.1f}..{np.nanmax(target_yr):.1f} yr BP) "
            f"fall outside packaged CO2 coverage ({np.nanmin(x):.1f}..{np.nanmax(x):.1f} yr BP)."
        )
    out["co2_ppm"] = np.interp(target_yr, x, y)
    out["co2_source"] = "Bereiter2015_NOAA_revised_Antarctic_composite"
    return out


def _load_chelsa21k_aux_cloud() -> pd.DataFrame:
    """Load the packaged Beyer cloud-only auxiliary series for 0--21 ka.

    CHELSA-TraCE21k Centennial v1.0 does not provide cloud cover, while BIOME4
    requires monthly cloudiness/sunshine.  The CHELSA21K distribution therefore
    uses only the embedded Beyer cloud_pct series as an explicitly labelled
    auxiliary light forcing. Temperature and precipitation always come from the
    user-selected CHELSA raw-wide CSV.
    """
    aux_path = (
        Path(__file__).resolve().parent.parent
        / "embedded_inputs" / "yongneup_exact20m" / "AUX_BEYER_CLOUD_0_21KA.csv"
    )
    if not aux_path.exists():
        raise FileNotFoundError(f"CHELSA21K auxiliary cloud file is missing: {aux_path}")
    aux = pd.read_csv(aux_path)
    required = {"ka_bp", "month", "cloud_pct"}
    missing = required - set(aux.columns)
    if missing:
        raise ValueError(f"Auxiliary cloud CSV is missing columns: {sorted(missing)}")
    aux = aux.copy()
    aux["ka_bp"] = pd.to_numeric(aux["ka_bp"], errors="raise").astype(float)
    aux["month"] = pd.to_numeric(aux["month"], errors="raise").astype(int)
    aux["cloud_pct"] = pd.to_numeric(aux["cloud_pct"], errors="raise").astype(float)
    return aux.sort_values(["month", "ka_bp"]).reset_index(drop=True)


def _chelsa21k_cloud_for_rows(ka_bp: np.ndarray, month: np.ndarray) -> np.ndarray:
    aux = _load_chelsa21k_aux_cloud()
    ages = np.asarray(ka_bp, dtype="float64")
    months = np.asarray(month, dtype=int)
    out = np.full(ages.shape, np.nan, dtype="float64")
    for m in range(1, 13):
        mask = months == m
        if not np.any(mask):
            continue
        a = aux.loc[aux["month"] == m].sort_values("ka_bp")
        xa = a["ka_bp"].to_numpy(dtype="float64")
        ya = a["cloud_pct"].to_numpy(dtype="float64")
        if xa.size < 2:
            raise ValueError(f"Auxiliary cloud forcing has too few rows for month {m}.")
        if np.nanmin(ages[mask]) < xa.min() - 1e-9 or np.nanmax(ages[mask]) > xa.max() + 1e-9:
            raise ValueError(
                f"CHELSA21K cloud auxiliary coverage for month {m} is {xa.min():g}..{xa.max():g} ka BP, "
                f"but requested rows extend outside it."
            )
        out[mask] = np.interp(ages[mask], xa, ya)
    if np.any(~np.isfinite(out)):
        raise ValueError("CHELSA21K auxiliary cloud interpolation produced non-finite values.")
    return np.clip(out, 0.0, 100.0)


def _load_chelsa21k_raw_wide_csv(path: Path) -> pd.DataFrame:
    """Convert verified CHELSA-TraCE21k raw-wide CSV to PB4 monthly forcing.

    Required columns are ka_bp plus tasmin_raw_01..12, tasmax_raw_01..12 and
    pr_raw_01..12.  CHELSA temperatures must already be physical kelvin (the new
    EnviCloud representation, roughly 200--350 K); this loader never performs
    deci-kelvin /10 repair.  It performs only the requested K->degC conversion.

    No elevation correction is attached in this CHELSA21K distribution.
    """
    wide = pd.read_csv(path)
    needed = {"ka_bp"}
    for m in range(1, 13):
        needed.update({f"tasmin_raw_{m:02d}", f"tasmax_raw_{m:02d}", f"pr_raw_{m:02d}"})
    missing = needed - set(wide.columns)
    if missing:
        raise ValueError(
            "CHELSA21K raw-wide CSV is missing required columns: " + ", ".join(sorted(missing))
        )

    wide = wide.copy()
    wide["ka_bp"] = pd.to_numeric(wide["ka_bp"], errors="raise").astype(float)
    if wide["ka_bp"].duplicated().any():
        raise ValueError("CHELSA21K raw-wide CSV contains duplicated ka_bp rows.")
    if wide["ka_bp"].min() < -1e-9 or wide["ka_bp"].max() > 21.0 + 1e-9:
        raise ValueError(
            f"CHELSA21K accepts only 0..21 ka BP; file coverage is "
            f"{wide['ka_bp'].min():g}..{wide['ka_bp'].max():g} ka BP."
        )

    rows = []
    for m in range(1, 13):
        mn = pd.to_numeric(wide[f"tasmin_raw_{m:02d}"], errors="raise").to_numpy(dtype="float64")
        mx = pd.to_numeric(wide[f"tasmax_raw_{m:02d}"], errors="raise").to_numpy(dtype="float64")
        pr = pd.to_numeric(wide[f"pr_raw_{m:02d}"], errors="raise").to_numpy(dtype="float64")
        if np.any(~np.isfinite(mn)) or np.any(~np.isfinite(mx)) or np.any(~np.isfinite(pr)):
            raise ValueError(f"CHELSA21K raw-wide month {m:02d} contains non-finite values.")
        if np.nanmedian(mn) < 200.0 or np.nanmedian(mn) > 350.0 or np.nanmedian(mx) < 200.0 or np.nanmedian(mx) > 350.0:
            raise ValueError(
                f"CHELSA21K month {m:02d} temperature is not in physical kelvin range. "
                "This distribution intentionally refuses old deci-kelvin data; re-download from EnviCloud."
            )
        if np.any(mn > mx):
            raise ValueError(f"CHELSA21K month {m:02d} contains tasmin > tasmax.")
        if np.any(pr < 0.0):
            raise ValueError(f"CHELSA21K month {m:02d} contains negative precipitation.")
        temp_c = 0.5 * (mn + mx) - 273.15
        rows.append(pd.DataFrame({
            "ka_bp": wide["ka_bp"].to_numpy(dtype="float64"),
            "month": np.full(len(wide), m, dtype=int),
            "temp_C": temp_c,
            "precip_mm": pr,
        }))

    df = pd.concat(rows, ignore_index=True)
    df["cloud_pct"] = _chelsa21k_cloud_for_rows(
        df["ka_bp"].to_numpy(dtype="float64"), df["month"].to_numpy(dtype=int)
    )

    # BIOME4 documentation permits missing absolute Tmin and states that it is
    # estimated from mean climate.  Reproduce the original BIOME4 regression
    # from biome4.f::climdata: alttmin = 0.006*cold^2 + 1.316*cold - 21.9.
    cold = df.groupby("ka_bp")["temp_C"].transform("min").to_numpy(dtype="float64")
    df["tmin_C"] = 0.006 * cold * cold + 1.316 * cold - 21.9

    # CHELSA is already topographically downscaled.  Keep explicit zero lapse
    # metadata so climate_arrays_for_time cannot apply a DEM elevation change.
    df["reference_elevation_m"] = 0.0
    df["lapse_rate_C_per_m"] = 0.0
    df["tmin_lapse_rate_C_per_m"] = 0.0
    df["climate_source"] = "CHELSA-TraCE21k_EnviCloud_raw_wide"
    df["cloud_source"] = "Beyer_auxiliary_cloud_only"
    df["tmin_source"] = "BIOME4_original_regression_from_coldest_month_mean"

    # Full monthly audit.
    bad = df.groupby("ka_bp")["month"].apply(lambda x: sorted(set(int(v) for v in x)))
    bad = bad[bad.apply(lambda x: x != list(range(1, 13)))]
    if len(bad):
        raise ValueError(f"CHELSA21K requires exactly months 1..12 at every age; bad ages={bad.index.tolist()[:10]}")

    df = _attach_packaged_bereiter2015_co2(df)
    return df.sort_values(["ka_bp", "month"], ascending=[False, True]).reset_index(drop=True)


def load_climate(path: Path, lon_value: float | None = None, lat_value: float | None = None) -> pd.DataFrame:
    """Load CHELSA21K forcing for the dedicated 0--21 ka distribution.

    The supported production input is the verified CHELSA-TraCE21k EnviCloud
    RAW WIDE CSV.  Temperature is automatically converted from kelvin to degC,
    precipitation is passed through numerically as monthly mm equivalent, and
    elevation lapse correction is explicitly disabled.
    """
    path = resolve_data_path(path, suffixes=("", ".csv"))
    if path.suffix.lower() != ".csv":
        raise ValueError("PB4Studio CHELSA21K accepts CSV climate input only.")
    columns = set(pd.read_csv(path, nrows=1).columns)
    if "tasmin_raw_01" in columns and "tasmax_raw_01" in columns and "pr_raw_01" in columns:
        return _load_chelsa21k_raw_wide_csv(path)
    raise ValueError(
        "PB4Studio CHELSA21K requires the CHELSA EnviCloud RAW WIDE CSV "
        "(ka_bp + tasmin_raw_01..12 + tasmax_raw_01..12 + pr_raw_01..12)."
    )


def climate_arrays_for_time(
    cfg: YongneupConfig,
    climate_df: pd.DataFrame,
    ka_bp: float,
    elevation_m: np.ndarray,
    land: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Build gridded monthly climate arrays using linear interpolation in time.

    hotfix10n10 removes the former nearest-time-slice step function.  Monthly
    temperature, precipitation, cloudiness, annual Tmin and the supplied lapse
    metadata are linearly interpolated between the two bracketing Beyer ages.
    Atmospheric CO2 is evaluated directly from the packaged Bereiter et al.
    composite at the requested model age, so the 0.1-kyr coupling step receives
    continuous forcing rather than climate-slice jumps.
    """
    target = float(ka_bp)
    available = np.asarray(sorted(climate_df["ka_bp"].unique()), dtype="float64")
    if available.size == 0:
        raise ValueError("Climate table contains no ka_bp values.")
    if target < float(available[0]) - 1e-9 or target > float(available[-1]) + 1e-9:
        raise ValueError(
            f"Requested age {target:g} ka BP lies outside climate coverage "
            f"{available[0]:g}..{available[-1]:g} ka BP."
        )

    hi_idx = int(np.searchsorted(available, target, side="left"))
    if hi_idx < available.size and abs(float(available[hi_idx]) - target) <= 1e-10:
        lo_age = hi_age = float(available[hi_idx]); w = 0.0
    elif hi_idx == 0:
        lo_age = hi_age = float(available[0]); w = 0.0
    elif hi_idx >= available.size:
        lo_age = hi_age = float(available[-1]); w = 0.0
    else:
        lo_age = float(available[hi_idx - 1])
        hi_age = float(available[hi_idx])
        w = (target - lo_age) / (hi_age - lo_age)

    def _slice(age: float) -> pd.DataFrame:
        sub = climate_df.loc[np.isclose(climate_df["ka_bp"], age)].sort_values("month").copy()
        if len(sub) != 12 or sub["month"].astype(int).tolist() != list(range(1, 13)):
            counts = climate_df.groupby("ka_bp")["month"].nunique().sort_index(ascending=False).head(10).to_dict()
            raise ValueError(
                f"Time slice {age:g} ka BP must have exactly months 1..12; "
                f"got {sub['month'].tolist()}. Monthly counts sample={counts}"
            )
        return sub.reset_index(drop=True)

    a = _slice(lo_age)
    b = _slice(hi_age)

    def _interp_col(name: str, default: float | None = None) -> np.ndarray:
        if name not in a.columns or name not in b.columns:
            if default is None:
                raise ValueError(f"Climate interpolation requires column {name!r}.")
            return np.full(12, float(default), dtype="float64")
        av = pd.to_numeric(a[name], errors="coerce").to_numpy(dtype="float64")
        bv = pd.to_numeric(b[name], errors="coerce").to_numpy(dtype="float64")
        if np.any(~np.isfinite(av)) or np.any(~np.isfinite(bv)):
            raise ValueError(f"Climate interpolation column {name!r} contains non-finite values at {lo_age:g}/{hi_age:g} ka BP.")
        return av if hi_age == lo_age else (1.0 - w) * av + w * bv

    temp_ref = _interp_col("temp_C")
    prec_ref = _interp_col("precip_mm")
    cloud_ref = _interp_col("cloud_pct")
    lapse_series = _interp_col("lapse_rate_C_per_m", 0.0)

    uses_lapse = bool(np.any(np.abs(lapse_series) > 0.0))
    if "reference_elevation_m" in a.columns and "reference_elevation_m" in b.columns:
        ar = pd.to_numeric(a["reference_elevation_m"], errors="coerce").dropna().unique()
        br = pd.to_numeric(b["reference_elevation_m"], errors="coerce").dropna().unique()
        if len(ar) != 1 or len(br) != 1:
            raise ValueError("Each bracketing climate slice must contain one finite reference_elevation_m.")
        ref_elev = float(ar[0]) if hi_age == lo_age else float((1.0 - w) * ar[0] + w * br[0])
    else:
        if uses_lapse:
            raise ValueError("Non-zero lapse_rate_C_per_m requires reference_elevation_m.")
        ref_elev = 0.0

    shape = elevation_m.shape
    temp = np.zeros((12,) + shape, dtype="float32")
    prec = np.zeros((12,) + shape, dtype="float32")
    cloud = np.zeros((12,) + shape, dtype="float32")
    elev_delta = np.where(np.isfinite(elevation_m), elevation_m - ref_elev, 0.0)
    for i in range(12):
        temp[i] = float(temp_ref[i]) + float(lapse_series[i]) * elev_delta
        prec[i] = float(prec_ref[i])
        cloud[i] = float(cloud_ref[i])

    tmin_ref = float(_interp_col("tmin_C")[0])
    if "tmin_lapse_rate_C_per_m" in a.columns and "tmin_lapse_rate_C_per_m" in b.columns:
        atl = pd.to_numeric(a["tmin_lapse_rate_C_per_m"], errors="coerce").dropna().unique()
        btl = pd.to_numeric(b["tmin_lapse_rate_C_per_m"], errors="coerce").dropna().unique()
        if len(atl) != 1 or len(btl) != 1:
            raise ValueError("Each bracketing climate slice must contain one finite tmin_lapse_rate_C_per_m.")
        tmin_lapse = float(atl[0]) if hi_age == lo_age else float((1.0 - w) * atl[0] + w * btl[0])
    else:
        coldest_idx = int(np.argmin(temp_ref))
        tmin_lapse = float(lapse_series[coldest_idx])
    tmin = np.full(shape, tmin_ref, dtype="float32") + tmin_lapse * elev_delta

    # Direct interpolation on the packaged CO2 record avoids a second-order
    # dependence on the spacing of the Beyer climate slices.
    co2_age, co2_val = _load_packaged_bereiter2015_co2()
    target_yr = target * 1000.0
    if target_yr < float(np.min(co2_age)) or target_yr > float(np.max(co2_age)):
        raise ValueError("Requested age lies outside packaged Bereiter-2015 CO2 coverage.")
    co2 = float(np.interp(target_yr, co2_age, co2_val))

    temp = np.where(land[None, :, :], temp, np.nan)
    prec = np.where(land[None, :, :], prec, np.nan)
    cloud = np.where(land[None, :, :], cloud, np.nan)
    tmin = np.where(land, tmin, np.nan)
    return temp, prec, cloud, tmin, co2

def _texture_hydraulic_arrays(cfg: YongneupConfig, texture_class: np.ndarray | None, shape: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Convert three-class texture values to BIOME4 hydraulic parameters."""
    if texture_class is None or not bool(cfg.use_soil_texture_for_hydraulics):
        whc_top_per_m = np.full(shape, float(cfg.whc_mm_per_m_top), dtype="float64")
        whc_bottom_per_m = np.full(shape, float(cfg.whc_mm_per_m_bottom), dtype="float64")
        perc_top = np.full(shape, float(cfg.perc_top_mm_hr), dtype="float64")
        perc_bottom = np.full(shape, float(cfg.perc_bottom_mm_hr), dtype="float64")
        return whc_top_per_m, whc_bottom_per_m, perc_top, perc_bottom

    tex_raw = np.asarray(texture_class, dtype="float64")
    tex = np.full(shape, -9999, dtype="int16")
    tex_finite = np.isfinite(tex_raw)
    tex[tex_finite] = np.rint(tex_raw[tex_finite]).astype("int16")
    whc_map = {
        1: float(cfg.texture1_whc_mm_per_m),
        2: float(cfg.texture2_whc_mm_per_m),
        3: float(cfg.texture3_whc_mm_per_m),
    }
    perc_map = {
        1: float(cfg.texture1_perc_top_mm_hr),
        2: float(cfg.texture2_perc_top_mm_hr),
        3: float(cfg.texture3_perc_top_mm_hr),
    }
    whc_top_per_m = np.full(shape, float(cfg.whc_mm_per_m_top), dtype="float64")
    whc_bottom_per_m = np.full(shape, float(cfg.whc_mm_per_m_bottom), dtype="float64")
    perc_top = np.full(shape, float(cfg.perc_top_mm_hr), dtype="float64")
    for klass, value in whc_map.items():
        whc_top_per_m[tex == klass] = value
        whc_bottom_per_m[tex == klass] = value
    for klass, value in perc_map.items():
        perc_top[tex == klass] = value
    perc_bottom = np.full(shape, float(cfg.texture_bottom_mm_hr), dtype="float64")
    return whc_top_per_m, whc_bottom_per_m, perc_top, perc_bottom


def _mckenzie2003_yongneup_awc_stores(soil_depth_m: np.ndarray, max_depth_m: float = 1.5) -> tuple[np.ndarray, np.ndarray]:
    """Return McKenzie-profile AWC stores for the user-provided Yongneup SoilGrids point.

    McKenzie et al. (2003) define profile available water capacity as the
    difference in volumetric water content between -10 kPa and -1.5 MPa,
    integrated over profile depth. SoilGrids supplies these water contents at
    six standard depth intervals. Values below are the Explore values supplied
    by the user for 128.1236 E, 38.2153 N. No coarse-fragment correction, PTF,
    calibration, or pollen-fit coefficient is applied.

    The returned stores retain BIOME4's native two hydraulic domains: 0-0.30 m
    and 0.30-1.50 m. The 1.50 m cap is therefore a BIOME4 structural limit, not
    a McKenzie parameter.
    """
    h = np.clip(np.asarray(soil_depth_m, dtype="float64"), 0.0, float(max_depth_m))
    # (top m, bottom m, theta_-10 - theta_-1500 in mm per metre)
    profile = (
        (0.00, 0.05, 237.0),
        (0.05, 0.15, 232.0),
        (0.15, 0.30, 218.0),
        (0.30, 0.60, 207.0),
        (0.60, 1.00, 198.0),
        (1.00, 2.00, 179.0),
    )

    def integrate(z0: float, z1: np.ndarray) -> np.ndarray:
        total = np.zeros_like(h, dtype="float64")
        upper = np.minimum(z1, float(max_depth_m))
        for a, b, awc_per_m in profile:
            lo = np.maximum(float(a), z0)
            hi = np.minimum(float(b), upper)
            thickness = np.maximum(hi - lo, 0.0)
            total += thickness * float(awc_per_m)
        return total

    top_end = np.minimum(h, 0.30)
    whc_top = integrate(0.0, top_end)
    whc_bottom = integrate(0.30, h)
    return whc_top, whc_bottom


def build_soil_arrays(cfg: YongneupConfig, soil_depth_m: np.ndarray, land: np.ndarray, texture_class: np.ndarray | None = None) -> Dict[str, np.ndarray]:
    """Convert BDRICM-derived soil depth and texture class to BIOME4 soil inputs.

    In the original variant, soil depth changes only the two BIOME4 WHC stores.
    In the mckenzie2003 variant, Yongneup SoilGrids theta(-10 kPa)-theta(-1500 kPa)
    is integrated over actual profile depth while retaining BIOME4's 0-0.30 m and
    0.30-1.50 m hydraulic domains; root-depth weights are handled in the Fortran
    backend. No direct soil-depth multiplier is applied to NPP, LAI, FVC, or competition.
    """
    # 지형 상태의 토심을 그대로 사용한다. 노출 기반암(h=0)은 호출부에서
    # BIOME4 활성 마스크에서 제외하므로, 여기서 가상의 1 mm 토양을 만들지 않는다.
    h = np.maximum(np.asarray(soil_depth_m, dtype="float64"), 0.0)
    h = np.where(land, h, np.nan)

    if str(getattr(cfg, "biome4_variant", "original")).strip().lower() == "mckenzie2003":
        # The Yongneup SoilGrids point is classified as BIOME4 texture class 2
        # across all valid model cells in the supplied texture raster. Guard
        # against silently applying this site profile to a different texture.
        if texture_class is not None:
            tex = np.asarray(texture_class, dtype="float64")
            vals = np.unique(np.rint(tex[land & np.isfinite(tex)]).astype(int))
            if vals.size and np.any(vals != 2):
                raise ValueError(
                    "McKenzie2003 Yongneup profile is site-specific to the supplied texture-2 domain; "
                    f"found other texture classes: {vals.tolist()}"
                )
        whc_top, whc_bottom = _mckenzie2003_yongneup_awc_stores(
            h, max_depth_m=float(cfg.whc_max_depth_m)
        )
        # Hydraulic conductivity indices remain the native BIOME4 texture
        # values; McKenzie (2003) is used only for available-water storage and
        # root-density scaling, not to invent a new conductivity relation.
        _, _, perc_top, perc_bottom = _texture_hydraulic_arrays(cfg, texture_class, h.shape)
        out = {
            "perc_top_mm_hr": np.where(land, perc_top, np.nan).astype("float32"),
            "perc_bottom_mm_hr": np.where(land, perc_bottom, np.nan).astype("float32"),
            "whc_top_mm": np.where(land, whc_top, np.nan).astype("float32"),
            "whc_bottom_mm": np.where(land, whc_bottom, np.nan).astype("float32"),
            "soil_depth_m": np.where(land, h, np.nan).astype("float32"),
            "awc_method": "McKenzie2003_theta10_minus_theta1500_SoilGrids_Yongneup",
        }
        if texture_class is not None:
            out["soil_texture_class"] = np.where(land, texture_class, np.nan).astype("float32")
        return out

    top_thick = np.minimum(h, float(cfg.whc_top_layer_m))
    bottom_thick = np.minimum(
        np.maximum(h - float(cfg.whc_top_layer_m), 0.0),
        max(float(cfg.whc_max_depth_m) - float(cfg.whc_top_layer_m), 0.0),
    )
    whc_top_per_m, whc_bottom_per_m, perc_top, perc_bottom = _texture_hydraulic_arrays(cfg, texture_class, h.shape)
    whc_top = top_thick * whc_top_per_m
    whc_bottom = bottom_thick * whc_bottom_per_m
    out = {
        "perc_top_mm_hr": np.where(land, perc_top, np.nan).astype("float32"),
        "perc_bottom_mm_hr": np.where(land, perc_bottom, np.nan).astype("float32"),
        "whc_top_mm": np.where(land, whc_top, np.nan).astype("float32"),
        "whc_bottom_mm": np.where(land, whc_bottom, np.nan).astype("float32"),
        "soil_depth_m": np.where(land, h, np.nan).astype("float32"),
    }
    if texture_class is not None:
        out["soil_texture_class"] = np.where(land, texture_class, np.nan).astype("float32")
    return out


def pressure_from_elevation_pa(elevation_m: float) -> float:
    """Approximate atmospheric pressure from elevation for BIOME4."""
    z = max(float(elevation_m), -500.0)
    return 101325.0 * (1.0 - 2.25577e-5 * z) ** 5.25588


def run_biome4_dynamic_step(
    cfg: YongneupConfig,
    temp_monthly_C: np.ndarray,
    prec_monthly_mm: np.ndarray,
    cloud_percent_monthly: np.ndarray,
    tmin_C: np.ndarray,
    co2_ppm: float,
    soil_arrays: Dict[str, np.ndarray],
    lat_grid: np.ndarray,
    lon_grid: np.ndarray,
    elevation_m: np.ndarray,
    land_mask: np.ndarray,
) -> Dict[str, np.ndarray]:
    """Run the selected BIOME4 Fortran backend on every valid land cell."""
    return biome4_backend.run_biome4_fortran_batch_grid(
        temp_monthly_C=temp_monthly_C,
        prec_monthly_mm=prec_monthly_mm,
        cloud_percent_monthly=cloud_percent_monthly,
        tmin_C=tmin_C,
        co2_ppm=co2_ppm,
        soil_arrays=soil_arrays,
        lat_grid=lat_grid,
        land_mask=land_mask,
        elevation_m=elevation_m,
        lon_grid=lon_grid,
        light_input_kind=cfg.light_input_kind,
        force_compile=bool(cfg.force_compile_biome4),
        pressure_from_elevation_func=pressure_from_elevation_pa,
        openmp_threads=int(cfg.biome4_threads_per_resolution),
        biome4_variant=str(cfg.biome4_variant),
    )


def compute_eemt_and_agb(
    cfg: YongneupConfig,
    veg: Dict[str, np.ndarray],
    temp_monthly_C: np.ndarray,
    prec_monthly_mm: np.ndarray,
    land: np.ndarray,
    bare_bedrock: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute EEMT and the AGB proxy that feeds Pelletier kd."""
    land = np.asarray(land, dtype=bool)
    shape = land.shape
    if bare_bedrock is None:
        bare_bedrock = np.zeros(shape, dtype=bool)
    else:
        bare_bedrock = np.asarray(bare_bedrock, dtype=bool) & land
    aet_monthly = np.zeros((12,) + shape, dtype="float64")
    for m in range(1, 13):
        key = f"aet_month_{m:02d}_node"
        if key in veg:
            aet_monthly[m - 1] = np.asarray(veg[key], dtype="float64")
        else:
            annual_aet = np.asarray(veg.get("aet_node", np.zeros(shape)), dtype="float64")
            aet_monthly[m - 1] = annual_aet / 12.0

    # BIOME4를 우회한 노출 기반암 셀에서는 식생 증발산과 생산성을 0으로
    # 둔다. 따라서 EEMT의 물리적 기후항(유효강수)은 유지되지만 생물에너지항은 0이다.
    aet_monthly[:, bare_bedrock] = 0.0

    # Pelletier et al. (2013), Eqs. (1)-(2): Peff = PPT - ET and
    # DeltaT = Tambient - 273 K. Do not impose PB4-specific zero clips.
    peff_mm = np.asarray(prec_monthly_mm, dtype="float64") - aet_monthly
    eppt_mj = np.nansum(np.asarray(temp_monthly_C, dtype="float64") * float(cfg.eemt_cw_j_kg_k) * peff_mm, axis=0) / 1.0e6

    npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
    npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
    npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
    ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6

    # No PB4 1--80 MJ m^-2 yr^-1 clipping.
    eemt = eppt_mj + ebio_mj
    eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)

    # BIOME4 optLAI -> Reich leaf dry biomass + BIOME3/BIOME4 sapwood bridge.
    # Reich et al. (1992): log10(SLA[cm2 g-1]) = 2.44 - 0.43*log10(leaf life-span[months]).
    # Haxeltine & Prentice (1996) Eq. 34: Cs = LAI*Cn.
    # BIOME4 v4.2b2: pftpar(:,7)=expected leaf longevity in months;
    # pftpar(:,10)=presence of sapwood respiration; stemcarbon=0.5 kgC m-2 LAI-1.
    # fC=0.5 converts sapwood carbon to dry biomass.
    optpft = np.asarray(veg.get("optpft_node", np.full(shape, np.nan)), dtype="float64")
    lai = np.asarray(veg.get("lai_node", np.full(shape, np.nan)), dtype="float64")
    pft_round = np.rint(np.where(np.isfinite(optpft), optpft, -999.0)).astype("int16")
    active = land & (~bare_bedrock) & (pft_round != 0)
    valid_pft = active & (pft_round >= 1) & (pft_round <= 13)
    invalid_pft = active & (~valid_pft)
    if np.any(invalid_pft):
        vals, counts = np.unique(pft_round[invalid_pft], return_counts=True)
        detail = {int(v): int(n) for v, n in zip(vals, counts)}
        raise RuntimeError(
            "REICH-LAI-SAPWOOD AGB candidate encountered invalid BIOME4 PFT(s): "
            + repr(detail)
        )
    bad_lai = active & ((~np.isfinite(lai)) | (lai < 0.0))
    if np.any(bad_lai):
        vals, counts = np.unique(pft_round[bad_lai], return_counts=True)
        detail = {int(v): int(n) for v, n in zip(vals, counts)}
        raise RuntimeError(
            "REICH-LAI-SAPWOOD AGB candidate encountered invalid optLAI: "
            + repr(detail)
        )

    L = np.maximum(np.where(np.isfinite(lai), lai, 0.0), 0.0)
    leaf_months = np.array(
        [np.nan, 18.0, 9.0, 18.0, 7.0, 30.0, 24.0, 24.0, 8.0, 10.0, 12.0, 8.0, 8.0, 8.0],
        dtype="float64",
    )
    sapwood_present = np.array(
        [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        dtype="float64",
    )
    leaf_dry_coef = 1.0 / (0.1 * (10.0 ** 2.44))
    agb = np.zeros(shape, dtype="float64")
    for _p in range(1, 14):
        _m = pft_round == _p
        if not np.any(_m):
            continue
        _leaf = leaf_dry_coef * L[_m] * (leaf_months[_p] ** 0.43)
        _sapwood = L[_m] * sapwood_present[_p]
        agb[_m] = _leaf + _sapwood
    agb = np.where(bare_bedrock, 0.0, agb)
    agb = np.where(land & np.isfinite(agb), agb, np.nan)
    return eemt.astype("float32"), agb.astype("float32")


# -----------------------------------------------------------------------------
# Output helpers
# -----------------------------------------------------------------------------

def vegetation_array(
    veg: Dict[str, np.ndarray],
    shape: Tuple[int, int],
    land: np.ndarray | None = None,
    bare_bedrock: np.ndarray | None = None,
) -> np.ndarray:
    """Return the five-class vegetation raster used by maps and validation.

    hotfix10n10 restores all native BIOME4 competition PFTs (PFT2--13), so the
    reduced Yongneup classes are assigned from native biome physiognomy plus
    dominant functional-group diagnostics rather than from the old 4/5/6/8
    subset.  The reduced classes remain:

      0 conifer forest; 1 broadleaf forest; 2 mixed forest;
      3 herbaceous/open vegetation; 4 truly non-vegetated/bare.

    Functional-group interpretation of restored PFTs:
      PFT2/3/4 = broadleaf-tree group;
      PFT5/6/7 = conifer/taiga-tree group (PFT7 is boreal deciduous taiga);
      PFT8/9 = grass; PFT10 = desert woody; PFT11 = tundra shrub;
      PFT12 = cold herbaceous; PFT13 = lichen/forb.

    Native mixed biomes 6/7/9 keep the symmetric 51% dominance rule.  To avoid
    bias merely because one functional group contains more PFTs, the strongest
    potential-NPP member of each woody group is compared, not the sum of all
    group members.  Native Desert (21) is classed as open vegetation when a
    real PFT and positive productivity/LAI are present; only Barren (27), Land
    ice (28), PB4 exposed bedrock, or a genuinely vegetation-free desert cell
    are class 4.
    """
    if land is None:
        land = np.ones(shape, dtype=bool)
    land = np.asarray(land, dtype=bool)
    if bare_bedrock is None:
        bare_bedrock = np.zeros(shape, dtype=bool)
    else:
        bare_bedrock = np.asarray(bare_bedrock, dtype=bool) & land

    out = np.full(shape, np.nan, dtype="float32")
    if "biome4_full_id_node" not in veg:
        return out
    full = np.asarray(veg["biome4_full_id_node"], dtype="float32")
    optpft = np.asarray(veg.get("optpft_node", np.zeros(shape)), dtype="float64")
    npp = np.asarray(veg.get("npp_node", np.full(shape, np.nan)), dtype="float64")
    lai = np.asarray(veg.get("lai_node", np.full(shape, np.nan)), dtype="float64")

    # Closed-forest physiognomies.
    out[np.isin(full, [5, 8, 10, 11]) & land] = 0  # conifer/taiga forest
    out[np.isin(full, [1, 2, 3, 4]) & land] = 1   # broadleaf forest

    # Native mixed forest, generalized to all restored woody PFTs.
    mixed = np.isin(full, [6, 7, 9]) & land
    out[mixed] = 2
    broad_arrays = [veg.get(f"pft{i:02d}_mod_npp_node") for i in (2, 3, 4)]
    conif_arrays = [veg.get(f"pft{i:02d}_mod_npp_node") for i in (5, 6, 7)]
    if all(x is not None for x in broad_arrays + conif_arrays):
        broad = np.maximum.reduce([np.asarray(x, dtype="float64") for x in broad_arrays])
        conifer = np.maximum.reduce([np.asarray(x, dtype="float64") for x in conif_arrays])
        denom = broad + conifer
        con_share = np.divide(conifer, denom, out=np.full(shape, np.nan), where=denom > 0.0)
        brd_share = np.divide(broad, denom, out=np.full(shape, np.nan), where=denom > 0.0)
        out[mixed & np.isfinite(con_share) & (con_share >= 0.51)] = 0
        out[mixed & np.isfinite(brd_share) & (brd_share >= 0.51)] = 1

    # Savanna/woodland, shrub, grass and tundra are reduced to open vegetation.
    out[np.isin(full, [12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26]) & land] = 3

    # BIOME4 Desert may still contain low-productivity desert woody/grass PFTs.
    desert = (full == 21) & land
    desert_vegetated = desert & (optpft > 0) & (
        (np.isfinite(npp) & (npp > 0.0)) | (np.isfinite(lai) & (lai > 0.0))
    )
    out[desert_vegetated] = 3
    out[desert & ~desert_vegetated] = 4

    # Explicit non-vegetated states only.
    out[np.isin(full, [27, 28]) & land] = 4
    out[bare_bedrock] = 4
    return out

def write_geotiff(path: Path, arr: np.ndarray, transform, crs: str, nodata: float = -9999.0) -> None:
    """Write one single-band GeoTIFF."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.asarray(arr, dtype="float32")
    out = np.where(np.isfinite(data), data, nodata).astype("float32")
    with rasterio.open(path, "w", driver="GTiff", height=out.shape[0], width=out.shape[1], count=1, dtype="float32", crs=CRS.from_string(crs), transform=transform, nodata=nodata, compress="deflate") as dst:
        dst.write(out, 1)


def write_cell_csv(path: Path, x: np.ndarray, y: np.ndarray, lon: np.ndarray, lat: np.ndarray, land: np.ndarray, fields: Dict[str, np.ndarray]) -> None:
    """Write land-cell table for one resolution and time slice."""
    path.parent.mkdir(parents=True, exist_ok=True)
    flat_land = land.ravel()
    idx = np.where(flat_land)[0]
    df = pd.DataFrame({
        "row": np.repeat(np.arange(land.shape[0]), land.shape[1]).ravel()[idx],
        "col": np.tile(np.arange(land.shape[1]), land.shape[0]).ravel()[idx],
        "x": x.ravel()[idx],
        "y": y.ravel()[idx],
        "lon": lon.ravel()[idx],
        "lat": lat.ravel()[idx],
    })
    for name, arr in fields.items():
        df[name] = np.asarray(arr).ravel()[idx]
    df.to_csv(path, index=False, encoding="utf-8-sig")


def _numeric_summary(values: np.ndarray, prefix: str) -> Dict[str, float | str]:
    """Return mean, standard deviation, minimum, maximum, and formatted mean±SD.

    The function is used in both per-snapshot summaries and 10 m baseline
    comparison tables.  It deliberately ignores NaN values so that NoData cells
    outside the watershed do not affect the reported statistics.
    """
    vals = np.asarray(values, dtype="float64")
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return {
            f"{prefix}_mean": np.nan,
            f"{prefix}_sd": np.nan,
            f"{prefix}_mean_sd": "",
            f"{prefix}_min": np.nan,
            f"{prefix}_max": np.nan,
        }
    mean = float(np.nanmean(vals))
    sd = float(np.nanstd(vals))
    mn = float(np.nanmin(vals))
    mx = float(np.nanmax(vals))
    return {
        f"{prefix}_mean": mean,
        f"{prefix}_sd": sd,
        f"{prefix}_mean_sd": f"{mean:.4g} ± {sd:.4g}",
        f"{prefix}_min": mn,
        f"{prefix}_max": mx,
    }


def _categorical_summary(values: np.ndarray, prefix: str) -> Dict[str, float | int | str]:
    """Return dominant class, class richness, and class-code range for vegetation."""
    vals = np.asarray(values)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return {
            f"{prefix}_dominant_code": -999,
            f"{prefix}_class_richness": 0,
            f"{prefix}_min_code": np.nan,
            f"{prefix}_max_code": np.nan,
            f"{prefix}_class_counts": "",
        }
    ints = vals.astype(int)
    classes, counts = np.unique(ints, return_counts=True)
    dominant = int(classes[np.argmax(counts)])
    count_text = "; ".join(f"{int(c)}:{int(n)}" for c, n in zip(classes, counts))
    return {
        f"{prefix}_dominant_code": dominant,
        f"{prefix}_class_richness": int(len(classes)),
        f"{prefix}_min_code": int(np.min(classes)),
        f"{prefix}_max_code": int(np.max(classes)),
        f"{prefix}_class_counts": count_text,
    }


def summarize_snapshot(resolution_m: int, ka_bp: float, z: np.ndarray, h: np.ndarray, veg_code: np.ndarray, npp: np.ndarray, eemt: np.ndarray, land: np.ndarray) -> Dict[str, float | int | str]:
    """Build one summary row for Word/CSV report tables.

    For every continuous output variable, the table now reports the mean,
    standard deviation, formatted mean ± SD, minimum, and maximum.  This makes
    the Word tables usable as direct report tables rather than only diagnostics.
    """
    slope, _ = local_slope_and_costheta(z, float(resolution_m), land)
    out: Dict[str, float | int | str] = {
        "resolution_m": int(resolution_m),
        "ka_bp": float(ka_bp),
        "n_cells": int(np.sum(land)),
        "area_m2": float(np.sum(land) * resolution_m * resolution_m),
    }

    # Continuous variables.  Naming keeps the older mean_* columns for backward
    # compatibility and adds sd/min/max/mean_sd columns for final reporting.
    stats_map = {
        "elevation_m": z,
        "soil_depth_m": h,
        "slope": slope,
        "npp": npp,
        "eemt": eemt,
    }
    for name, arr in stats_map.items():
        stats = _numeric_summary(np.asarray(arr)[land], name)
        out[f"mean_{name}"] = stats[f"{name}_mean"]
        out[f"sd_{name}"] = stats[f"{name}_sd"]
        out[f"{name}_mean_sd"] = stats[f"{name}_mean_sd"]
        out[f"min_{name}"] = stats[f"{name}_min"]
        out[f"max_{name}"] = stats[f"{name}_max"]

    # Relief is kept as a direct terrain metric because it is easier to interpret
    # than max_elevation - min_elevation when reading summary tables.
    out["relief_m"] = float(out["max_elevation_m"] - out["min_elevation_m"])

    veg_stats = _categorical_summary(np.asarray(veg_code)[land], "vegetation")
    out["dominant_vegetation_code"] = veg_stats["vegetation_dominant_code"]
    out["vegetation_class_richness"] = veg_stats["vegetation_class_richness"]
    out["vegetation_min_code"] = veg_stats["vegetation_min_code"]
    out["vegetation_max_code"] = veg_stats["vegetation_max_code"]
    out["vegetation_class_counts"] = veg_stats["vegetation_class_counts"]
    veg_land = np.asarray(veg_code, dtype="float32")[land]
    out["vegetation_nonvegetated_cell_count"] = int(np.sum(np.isfinite(veg_land) & (veg_land == 4.0)))
    out["vegetation_unclassified_cell_count"] = int(np.sum(~np.isfinite(veg_land)))
    out["vegetation_unclassified_fraction"] = (
        float(out["vegetation_unclassified_cell_count"]) / float(out["n_cells"])
        if int(out["n_cells"]) > 0 else np.nan
    )
    return out
