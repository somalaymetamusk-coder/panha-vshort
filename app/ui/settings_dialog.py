"""Settings dialog — language toggle, folders, overlays, audio mode, encoder, CPU limit."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget,
)

from ..core.hardware import available_encoders
from ..core.settings_store import SettingsStore
from ..i18n import available_languages, get_language, set_language, tr


def _picker(line: QLineEdit, btn_text: str, dir_mode: bool, parent: QWidget):
    def _on_click():
        if dir_mode:
            p = QFileDialog.getExistingDirectory(parent, btn_text, line.text() or str(Path.home()))
        else:
            p, _ = QFileDialog.getOpenFileName(parent, btn_text, line.text() or str(Path.home()))
        if p:
            line.setText(p)
    btn = QPushButton(tr("browse"))
    btn.clicked.connect(_on_click)
    return btn


class SettingsDialog(QDialog):
    def __init__(self, store: SettingsStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.setWindowTitle(tr("settings_title"))
        self.setModal(True)
        self.setMinimumWidth(620)

        # ---- General tab ------------------------------------------------
        general = QWidget()
        gform = QFormLayout(general)

        self.lang_combo = QComboBox()
        for code, label in available_languages():
            self.lang_combo.addItem(label, userData=code)
        idx = self.lang_combo.findData(get_language())
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        gform.addRow(QLabel(tr("settings_language")), self.lang_combo)

        self.in_folder = QLineEdit(store.get("input_folder", ""))
        row1 = QHBoxLayout()
        row1.addWidget(self.in_folder); row1.addWidget(_picker(self.in_folder, tr("settings_input_folder"), True, self))
        gform.addRow(QLabel(tr("settings_input_folder")), self._wrap(row1))

        self.out_folder = QLineEdit(store.get("output_folder", ""))
        row2 = QHBoxLayout()
        row2.addWidget(self.out_folder); row2.addWidget(_picker(self.out_folder, tr("settings_output_folder"), True, self))
        gform.addRow(QLabel(tr("settings_output_folder")), self._wrap(row2))

        self.audio_folder = QLineEdit(store.get("audio_folder", ""))
        row3 = QHBoxLayout()
        row3.addWidget(self.audio_folder); row3.addWidget(_picker(self.audio_folder, tr("settings_audio_folder"), True, self))
        gform.addRow(QLabel(tr("settings_audio_folder")), self._wrap(row3))

        self.logo_file = QLineEdit(store.get("logo_file", ""))
        row4 = QHBoxLayout()
        row4.addWidget(self.logo_file); row4.addWidget(_picker(self.logo_file, tr("settings_logo_file"), False, self))
        gform.addRow(QLabel(tr("settings_logo_file")), self._wrap(row4))

        # ---- Overlay / effects tab -------------------------------------
        effects = QWidget()
        eform = QFormLayout(effects)
        self.overlay_text = QLineEdit(store.get("overlay_text", ""))
        eform.addRow(QLabel(tr("settings_overlay_text")), self.overlay_text)

        self.show_timer = QCheckBox()
        self.show_timer.setChecked(bool(store.get("show_timer", False)))
        eform.addRow(QLabel(tr("settings_show_timer")), self.show_timer)

        self.blur_bg = QCheckBox()
        self.blur_bg.setChecked(bool(store.get("blur_background", False)))
        eform.addRow(QLabel(tr("settings_blur_bg")), self.blur_bg)

        self.merge = QCheckBox()
        self.merge.setChecked(bool(store.get("merge", False)))
        eform.addRow(QLabel(tr("settings_merge")), self.merge)

        self.cut_plus = QCheckBox()
        self.cut_plus.setChecked(bool(store.get("cut_plus", False)))
        eform.addRow(QLabel(tr("settings_cut_plus")), self.cut_plus)

        self.cut_parts = QSpinBox()
        self.cut_parts.setRange(1, 20)
        self.cut_parts.setValue(int(store.get("cut_parts", 2)))
        eform.addRow(QLabel(tr("settings_cut_parts")), self.cut_parts)

        self.rename_prefix = QLineEdit(store.get("rename_prefix", "video_"))
        eform.addRow(QLabel(tr("settings_rename_prefix")), self.rename_prefix)

        self.rename_start = QSpinBox()
        self.rename_start.setRange(1, 999999)
        self.rename_start.setValue(int(store.get("rename_start", 1)))
        eform.addRow(QLabel(tr("settings_rename_start")), self.rename_start)

        # ---- Audio + encoder tab ---------------------------------------
        media = QWidget()
        mform = QFormLayout(media)

        self.audio_mode = QComboBox()
        for code, key in [
            ("keep",   "settings_audio_keep"),
            ("mix",    "settings_audio_mix"),
            ("mute",   "settings_audio_mute"),
            ("random", "settings_audio_random"),
            ("mp3",    "settings_audio_mp3"),
        ]:
            self.audio_mode.addItem(tr(key), userData=code)
        idx = self.audio_mode.findData(store.get("audio_mode", "keep"))
        if idx >= 0:
            self.audio_mode.setCurrentIndex(idx)
        mform.addRow(QLabel(tr("settings_audio_mode")), self.audio_mode)

        self.encoder = QComboBox()
        self.encoder.addItem(tr("settings_encoder_auto"), userData="auto")
        avail = {e.key for e in available_encoders()}
        if "nvenc" in avail:
            self.encoder.addItem(tr("settings_encoder_nvenc"), userData="nvenc")
        if "amf" in avail:
            self.encoder.addItem(tr("settings_encoder_amf"), userData="amf")
        self.encoder.addItem(tr("settings_encoder_cpu"), userData="cpu")
        idx = self.encoder.findData(store.get("encoder", "auto"))
        if idx >= 0:
            self.encoder.setCurrentIndex(idx)
        mform.addRow(QLabel(tr("settings_encoder")), self.encoder)

        self.cpu_limit = QSpinBox()
        self.cpu_limit.setRange(1, 32)
        self.cpu_limit.setValue(int(store.get("cpu_limit", 4)))
        mform.addRow(QLabel(tr("settings_cpu_limit")), self.cpu_limit)

        self.fmt = QComboBox()
        for f in ["mp4", "mov", "mkv", "webm"]:
            self.fmt.addItem(f)
        cur = store.get("output_format", "mp4")
        idx = self.fmt.findText(cur)
        if idx >= 0:
            self.fmt.setCurrentIndex(idx)
        mform.addRow(QLabel(tr("settings_output_format")), self.fmt)

        tabs = QTabWidget()
        tabs.addTab(general, tr("settings_tab_general"))
        tabs.addTab(effects, tr("settings_tab_effects"))
        tabs.addTab(media, tr("settings_tab_media"))

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(btns)

    @staticmethod
    def _wrap(layout) -> QWidget:
        w = QWidget()
        w.setLayout(layout)
        return w

    def _on_accept(self) -> None:
        lang = self.lang_combo.currentData()
        if lang:
            set_language(lang)
        self.store.update({
            "language": lang or get_language(),
            "input_folder": self.in_folder.text().strip(),
            "output_folder": self.out_folder.text().strip(),
            "audio_folder": self.audio_folder.text().strip(),
            "logo_file": self.logo_file.text().strip(),
            "overlay_text": self.overlay_text.text(),
            "show_timer": self.show_timer.isChecked(),
            "blur_background": self.blur_bg.isChecked(),
            "merge": self.merge.isChecked(),
            "cut_plus": self.cut_plus.isChecked(),
            "cut_parts": int(self.cut_parts.value()),
            "rename_prefix": self.rename_prefix.text() or "video_",
            "rename_start": int(self.rename_start.value()),
            "audio_mode": self.audio_mode.currentData() or "keep",
            "encoder": self.encoder.currentData() or "auto",
            "cpu_limit": int(self.cpu_limit.value()),
            "output_format": self.fmt.currentText(),
        })
        self.store.save()
        self.accept()
