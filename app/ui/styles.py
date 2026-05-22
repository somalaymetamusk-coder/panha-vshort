"""Dark stylesheet matching V-Short 3.2 look."""

QSS = """
QWidget {
    background: #0d1b2a;
    color: #e7ecf3;
    font-family: "Segoe UI", "Noto Sans Khmer", "Khmer OS", "Khmer OS Battambang", "Noto Sans", sans-serif;
    font-size: 13px;
}
QMainWindow, QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0a1422, stop:1 #061018);
}
#TopBar {
    background: #0a1422;
    border-bottom: 1px solid #14253a;
}
#TopBarTitle {
    color: #e7ecf3;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
}
#NavButton {
    background: transparent;
    border: none;
    color: #cbd5e1;
    padding: 6px 14px;
    font-size: 14px;
    font-weight: 600;
}
#NavButton:hover { color: #ffffff; }

#TrialBadge {
    background: #18324d;
    border: 1px solid #2a4a73;
    border-radius: 10px;
    padding: 8px 16px;
    color: #ffd166;
    font-weight: 700;
}
#WinBtn, #WinBtnClose {
    background: transparent;
    border: none;
    color: #cbd5e1;
    font-size: 18px;
    padding: 4px 10px;
}
#WinBtn:hover { color: #ffffff; }
#WinBtnClose:hover { color: #ff4b6e; }

#PreviewFrame {
    background: #060a12;
    border: 1px solid #14253a;
    border-radius: 8px;
}
#PreviewLabel {
    background: #060a12;
    border-radius: 6px;
    color: #94a3b8;
}
#PreviewInfo {
    color: #94a3b8;
    font-size: 11px;
}
#PreviewCheckbox {
    color: #38bdf8;
    font-weight: 600;
}

#RightPane {
    background: transparent;
}

#PanelTitle {
    color: #e7ecf3;
    font-size: 18px;
    font-weight: 700;
}

#OutputLabel {
    color: #94a3b8;
}

QLineEdit, QComboBox, QSpinBox {
    background: #0a1422;
    border: 1px solid #1f3553;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e7ecf3;
    selection-background-color: #1d3a5b;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #38bdf8; }

QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #0a1422;
    color: #e7ecf3;
    border: 1px solid #1f3553;
    selection-background-color: #1d3a5b;
}

QTableView {
    background: #0a1422;
    alternate-background-color: #0e1c30;
    gridline-color: #14253a;
    border: 1px solid #14253a;
    border-radius: 4px;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}
QHeaderView::section {
    background: #11203a;
    color: #cbd5e1;
    padding: 6px;
    border: none;
    border-right: 1px solid #14253a;
    font-weight: 700;
}
QTableView::item { padding: 4px 6px; }

QProgressBar {
    background: #0a1422;
    border: 1px solid #14253a;
    border-radius: 6px;
    text-align: center;
    color: #e7ecf3;
    height: 22px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1d4ed8, stop:1 #38bdf8);
    border-radius: 6px;
}

QPushButton#BtnStart {
    background: #16a34a;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 22px;
    font-weight: 700;
}
QPushButton#BtnStart:hover { background: #15803d; }

QPushButton#BtnStop {
    background: #475569;
    color: #cbd5e1;
    border: none;
    border-radius: 6px;
    padding: 8px 22px;
    font-weight: 700;
}
QPushButton#BtnStop:hover { background: #334155; }

QPushButton#BtnReload {
    background: #1e293b;
    color: #e7ecf3;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton#BtnReload:hover { background: #273449; }

QPushButton {
    background: #1f3553;
    color: #e7ecf3;
    border: 1px solid #2a4a73;
    border-radius: 6px;
    padding: 6px 14px;
}
QPushButton:hover { background: #2a4a73; }

QCheckBox {
    color: #cbd5e1;
}
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #2a4a73;
    border-radius: 3px;
    background: #0a1422;
}
QCheckBox::indicator:checked {
    background: #38bdf8;
    border-color: #38bdf8;
}

#FooterLabel {
    color: #6b7280;
    font-size: 11px;
}

QScrollBar:vertical {
    background: #0a1422;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #1f3553;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #2a4a73; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMenu {
    background: #0a1422;
    color: #e7ecf3;
    border: 1px solid #1f3553;
}
QMenu::item:selected { background: #1d3a5b; }
"""
