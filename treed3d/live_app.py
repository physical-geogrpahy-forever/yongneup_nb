from __future__ import annotations

from pathlib import Path
import sys
import traceback

import numpy as np
import pandas as pd
import pyvista as pv
from pyvistaqt import QtInteractor
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from treed3d.live_bridge import LiveEngineProcess, LiveEvent, load_render_state


class EngineWorker(QObject):
    ready = Signal(object)
    state_ready = Signal(object, object)
    status_ready = Signal(object)
    error = Signal(str)
    closed = Signal()

    def __init__(self, repo_root: Path, mode: str, session_dir: Path):
        super().__init__()
        self.repo_root = repo_root
        self.mode = mode
        self.session_dir = session_dir
        self.engine: LiveEngineProcess | None = None

    @Slot()
    def start_engine(self) -> None:
        try:
            self.engine = LiveEngineProcess(self.repo_root, self.mode, self.session_dir)
            self.ready.emit(self.engine.start())
        except Exception:
            self.error.emit(traceback.format_exc())

    @Slot()
    def step_engine(self) -> None:
        try:
            if self.engine is None:
                raise RuntimeError("engine not started")
            event = self.engine.step()
            frame = load_render_state(event)
            self.state_ready.emit(event, frame)
        except Exception:
            self.error.emit(traceback.format_exc())

    @Slot()
    def query_status(self) -> None:
        try:
            if self.engine is None:
                raise RuntimeError("engine not started")
            self.status_ready.emit(self.engine.status())
        except Exception:
            self.error.emit(traceback.format_exc())

    @Slot()
    def close_engine(self) -> None:
        try:
            if self.engine is not None:
                self.engine.close()
                self.engine = None
        finally:
            self.closed.emit()


class LiveWindow(QMainWindow):
    request_start = Signal()
    request_step = Signal()
    request_status = Signal()
    request_close = Signal()

    def __init__(self, repo_root: Path):
        super().__init__()
        self.repo_root = repo_root
        self.thread: QThread | None = None
        self.worker: EngineWorker | None = None
        self.busy = False
        self.auto_running = False
        self.current_event: LiveEvent | None = None
        self.current_frame: pd.DataFrame | None = None

        self.setWindowTitle("TREED3D — Live TREED–Direct AGB–Pelletier")
        self.resize(1450, 900)

        splitter = QSplitter()
        self.plotter = QtInteractor(splitter)
        side = QWidget()
        side_layout = QVBoxLayout(side)

        form = QFormLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["dynamic", "frozen"])
        form.addRow("Scenario", self.mode_combo)
        self.age_label = QLabel("not started")
        form.addRow("Model age", self.age_label)
        self.mean_h_label = QLabel("—")
        form.addRow("Mean H", self.mean_h_label)
        self.mean_agb_label = QLabel("—")
        form.addRow("Mean AGB", self.mean_agb_label)
        self.mean_npp_label = QLabel("—")
        form.addRow("Mean NPP", self.mean_npp_label)
        side_layout.addLayout(form)

        self.start_btn = QPushButton("Start actual model")
        self.step_btn = QPushButton("STEP actual model")
        self.play_btn = QPushButton("Play")
        self.pause_btn = QPushButton("Pause")
        self.export_btn = QPushButton("Export screenshot")
        self.step_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        side_layout.addWidget(self.start_btn)
        side_layout.addWidget(self.step_btn)
        side_layout.addWidget(self.play_btn)
        side_layout.addWidget(self.pause_btn)
        side_layout.addWidget(self.export_btn)
        side_layout.addStretch(1)

        note = QLabel(
            "Renderer rule:\n"
            "Only model-produced state is displayed.\n"
            "Current TREED has no categorical PFT state;\n"
            "PFT crowns remain disabled until the model\n"
            "actually contains PFT/cohort state."
        )
        note.setWordWrap(True)
        side_layout.addWidget(note)

        splitter.addWidget(self.plotter.interactor)
        splitter.addWidget(side)
        splitter.setSizes([1150, 300])
        self.setCentralWidget(splitter)

        self.start_btn.clicked.connect(self.start_session)
        self.step_btn.clicked.connect(self.request_one_step)
        self.play_btn.clicked.connect(self.start_auto)
        self.pause_btn.clicked.connect(self.pause_auto)
        self.export_btn.clicked.connect(self.export_screenshot)

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self._auto_tick)

    def _session_dir(self, mode: str) -> Path:
        return self.repo_root / "treed3d_sessions" / mode

    @Slot()
    def start_session(self) -> None:
        if self.thread is not None:
            QMessageBox.information(self, "TREED3D", "A live model session is already active.")
            return
        mode = self.mode_combo.currentText()
        session_dir = self._session_dir(mode)
        if session_dir.exists():
            # Never silently resume a stale scientific state in v0.
            import shutil
            shutil.rmtree(session_dir)

        self.thread = QThread(self)
        self.worker = EngineWorker(self.repo_root, mode, session_dir)
        self.worker.moveToThread(self.thread)
        self.request_start.connect(self.worker.start_engine)
        self.request_step.connect(self.worker.step_engine)
        self.request_status.connect(self.worker.query_status)
        self.request_close.connect(self.worker.close_engine)
        self.worker.ready.connect(self._on_ready)
        self.worker.state_ready.connect(self._on_state)
        self.worker.status_ready.connect(self._on_status)
        self.worker.error.connect(self._on_error)
        self.worker.closed.connect(self._on_closed)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.request_start.emit()
        self.start_btn.setEnabled(False)

    @Slot(object)
    def _on_ready(self, event: LiveEvent) -> None:
        self.age_label.setText(f"next: {event.fields.get('next_age')} ka BP")
        self.step_btn.setEnabled(True)
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)

    @Slot(object, object)
    def _on_state(self, event: LiveEvent, frame: pd.DataFrame) -> None:
        self.busy = False
        self.current_event = event
        self.current_frame = frame
        self.age_label.setText(f"{event.fields['age']} ka BP")
        self.mean_h_label.setText(f"{float(event.fields['mean_h_m']):.4f} m")
        self.mean_agb_label.setText(f"{float(event.fields['mean_agb_dry_kg_m2']):.4f} kg m⁻²")
        self.mean_npp_label.setText(f"{float(event.fields['mean_npp_gC_m2_yr']):.2f} gC m⁻² yr⁻¹")
        self._render_model_state(frame, event)

    @Slot(object)
    def _on_status(self, event: LiveEvent) -> None:
        self.age_label.setText(f"next: {event.fields.get('next_age')} ka BP")

    @Slot(str)
    def _on_error(self, text: str) -> None:
        self.busy = False
        self.auto_running = False
        QMessageBox.critical(self, "TREED3D model error", text)

    @Slot()
    def _on_closed(self) -> None:
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait(5000)
        self.thread = None
        self.worker = None
        self.start_btn.setEnabled(True)
        self.step_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)

    def request_one_step(self) -> None:
        if self.busy or self.worker is None:
            return
        self.busy = True
        self.request_step.emit()

    def start_auto(self) -> None:
        self.auto_running = True
        self.timer.start()

    def pause_auto(self) -> None:
        self.auto_running = False
        self.timer.stop()

    def _auto_tick(self) -> None:
        if self.auto_running and not self.busy:
            self.request_one_step()

    @staticmethod
    def _xy_from_transform(rows: np.ndarray, cols: np.ndarray, transform_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        v = np.asarray(transform_values).reshape(-1)
        if len(v) < 6:
            return cols.astype(float), -rows.astype(float)
        a, b, c, d, e, f = [float(x) for x in v[:6]]
        cc = cols.astype(float) + 0.5
        rr = rows.astype(float) + 0.5
        x = a * cc + b * rr + c
        y = d * cc + e * rr + f
        return x, y

    def _render_model_state(self, frame: pd.DataFrame, event: LiveEvent) -> None:
        self.plotter.clear()
        session = Path(event.fields["snapshot"]).parents[2]
        state_path = session / "work" / "state_120.npz"
        transform = np.load(state_path, allow_pickle=True)["transform"]

        rows = frame.row.to_numpy(int)
        cols = frame.col.to_numpy(int)
        x, y = self._xy_from_transform(rows, cols, transform)
        z = frame.z_m.to_numpy(float)

        points = np.c_[x, y, z]
        terrain = pv.PolyData(points).delaunay_2d()
        self.plotter.add_mesh(terrain, scalars=terrain.points[:, 2], cmap="terrain", smooth_shading=True, show_scalar_bar=False)

        # Current production TREED has continuous traits but no categorical PFT.
        # Use only actual realized woody state, and color it by the actual a_ll trait.
        woody = (
            (frame.trait_H_m.to_numpy(float) > 0)
            & np.isfinite(frame.trait_H_m.to_numpy(float))
            & (frame.Pelletier_AGB_dry_kg_m2.to_numpy(float) > 0)
        )
        if woody.any():
            wx, wy, wz = x[woody], y[woody], z[woody]
            h = frame.loc[woody, "trait_H_m"].to_numpy(float)
            lai = np.maximum(frame.loc[woody, "LAI"].to_numpy(float), 0.0)
            all_yr = frame.loc[woody, "a_ll_yr"].to_numpy(float)

            crown_points = pv.PolyData(np.c_[wx, wy, wz + h])
            crown_points["a_ll_yr"] = all_yr
            crown_points["radius"] = np.clip(0.8 + np.sqrt(lai + 1e-9), 0.8, 4.0)
            glyph = crown_points.glyph(scale="radius", geom=pv.Sphere(radius=1.0, theta_resolution=10, phi_resolution=10))
            self.plotter.add_mesh(glyph, scalars="a_ll_yr", cmap="viridis", show_scalar_bar=True, scalar_bar_args={"title":"TREED leaf longevity (yr)"})

            stems = []
            for xi, yi, zi, hi in zip(wx, wy, wz, h):
                stems.append(pv.Line((xi, yi, zi), (xi, yi, zi + hi)))
            if stems:
                merged = stems[0]
                for s in stems[1:]:
                    merged = merged.merge(s, merge_points=False)
                self.plotter.add_mesh(merged, color="saddlebrown", line_width=2)

        self.plotter.reset_camera()
        self.plotter.render()

    def export_screenshot(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Export model screenshot", "treed3d.png", "PNG (*.png)")
        if filename:
            self.plotter.screenshot(filename)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.pause_auto()
        if self.worker is not None:
            self.request_close.emit()
        event.accept()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    app = QApplication(sys.argv)
    w = LiveWindow(repo_root)
    w.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
