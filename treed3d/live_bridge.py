from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import TextIO

import pandas as pd


@dataclass(frozen=True)
class LiveEvent:
    kind: str
    fields: dict[str, str]
    raw: str

    @property
    def age(self) -> int | None:
        value = self.fields.get("age")
        return None if value is None else int(float(value))


class LiveEngineProcess:
    """Long-lived Python bridge to the *actual* Julia TREED/Pelletier engine.

    This class never fabricates ecological state. ``step()`` blocks until the
    Julia model has completed one audited age step and returns paths to the
    model-produced state tables.
    """

    def __init__(
        self,
        repo_root: str | Path,
        mode: str,
        session_dir: str | Path,
        julia: str = "julia",
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.mode = mode
        self.session_dir = Path(session_dir).resolve()
        self.julia = julia
        self.proc: subprocess.Popen[str] | None = None
        self.diagnostics: list[str] = []

    @staticmethod
    def _parse_event(line: str) -> LiveEvent:
        parts = line.rstrip("\n").split("\t")
        kind = parts[0]
        fields: dict[str, str] = {}
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                fields[key] = value
        return LiveEvent(kind=kind, fields=fields, raw=line.rstrip("\n"))

    def _read_until(self, prefix: str) -> LiveEvent:
        if self.proc is None or self.proc.stdout is None:
            raise RuntimeError("live engine is not running")
        for line in self.proc.stdout:
            if line.startswith(prefix):
                return self._parse_event(line)
            self.diagnostics.append(line.rstrip("\n"))
        code = self.proc.poll()
        raise RuntimeError(f"Julia live engine terminated before {prefix!r}; returncode={code}")

    def start(self) -> LiveEvent:
        if self.proc is not None:
            raise RuntimeError("live engine already started")
        if self.mode not in {"dynamic", "frozen"}:
            raise ValueError("mode must be dynamic or frozen")

        script = self.repo_root / "treed3d" / "live_engine.jl"
        project = self.repo_root / "treed120"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.julia,
            f"--project={project}",
            str(script),
            self.mode,
            str(self.session_dir),
        ]
        self.proc = subprocess.Popen(
            cmd,
            cwd=self.repo_root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return self._read_until("LIVE_READY")

    def _send(self, command: str, expect: str) -> LiveEvent:
        if self.proc is None or self.proc.stdin is None:
            raise RuntimeError("live engine is not running")
        self.proc.stdin.write(command + "\n")
        self.proc.stdin.flush()
        return self._read_until(expect)

    def step(self) -> LiveEvent:
        return self._send("STEP", "LIVE_STATE")

    def run_steps(self, n: int) -> list[LiveEvent]:
        if n < 1:
            raise ValueError("n must be >= 1")
        if self.proc is None or self.proc.stdin is None:
            raise RuntimeError("live engine is not running")
        self.proc.stdin.write(f"RUN {n}\n")
        self.proc.stdin.flush()
        return [self._read_until("LIVE_STATE") for _ in range(n)]

    def status(self) -> LiveEvent:
        return self._send("STATUS", "LIVE_STATUS")

    def close(self) -> None:
        if self.proc is None:
            return
        if self.proc.poll() is None and self.proc.stdin is not None:
            try:
                self.proc.stdin.write("QUIT\n")
                self.proc.stdin.flush()
                self._read_until("LIVE_BYE")
            except Exception:
                self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.proc = None

    def __enter__(self) -> "LiveEngineProcess":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def load_render_state(event: LiveEvent) -> pd.DataFrame:
    """Load only model-produced state for rendering.

    The geomorphic snapshot is merged with the same-step physiology summary to
    add fields such as FPC/GPP/BGB. No interpolation or synthetic PFT is added.
    """

    if event.kind != "LIVE_STATE":
        raise ValueError("load_render_state requires a LIVE_STATE event")
    snap = pd.read_csv(event.fields["snapshot"])
    summary = pd.read_csv(event.fields["summary"])
    extra = [
        c
        for c in [
            "row",
            "col",
            "FPC",
            "GPP_gC_m2_yr",
            "BGB_C_g_m2_component_sum",
            "seasonality",
            "r_s_r",
            "Net_C_gain_gC_m2_yr",
        ]
        if c in summary.columns
    ]
    if {"row", "col"}.issubset(extra):
        snap = snap.merge(summary[extra], on=["row", "col"], how="left", validate="one_to_one")
    return snap
