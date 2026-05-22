"""Activate License dialog — paste a key, validate, save activation."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel,
    QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from ..core.licensing import LicenseManager, hardware_id
from ..i18n import tr


class ActivateDialog(QDialog):
    def __init__(self, manager: LicenseManager, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle(tr("lic_dialog_title"))
        self.setModal(True)
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("lic_paste_key")))
        self.key_edit = QPlainTextEdit()
        self.key_edit.setPlaceholderText("PNNHA1.eyJ...")
        self.key_edit.setMinimumHeight(80)
        layout.addWidget(self.key_edit)

        # current status
        form = QFormLayout()
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        form.addRow(QLabel(tr("lic_current_status")), self.status_label)

        self.hw_label = QLabel(hardware_id())
        self.hw_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow(QLabel(tr("lic_hardware_id")), self.hw_label)

        form_w = QWidget()
        form_w.setLayout(form)
        layout.addWidget(form_w)

        # buttons
        btn_row = QHBoxLayout()
        self.btn_deactivate = QPushButton(tr("lic_deactivate"))
        self.btn_deactivate.clicked.connect(self._on_deactivate)
        btn_row.addWidget(self.btn_deactivate)
        btn_row.addStretch(1)
        self.btn_activate = QPushButton(tr("lic_activate"))
        self.btn_activate.clicked.connect(self._on_activate)
        btn_row.addWidget(self.btn_activate)
        layout.addLayout(btn_row)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

        self._refresh_status()

    def _refresh_status(self) -> None:
        s = self.manager.display_status()
        self.status_label.setText(s.get("label", ""))
        self.btn_deactivate.setEnabled(s.get("state") in ("licensed", "expired"))

    def _on_activate(self) -> None:
        key = self.key_edit.toPlainText().strip()
        if not key:
            return
        result = self.manager.activate(key)
        if result.ok:
            QMessageBox.information(self, tr("lic_dialog_title"),
                                    tr("lic_activated_ok", name=result.info.name))
            self._refresh_status()
            self.accept()
            return
        QMessageBox.critical(self, tr("lic_dialog_title"),
                             tr("lic_activate_failed", err=result.error))

    def _on_deactivate(self) -> None:
        confirm = QMessageBox.question(
            self, tr("lic_dialog_title"), tr("lic_confirm_deactivate"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.manager.deactivate()
        self._refresh_status()
        self.accept()
