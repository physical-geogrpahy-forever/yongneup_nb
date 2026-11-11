from __future__ import annotations

import argparse
import ast
import json
import os
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient


MODEL_SHA256 = "17c755af300aa25369692addaa5ffc1b0c0c66f48d11401bc5ab31795f8e5529"
CLIMATE_LZMA_SHA256 = "5ffd460e963f798399194ae2e478b3bd6393acde23e45b1382ab9bcec8df92fe"
ORIGINAL_BIOME4_SHA256 = "23b5194b7b2ca25439f9a97e4f55c147c78ee9198c5f953ca2fac8c4ce689968"


class StreamingNotebookClient(NotebookClient):
    def process_message(self, msg, cell, cell_index):
        if msg.get("msg_type") == "stream":
            chunk = msg.get("content", {}).get("text", "")
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
        return super().process_message(msg, cell, cell_index)


def source_text(cell) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def insert_after(nb, predicate, source: str, label: str) -> None:
    matches = [
        i for i, cell in enumerate(nb.cells)
        if cell.cell_type == "code" and predicate(source_text(cell))
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one insertion point for {label}; found {matches}"
        )
    nb.cells.insert(matches[0] + 1, nbformat.v4.new_code_cell(source))


def add_process_budget_instrumentation(nb) -> None:
    patch = r'''
# Diagnostic-only process-budget instrumentation.
# This records accepted substep fluxes; it does not alter z, b, h or any process rate.
import inspect
import numpy as np

_adv_source = inspect.getsource(runner._advance_geomorph_interval_adaptive)
_adv_markers = {
    "init": "    accepted = 0\n",
    "accepted": "        z, b, h = z_try, b_try, h_try\n",
    "stats": '        "last_diagnostics": last_diag,\n',
}
for _name, _marker in _adv_markers.items():
    if _adv_source.count(_marker) != 1:
        raise RuntimeError(f"Could not safely instrument geomorph function marker: {_name}")

_adv_source = _adv_source.replace(
    _adv_markers["init"],
    """    hillslope_erosion_depthsum_m = 0.0
    hillslope_deposition_depthsum_m = 0.0
    fluvial_regolith_erosion_depthsum_m = 0.0
    fluvial_bedrock_erosion_depthsum_m = 0.0
    soil_production_depthsum_m = 0.0
    bedrock_weathering_depthsum_m = 0.0
    accepted = 0
""",
    1,
)

_adv_source = _adv_source.replace(
    _adv_markers["accepted"],
    """        z, b, h = z_try, b_try, h_try

        _hill = np.asarray(diag.get("hillslope_dz_m", 0.0), dtype="float64")
        _freg = np.asarray(diag.get("fluvial_regolith_erosion_m", 0.0), dtype="float64")
        _fbed = np.asarray(diag.get("fluvial_bedrock_erosion_m", 0.0), dtype="float64")
        _soilprod = np.asarray(diag.get("soil_production_m", 0.0), dtype="float64")
        _weather = np.asarray(diag.get("bedrock_weathering_m", 0.0), dtype="float64")
        if _hill.shape == active.shape:
            hillslope_erosion_depthsum_m += float(np.sum(np.maximum(-_hill[active], 0.0)))
            hillslope_deposition_depthsum_m += float(np.sum(np.maximum(_hill[active], 0.0)))
        if _freg.shape == active.shape:
            fluvial_regolith_erosion_depthsum_m += float(np.sum(np.maximum(_freg[active], 0.0)))
        if _fbed.shape == active.shape:
            fluvial_bedrock_erosion_depthsum_m += float(np.sum(np.maximum(_fbed[active], 0.0)))
        if _soilprod.shape == active.shape:
            soil_production_depthsum_m += float(np.sum(np.maximum(_soilprod[active], 0.0)))
        if _weather.shape == active.shape:
            bedrock_weathering_depthsum_m += float(np.sum(np.maximum(_weather[active], 0.0)))
""",
    1,
)

_adv_source = _adv_source.replace(
    _adv_markers["stats"],
    """        "hillslope_erosion_volume_m3": hillslope_erosion_depthsum_m * float(dx_m) ** 2,
        "hillslope_deposition_volume_m3": hillslope_deposition_depthsum_m * float(dx_m) ** 2,
        "fluvial_regolith_erosion_volume_m3": fluvial_regolith_erosion_depthsum_m * float(dx_m) ** 2,
        "fluvial_bedrock_erosion_volume_m3": fluvial_bedrock_erosion_depthsum_m * float(dx_m) ** 2,
        "soil_production_volume_m3": soil_production_depthsum_m * float(dx_m) ** 2,
        "bedrock_weathering_volume_m3": bedrock_weathering_depthsum_m * float(dx_m) ** 2,
        "active_land_area_m2": float(np.count_nonzero(np.asarray(land, dtype=bool))) * float(dx_m) ** 2,
        "last_diagnostics": last_diag,
""",
    1,
)
exec(compile(_adv_source, inspect.getsourcefile(runner._advance_geomorph_interval_adaptive), "exec"), runner.__dict__)

_case_source = inspect.getsource(runner.run_single_case)
_case_marker = '            row["geomorph_max_accepted_fluvial_change_m_to_next"] = geomorph_stats["max_accepted_fluvial_change_m"]\n'
if _case_source.count(_case_marker) != 1:
    raise RuntimeError("Could not safely instrument run_single_case process-budget output marker.")

_case_insert = _case_marker + """            _budget_area = max(float(geomorph_stats["active_land_area_m2"]), 1e-12)
            for _budget_name in (
                "hillslope_erosion",
                "hillslope_deposition",
                "fluvial_regolith_erosion",
                "fluvial_bedrock_erosion",
                "soil_production",
                "bedrock_weathering",
            ):
                _budget_volume = float(geomorph_stats[_budget_name + "_volume_m3"])
                row["geomorph_" + _budget_name + "_volume_m3_to_next"] = _budget_volume
                row["geomorph_" + _budget_name + "_mean_depth_mm_to_next"] = (
                    1000.0 * _budget_volume / _budget_area
                )
            row["geomorph_fluvial_total_erosion_volume_m3_to_next"] = (
                float(geomorph_stats["fluvial_regolith_erosion_volume_m3"])
                + float(geomorph_stats["fluvial_bedrock_erosion_volume_m3"])
            )
            row["geomorph_fluvial_total_erosion_mean_depth_mm_to_next"] = (
                1000.0 * row["geomorph_fluvial_total_erosion_volume_m3_to_next"] / _budget_area
            )
"""
_case_source = _case_source.replace(_case_marker, _case_insert, 1)
exec(compile(_case_source, inspect.getsourcefile(runner.run_single_case), "exec"), runner.__dict__)

if "hillslope_erosion_depthsum_m" not in runner._advance_geomorph_interval_adaptive.__code__.co_varnames:
    raise RuntimeError("Geomorphic process-budget instrumentation did not load.")
if "geomorph_hillslope_erosion_volume_m3_to_next" not in runner.run_single_case.__code__.co_consts:
    raise RuntimeError("Process-budget columns were not added to the run output.")
print("Accepted-substep hillslope/fluvial process-budget diagnostics enabled.")
'''
    insert_after(
        nb,
        lambda s: 'from pb4studio import runner' in s and 'runner.run_single_case' in s,
        patch,
        "process-budget instrumentation after model preparation",
    )


def fixed_basin_cell() -> str:
    return r'''
# Fixed common virtual basin used in both notebook runs.
basin_area_widget.value = 0.0936
basin_cellsize_widget.value = 20.0
basin_base_elev_widget.value = 350.0
basin_long_relief_widget.value = 55.0
basin_soil_depth_widget.value = 0.55
basin_seed_widget.value = 12
basin_elongation_widget.value = 1.15
basin_irregularity_widget.value = 0.12
basin_noise_widget.value = 3.0
print("Fixed basin:", {
    "target_area_km2": basin_area_widget.value,
    "cell_size_m": basin_cellsize_widget.value,
    "base_elevation_m": basin_base_elev_widget.value,
    "relief_m": basin_long_relief_widget.value,
    "initial_soil_depth_m": basin_soil_depth_widget.value,
    "seed": basin_seed_widget.value,
    "elongation": basin_elongation_widget.value,
    "irregularity": basin_irregularity_widget.value,
    "microrelief_noise_m": basin_noise_widget.value,
})
'''


def fixed_scenarios_cell() -> str:
    return r'''
# Identical two-scenario configuration in both timestep notebooks.
scenario_count_widget.value = 2
start_ka_widget.value = 120
end_ka_widget.value = 0

for _idx, _name in enumerate(("baseline", "scenario2")):
    _w = scenario_controls[_idx]
    _w["name"].value = _name
    _w["model"].value = "동적"
    _w["koppen"].value = "Dwa"
    _rep_ids = [value for _label, value in _w["representative"].options]
    if "KR_SEOUL" not in _rep_ids:
        raise RuntimeError(f"Dwa representative list does not contain KR_SEOUL: {_rep_ids}")
    _w["representative"].value = "KR_SEOUL"
    _w["initial_soil_depth_multiplier"].value = 1.0
    _w["uplift_m_per_kyr"].value = 0.08
    _w["soil_production_a"].value = 0.037
    _w["hillslope_eemt_c"].value = 0.033
    _w["hillslope_biomass_d"].value = 0.050
    _w["fluvial_erodibility_k0"].value = 0.020

print("Fixed scenarios:")
for _w in scenario_controls[:2]:
    print({
        "name": _w["name"].value,
        "model": _w["model"].value,
        "koppen": _w["koppen"].value,
        "representative_id": _w["representative"].value,
        "soil_depth_multiplier": _w["initial_soil_depth_multiplier"].value,
        "uplift_m_per_kyr": _w["uplift_m_per_kyr"].value,
        "soil_production_a": _w["soil_production_a"].value,
        "hillslope_c": _w["hillslope_eemt_c"].value,
        "hillslope_d": _w["hillslope_biomass_d"].value,
        "fluvial_K0": _w["fluvial_erodibility_k0"].value,
    })
'''


def validation_cell(expected_interval: float) -> str:
    return f'''
# Input identity and timestep contract.
EXPECTED_MODEL_SHA256 = "{MODEL_SHA256}"
EXPECTED_CLIMATE_LZMA_SHA256 = "{CLIMATE_LZMA_SHA256}"
EXPECTED_ORIGINAL_BIOME4_SHA256 = "{ORIGINAL_BIOME4_SHA256}"
EXPECTED_INTERVAL_KYR = {expected_interval!r}

assert checksum == EXPECTED_MODEL_SHA256, (checksum, EXPECTED_MODEL_SHA256)
assert climate_manifest["sha256_lzma"] == EXPECTED_CLIMATE_LZMA_SHA256
assert MODEL_MANIFEST["sha256_zip"] == EXPECTED_MODEL_SHA256
assert climate_places.loc[
    climate_places["representative_id"] == "KR_SEOUL", "koppen_reference_0ka"
].iloc[0] == "Dwa"

import hashlib
_biome4_original_path = MODEL_DIR / "fortran_src" / "biome4_original_4_2b2.f"
_biome4_original_sha = hashlib.sha256(_biome4_original_path.read_bytes()).hexdigest()
assert _biome4_original_sha == EXPECTED_ORIGINAL_BIOME4_SHA256

if "MODEL_INTERVAL_KYR" in globals():
    _actual_interval = float(MODEL_INTERVAL_KYR)
else:
    _actual_interval = 1.0
assert abs(_actual_interval - EXPECTED_INTERVAL_KYR) < 1e-12, (
    _actual_interval, EXPECTED_INTERVAL_KYR
)
print("Verified package SHA-256:", checksum)
print("Verified original BIOME4 Fortran SHA-256:", _biome4_original_sha)
print("Verified Beyer climate archive SHA-256:", climate_manifest["sha256_lzma"])
print("Verified coupling interval (kyr):", _actual_interval)
'''


def post_run_cell(label: str, expected_interval: float) -> str:
    return f'''
# Persist exact run settings, per-scenario runtime and model interval diagnostics.
import json
import time
import pandas as pd

_actual_interval = float(globals().get("MODEL_INTERVAL_KYR", 1.0))
_expected_steps = int(round((float(start_ka) - float(end_ka)) / _actual_interval))
assert len(times) - 1 == _expected_steps, (len(times) - 1, _expected_steps)
assert abs(_actual_interval - {expected_interval!r}) < 1e-12

_runtime_frame = pd.DataFrame(scenario_runtime)
_runtime_frame.to_csv(exp_root / "scenario_runtime.csv", index=False, encoding="utf-8-sig")
_settings_frame = pd.DataFrame(scenario_configs)
_settings_frame.to_csv(exp_root / "scenario_settings_fixed.csv", index=False, encoding="utf-8-sig")

_github_run_metadata = {{
    "run_label": {label!r},
    "start_ka": float(start_ka),
    "end_ka": float(end_ka),
    "interval_kyr": _actual_interval,
    "model_intervals": _expected_steps,
    "snapshot_ages_ka": [float(x) for x in snaps],
    "PB4_threads": int(pb4_threads),
    "model_zip_sha256": checksum,
    "climate_lzma_sha256": climate_manifest["sha256_lzma"],
    "original_biome4_fortran_sha256": _biome4_original_sha,
    "virtual_basin": virtual_basin_config,
    "scenarios": scenario_configs,
    "scenario_runtime": scenario_runtime,
    "notebook_run_elapsed_seconds_including_postprocess": float(time.perf_counter() - overall_start),
    "diagnostic_process_budget_patch": "accepted-substep flux sums only; no state/process equation changes",
}}
(exp_root / "github_run_metadata.json").write_text(
    json.dumps(_github_run_metadata, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Persisted GitHub run metadata:", exp_root / "github_run_metadata.json")
print("Scenario runtimes:")
print(_runtime_frame.to_string(index=False))
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebook", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--interval-kyr", type=float, required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--timeout-seconds", type=int, default=21000)
    args = ap.parse_args()

    notebook_path = Path(args.notebook).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not notebook_path.is_file():
        raise FileNotFoundError(notebook_path)

    os.environ["PB4_THREADS"] = str(max(1, args.threads))
    os.environ["OMP_NUM_THREADS"] = str(max(1, args.threads))
    os.environ["OMP_DYNAMIC"] = "FALSE"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["PYTHONUNBUFFERED"] = "1"

    nb = nbformat.read(notebook_path, as_version=4)
    # nbformat accepts either a string or an array. Normalize arrays without
    # losing the line endings that were restored in the 0.1-kyr source file.
    for cell in nb.cells:
        if isinstance(cell.source, list):
            cell.source = "".join(cell.source)

    # Fail before a long run if any executable cell is syntactically invalid.
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            ast.parse(cell.source, filename=f"{notebook_path.name}:cell_{i}")

    # Validate the model/climate archive immediately after the climate loader.
    insert_after(
        nb,
        lambda s: "climate_places[" in s and "def _coord_label" in s,
        validation_cell(args.interval_kyr),
        "model/climate identity validation",
    )
    # Apply diagnostic-only process budget accounting after the package is loaded.
    add_process_budget_instrumentation(nb)
    # Fix all basin settings after the widgets are defined.
    insert_after(
        nb,
        lambda s: "basin_noise_widget=widgets.FloatSlider" in s and "def _build_virtual_basin" in s,
        fixed_basin_cell(),
        "fixed common virtual basin",
    )
    # Fix both scenario controls after the controls are defined.
    insert_after(
        nb,
        lambda s: "scenario_controls=[]" in s and '"fluvial_erodibility_k0"' in s,
        fixed_scenarios_cell(),
        "fixed two-scenario settings",
    )
    # Save run metadata immediately after the long model execution cell.
    insert_after(
        nb,
        lambda s: "runner.run(cfg,progress_callback=progress)" in s and "scenario_runtime.append" in s,
        post_run_cell(args.label, args.interval_kyr),
        "persist run metadata",
    )

    # Confirm the notebook's own interval implementation before execution.
    joined = "\n".join(source_text(c) for c in nb.cells if c.cell_type == "code")
    if abs(args.interval_kyr - 1.0) < 1e-12:
        if "interval_kyr=1.0" not in joined or "np.arange(start_ka,end_ka-0.01,-1.0)" not in joined:
            raise RuntimeError("The 1-kyr notebook does not contain its expected 1-kyr time axis.")
    elif abs(args.interval_kyr - 0.1) < 1e-12:
        if "MODEL_INTERVAL_KYR=0.1" not in joined or "interval_kyr=model_interval_kyr" not in joined:
            raise RuntimeError("The 0.1-kyr notebook does not contain its expected 0.1-kyr time axis.")
    else:
        raise ValueError("Only the requested 1.0-kyr and 0.1-kyr notebook variants are supported.")

    executed_path = output_dir / f"{args.label}_executed.ipynb"
    log_path = output_dir / f"{args.label}_execution_status.json"
    start = time.perf_counter()
    os.chdir(output_dir)
    client = StreamingNotebookClient(
        nb,
        timeout=args.timeout_seconds,
        startup_timeout=180,
        kernel_name="python3",
        allow_errors=False,
        record_timing=True,
    )
    try:
        client.execute()
        status = "success"
    except Exception as exc:
        status = "failure"
        nbformat.write(nb, executed_path)
        log_path.write_text(
            json.dumps(
                {
                    "status": status,
                    "label": args.label,
                    "interval_kyr": args.interval_kyr,
                    "elapsed_seconds": time.perf_counter() - start,
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        raise
    else:
        nbformat.write(nb, executed_path)
        log_path.write_text(
            json.dumps(
                {
                    "status": status,
                    "label": args.label,
                    "interval_kyr": args.interval_kyr,
                    "elapsed_seconds": time.perf_counter() - start,
                    "executed_notebook": str(executed_path),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Notebook completed: {executed_path}")
        print(f"Elapsed: {time.perf_counter() - start:.1f} s")


if __name__ == "__main__":
    main()
