"""Qt model for the detected-videos table."""
from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QBrush, QColor

from ..core.video_scanner import VideoItem
from ..i18n import tr


COL_INDEX, COL_NAME, COL_AUDIO, COL_LOGO, COL_STATUS = range(5)
_STATUS_COLORS = {
    "ready":   QColor("#e7ecf3"),
    "queued":  QColor("#cbd5e1"),
    "running": QColor("#38bdf8"),
    "done":    QColor("#22c55e"),
    "error":   QColor("#ef4444"),
}


class VideoTableModel(QAbstractTableModel):
    def __init__(self, items: Optional[List[VideoItem]] = None, parent=None) -> None:
        super().__init__(parent)
        self._items: List[VideoItem] = list(items or [])

    # --- standard Qt overrides ----------------------------------------
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 5

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return {
                COL_INDEX: tr("col_index"),
                COL_NAME: tr("col_name"),
                COL_AUDIO: tr("col_audio"),
                COL_LOGO: tr("col_logo"),
                COL_STATUS: tr("col_status"),
            }.get(section, "")
        return str(section + 1)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        item = self._items[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == COL_INDEX:
                return item.index
            if col == COL_NAME:
                return item.name
            if col == COL_AUDIO:
                return item.audio.name if item.audio else "-"
            if col == COL_LOGO:
                return item.logo.name if item.logo else "-"
            if col == COL_STATUS:
                key = f"status_{item.status}"
                base = tr(key)
                return f"{base} — {item.status_detail}" if item.status_detail else base
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (COL_INDEX,):
                return int(Qt.AlignmentFlag.AlignCenter)
            return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        elif role == Qt.ItemDataRole.ForegroundRole and col == COL_STATUS:
            return QBrush(_STATUS_COLORS.get(item.status, QColor("#e7ecf3")))
        elif role == Qt.ItemDataRole.UserRole:
            return item
        return None

    # --- helpers ------------------------------------------------------
    def replace(self, items: List[VideoItem]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()

    def items(self) -> List[VideoItem]:
        return list(self._items)

    def item_at(self, row: int) -> Optional[VideoItem]:
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def set_status(self, row: int, status: str, detail: str = "") -> None:
        if 0 <= row < len(self._items):
            self._items[row].status = status
            self._items[row].status_detail = detail
            idx = self.index(row, COL_STATUS)
            self.dataChanged.emit(idx, idx)

    def refresh_headers(self) -> None:
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, self.columnCount() - 1)


class VideoFilterProxy(QSortFilterProxyModel):
    """Adds a status filter on top of QSortFilterProxyModel's name filter."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(COL_NAME)
        self._status_filter = "all"  # all | ready | running | done | error

    def set_status_filter(self, key: str) -> None:
        self._status_filter = key
        self.invalidateFilter()

    def filterAcceptsRow(self, row: int, parent: QModelIndex) -> bool:
        if not super().filterAcceptsRow(row, parent):
            return False
        if self._status_filter == "all":
            return True
        model = self.sourceModel()
        if not isinstance(model, VideoTableModel):
            return True
        item = model.item_at(row)
        return bool(item and item.status == self._status_filter)
