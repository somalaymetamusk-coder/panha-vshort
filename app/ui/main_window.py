"""Main window — matches the V-Short 3.2 layout from the screenshot."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QPixmap, QFont
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMessageBox, QProgressBar, QPushButton,
    QSpinBox, QSplitter, QTableView, QVBoxLayout, QWidget, QApplication,
)

from .. import APP_AUTHOR, APP_NAME, APP_YEAR
from ..core import scan_folder, ScanResult, VideoItem
from ..core.ffmpeg_runner import (
    RenderOptions, have_ffmpeg, video_dimensions,
)
from ..core.hardware import resolve_encoder
from ..core.preview import apply_preview_effects, first_frame, pil_to_qpixmap
from ..core.render_worker import RenderWorker
from ..core.licensing import LicenseManager
from ..core.settings_store import SettingsStore
from ..core.trial import Trial
from ..i18n import get_language, set_language, subscribe, tr
from .activate_dialog import ActivateDialog
from .settings_dialog import SettingsDialog
from .styles import QSS
from .video_table import (
    COL_AUDIO, COL_LOGO, COL_NAME, COL_STATUS,
    VideoFilterProxy, VideoTableModel,
)

ASSETS = Path(__file__).resolve().parents[2] / "assets"


def _file_size_str(p: Path) -> str:
    try:
        n = p.stat().st_size
    except Exception:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.2f} {unit}" if unit != "B" else f"{int(n)} {unit}"
        n /= 1024
    return f"{n:.2f} TB"


class MainWindow(QMainWindow):
    def __init__(self, store: SettingsStore, trial: Trial,
                 license_manager: Optional[LicenseManager] = None) -> None:
        super().__init__()
        self.store = store
        self.trial = trial
        self.license_manager = license_manager or LicenseManager(trial=trial)
        self.scan: ScanResult = ScanResult()
        self.worker: Optional[RenderWorker] = None

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1240, 760)
        self.setStyleSheet(QSS)

        # ----- top bar ---------------------------------------------------
        self.top_bar = self._build_top_bar()

        # ----- left: live preview ---------------------------------------
        self.preview_frame = self._build_preview()

        # ----- right: detected videos + controls ------------------------
        self.right_pane = self._build_right_pane()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.preview_frame)
        splitter.addWidget(self.right_pane)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 880])

        # ----- footer ----------------------------------------------------
        self.footer = QLabel()
        self.footer.setObjectName("FooterLabel")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self.top_bar)
        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(14, 12, 14, 8)
        body_l.addWidget(splitter)
        outer.addWidget(body, stretch=1)
        outer.addWidget(self.footer)

        self.setCentralWidget(central)
        subscribe(self._retranslate)

        # apply saved language
        set_language(store.get("language", "en"))
        self._retranslate()

        # initial scan
        self.reload_videos()

        if not have_ffmpeg():
            QMessageBox.warning(self, APP_NAME, tr("msg_ffmpeg_missing"))

    # =================================================================
    # builders
    # =================================================================
    def _build_top_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(60)
        h = QHBoxLayout(bar)
        h.setContentsMargins(16, 8, 12, 8)

        self.btn_home = QPushButton("🏠 " + tr("home"))
        self.btn_home.setObjectName("NavButton")
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_home.clicked.connect(self.reload_videos)

        self.btn_settings = QPushButton("⚙ " + tr("settings"))
        self.btn_settings.setObjectName("NavButton")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.open_settings)

        self.btn_help = QPushButton("❓ " + tr("help") + " ▾")
        self.btn_help.setObjectName("NavButton")
        self.btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_help.clicked.connect(self._show_help_menu)

        title = QLabel(APP_NAME)
        title.setObjectName("TopBarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.trial_badge = QPushButton()
        self.trial_badge.setObjectName("TrialBadge")
        self.trial_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.trial_badge.clicked.connect(self.open_activate_dialog)

        self.btn_min = QPushButton("—")
        self.btn_min.setObjectName("WinBtn")
        self.btn_min.setFixedWidth(32)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("WinBtnClose")
        self.btn_close.setFixedWidth(32)
        self.btn_close.clicked.connect(self.close)

        h.addWidget(self.btn_home)
        h.addWidget(self.btn_settings)
        h.addWidget(self.btn_help)
        h.addStretch(1)
        h.addWidget(title)
        h.addStretch(1)
        h.addWidget(self.trial_badge)
        h.addWidget(self.btn_min)
        h.addWidget(self.btn_close)
        return bar

    def _show_help_menu(self) -> None:
        menu = QMenu(self)
        menu.addAction(tr("help_about"), lambda: QMessageBox.about(
            self, APP_NAME,
            f"{APP_NAME}\n\n© {APP_AUTHOR} {APP_YEAR}\n\nBuilt with PyQt6 + ffmpeg.",
        ))
        menu.addAction(tr("help_check_updates"), lambda: QMessageBox.information(
            self, APP_NAME, "You are on the latest version.",
        ))
        menu.addAction(tr("help_contact"), lambda: QMessageBox.information(
            self, APP_NAME, "Telegram: @AdminKh",
        ))
        menu.exec(self.btn_help.mapToGlobal(self.btn_help.rect().bottomLeft()))

    def _build_preview(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("PreviewFrame")
        frame.setMinimumWidth(320)
        v = QVBoxLayout(frame)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        self.preview_label = QLabel(tr("no_preview"))
        self.preview_label.setObjectName("PreviewLabel")
        self.preview_label.setMinimumSize(280, 500)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.preview_label, stretch=1)

        self.preview_checkbox = QCheckBox(tr("live_preview"))
        self.preview_checkbox.setObjectName("PreviewCheckbox")
        self.preview_checkbox.setChecked(True)
        self.preview_checkbox.toggled.connect(lambda _: self.refresh_preview())
        v.addWidget(self.preview_checkbox)

        self.preview_info = QLabel("")
        self.preview_info.setObjectName("PreviewInfo")
        v.addWidget(self.preview_info)
        return frame

    def _build_right_pane(self) -> QWidget:
        pane = QWidget()
        pane.setObjectName("RightPane")
        v = QVBoxLayout(pane)
        v.setContentsMargins(8, 4, 4, 4)
        v.setSpacing(10)

        # header line: 🎬 Detected Videos : N      📁 Output: path
        header = QHBoxLayout()
        self.lbl_detected = QLabel("")
        self.lbl_detected.setObjectName("PanelTitle")
        header.addWidget(self.lbl_detected)
        header.addStretch(1)
        self.lbl_output = QLabel("")
        self.lbl_output.setObjectName("OutputLabel")
        self.lbl_output.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        header.addWidget(self.lbl_output)
        v.addLayout(header)

        # filter row
        row = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.textChanged.connect(self._on_filter_text)
        row.addWidget(self.filter_edit, stretch=3)
        self.filter_combo = QComboBox()
        self.filter_combo.currentIndexChanged.connect(self._on_filter_status)
        row.addWidget(self.filter_combo, stretch=1)
        v.addLayout(row)

        # table
        self.table_model = VideoTableModel([])
        self.proxy = VideoFilterProxy(self)
        self.proxy.setSourceModel(self.table_model)
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(COL_NAME, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(COL_AUDIO, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(COL_LOGO, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(280)
        self.table.selectionModel().selectionChanged.connect(lambda *_: self.refresh_preview())
        v.addWidget(self.table, stretch=1)

        # progress bars
        self.pb_overall = QProgressBar()
        self.pb_overall.setValue(0)
        self.pb_overall.setFormat("%p%")
        v.addWidget(self.pb_overall)

        self.pb_item = QProgressBar()
        self.pb_item.setValue(0)
        self.pb_item.setFormat("%p%")
        v.addWidget(self.pb_item)

        # stats line
        self.lbl_stats = QLabel("")
        v.addWidget(self.lbl_stats)

        # bottom controls
        ctrl = QHBoxLayout()
        self.lbl_threads = QLabel(tr("threads_render"))
        ctrl.addWidget(self.lbl_threads)
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 16)
        self.spin_threads.setValue(int(self.store.get("threads_render", 3)))
        self.spin_threads.setFixedWidth(80)
        self.spin_threads.valueChanged.connect(
            lambda val: (self.store.set("threads_render", int(val)), self.store.save())
        )
        ctrl.addWidget(self.spin_threads)
        ctrl.addStretch(1)
        self.btn_start = QPushButton(tr("start"))
        self.btn_start.setObjectName("BtnStart")
        self.btn_start.clicked.connect(self.start_render)
        ctrl.addWidget(self.btn_start)
        self.btn_stop = QPushButton(tr("stop"))
        self.btn_stop.setObjectName("BtnStop")
        self.btn_stop.clicked.connect(self.stop_render)
        ctrl.addWidget(self.btn_stop)
        self.btn_reload = QPushButton(tr("reload"))
        self.btn_reload.setObjectName("BtnReload")
        self.btn_reload.clicked.connect(self.reload_videos)
        ctrl.addWidget(self.btn_reload)
        v.addLayout(ctrl)

        return pane

    # =================================================================
    # actions
    # =================================================================
    def open_settings(self) -> None:
        dlg = SettingsDialog(self.store, self)
        if dlg.exec():
            self.reload_videos()
            self._retranslate()

    def reload_videos(self) -> None:
        in_folder = self.store.get("input_folder", "")
        self.scan = scan_folder(
            in_folder,
            logo_file=self.store.get("logo_file", ""),
            audio_folder=self.store.get("audio_folder", ""),
        )
        # auto-assign audio/logo for display
        for i, item in enumerate(self.scan.videos):
            item.logo = self.scan.logo
            if self.scan.audios:
                item.audio = self.scan.audios[i % len(self.scan.audios)]
            else:
                item.audio = None
            item.status = "ready"
            item.status_detail = ""
        self.table_model.replace(self.scan.videos)
        self._update_labels()
        if self.scan.videos:
            self.table.selectRow(0)
        self.refresh_preview()

    def _update_labels(self) -> None:
        self.lbl_detected.setText(
            f"📹 {tr('detected_videos')} : {self.scan.video_count} 🎬"
        )
        out = self.store.get("output_folder", "") or "—"
        self.lbl_output.setText(f"📁 {tr('output')}: {out}")
        self.lbl_stats.setText(tr(
            "stats_summary",
            videos=self.scan.video_count,
            audios=self.scan.audio_count,
            logos=self.scan.logo_count,
        ))
        s = self.license_manager.display_status()
        state = s.get("state")
        if state == "licensed":
            self.trial_badge.setText("🔑 " + tr("licensed_to", label=s.get("label", "")))
        elif state == "expired":
            self.trial_badge.setText("⚠ " + tr("license_expired"))
        elif state == "trial":
            self.trial_badge.setText("⏳ " + tr("trial_remaining", days=s.get("days", 0)))
        else:
            self.trial_badge.setText("⏳ " + tr("trial_expired"))
        self.footer.setText(tr("footer", year=APP_YEAR))

    # ---- filters -----------------------------------------------------
    def _on_filter_text(self, text: str) -> None:
        self.proxy.setFilterFixedString(text)

    def _on_filter_status(self, _idx: int) -> None:
        data = self.filter_combo.currentData()
        if data:
            self.proxy.set_status_filter(data)

    # ---- preview -----------------------------------------------------
    def selected_item(self) -> Optional[VideoItem]:
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        src_idx = self.proxy.mapToSource(idx)
        return self.table_model.item_at(src_idx.row())

    def refresh_preview(self) -> None:
        item = self.selected_item()
        if not item or not self.preview_checkbox.isChecked():
            self.preview_label.setText(tr("no_preview"))
            self.preview_label.setPixmap(QPixmap())
            self.preview_info.setText("")
            return
        img = first_frame(item.path)
        if img is None:
            self.preview_label.setText(tr("no_preview"))
            self.preview_label.setPixmap(QPixmap())
            self.preview_info.setText("")
            return
        target_w = max(280, self.preview_label.width())
        target_h = max(360, self.preview_label.height())
        # keep an aspect-correct preview
        target_w, target_h = min(target_w, 360), min(target_h, 640)
        result = apply_preview_effects(
            img,
            blur_background=bool(self.store.get("blur_background", False)),
            overlay_text=self.store.get("overlay_text", ""),
            show_timer=bool(self.store.get("show_timer", False)),
            logo_path=Path(self.store.get("logo_file", "")) if self.store.get("logo_file") else None,
            target_w=target_w,
            target_h=target_h,
        )
        self.preview_label.setPixmap(pil_to_qpixmap(result))
        self.preview_label.setText("")
        w, h = video_dimensions(item.path)
        size = _file_size_str(item.path)
        dst_w, dst_h = (1080, 1920) if self.store.get("blur_background") else (w, h)
        self.preview_info.setText(tr(
            "preview_info",
            size=size, srcw=w, srch=h, dstw=dst_w, dsth=dst_h,
        ))

    # ---- rendering ---------------------------------------------------
    def _options_from_store(self) -> RenderOptions:
        encoder = resolve_encoder(self.store.get("encoder", "auto"))
        return RenderOptions(
            output_folder=Path(self.store.get("output_folder", "")),
            output_format=self.store.get("output_format", "mp4"),
            overlay_text=self.store.get("overlay_text", ""),
            show_timer=bool(self.store.get("show_timer", False)),
            blur_background=bool(self.store.get("blur_background", False)),
            logo_file=Path(self.store.get("logo_file")) if self.store.get("logo_file") else None,
            audio_mode=self.store.get("audio_mode", "keep"),
            audio_file=Path(self.store.get("audio_file")) if self.store.get("audio_file") else None,
            audio_pool=tuple(self.scan.audios),
            encoder=encoder,
            cpu_limit=int(self.store.get("cpu_limit", 4)),
            cut_parts=int(self.store.get("cut_parts", 2)) if self.store.get("cut_plus") else 1,
            rename_prefix=self.store.get("rename_prefix", "video_"),
            rename_index=int(self.store.get("rename_start", 1)),
        )

    def open_activate_dialog(self) -> None:
        dlg = ActivateDialog(self.license_manager, self)
        dlg.exec()
        self._update_labels()

    def start_render(self) -> None:
        if not self.license_manager.can_render():
            # decide which message to show
            if self.license_manager.info and self.license_manager.info.is_expired():
                msg = tr("msg_license_expired")
            else:
                msg = tr("msg_need_license")
            res = QMessageBox.warning(
                self, APP_NAME, msg,
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if res == QMessageBox.StandardButton.Ok:
                self.open_activate_dialog()
            return
        if not have_ffmpeg():
            QMessageBox.critical(self, APP_NAME, tr("msg_ffmpeg_missing"))
            return
        if not self.scan.videos:
            QMessageBox.information(self, APP_NAME, tr("msg_no_videos"))
            return
        if self.worker and self.worker.isRunning():
            return

        opts = self._options_from_store()
        # mp3 / mix without a specific file → use first from audio pool if available
        if opts.audio_mode in ("mp3", "mix") and not opts.audio_file and opts.audio_pool:
            opts.audio_file = opts.audio_pool[0]

        self.worker = RenderWorker(
            items=self.scan.videos,
            opts=opts,
            threads_render=int(self.spin_threads.value()),
            merge=bool(self.store.get("merge", False)),
            rename_prefix=self.store.get("rename_prefix", "video_"),
            rename_start=int(self.store.get("rename_start", 1)),
            cut_parts=int(self.store.get("cut_parts", 2)) if self.store.get("cut_plus") else 1,
        )
        self.worker.item_started.connect(self._on_item_started)
        self.worker.item_progress.connect(self._on_item_progress)
        self.worker.item_finished.connect(self._on_item_finished)
        self.worker.overall_progress.connect(self.pb_overall.setValue)
        self.worker.finished_all.connect(self._on_finished_all)
        self.worker.log.connect(self._on_log)

        self.pb_overall.setValue(0)
        self.pb_item.setValue(0)
        self.btn_start.setEnabled(False)
        self.worker.start()

    def stop_render(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()

    @pyqtSlot(int)
    def _on_item_started(self, row: int) -> None:
        self.table_model.set_status(row, "running")
        self.pb_item.setValue(0)

    @pyqtSlot(int, int)
    def _on_item_progress(self, row: int, pct: int) -> None:
        self.pb_item.setValue(int(pct))

    @pyqtSlot(int, bool, str)
    def _on_item_finished(self, row: int, ok: bool, msg: str) -> None:
        self.table_model.set_status(row, "done" if ok else "error", msg)
        self.pb_item.setValue(100 if ok else 0)

    def _on_finished_all(self) -> None:
        self.btn_start.setEnabled(True)
        QMessageBox.information(self, APP_NAME, tr("msg_done"))

    def _on_log(self, line: str) -> None:
        # could route to a hidden debug panel; for now ignore unless verbose
        pass

    # =================================================================
    # i18n
    # =================================================================
    def _retranslate(self) -> None:
        self.btn_home.setText("🏠 " + tr("home"))
        self.btn_settings.setText("⚙ " + tr("settings"))
        self.btn_help.setText("❓ " + tr("help") + " ▾")
        self.preview_checkbox.setText(tr("live_preview"))
        self.lbl_threads.setText(tr("threads_render"))
        self.btn_start.setText(tr("start"))
        self.btn_stop.setText(tr("stop"))
        self.btn_reload.setText(tr("reload"))
        self.filter_edit.setPlaceholderText(tr("filter_name"))

        # status filter dropdown
        prev = self.filter_combo.currentData() or "all"
        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()
        for code, key in [
            ("all", "all"),
            ("ready", "status_ready"),
            ("running", "status_running"),
            ("done", "status_done"),
            ("error", "status_error"),
        ]:
            self.filter_combo.addItem(tr(key), userData=code)
        idx = self.filter_combo.findData(prev)
        if idx >= 0:
            self.filter_combo.setCurrentIndex(idx)
        self.filter_combo.blockSignals(False)

        self.table_model.refresh_headers()
        self._update_labels()
