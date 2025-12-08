STYLESHEET = """
/* ===== GLOBAL STYLES ===== */
QMainWindow {
    background-color: #2c3e50;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {
    border: 1px solid #34495e;
    background-color: #ecf0f1;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #34495e;
    color: #bdc3c7;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    font-size: 12pt;
}

QTabBar::tab:selected {
    background-color: #3498db;
    color: white;
    border-bottom: 3px solid #2980b9;
}

QTabBar::tab:hover {
    background-color: #4a6fa5;
    color: white;
}

/* ===== GROUP BOXES ===== */
QGroupBox {
    font-weight: bold;
    border: 2px solid #3498db;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: #2c3e50;
    font-size: 12pt;
}

/* ===== BUTTONS ===== */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 11pt;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #2980b9;
    border: 2px solid #1c6ea4;
}

QPushButton:pressed {
    background-color: #1c6ea4;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

/* Special buttons */
QPushButton[special="true"] {
    background-color: #2ecc71;
    font-size: 12pt;
    padding: 12px 24px;
}

QPushButton[special="true"]:hover {
    background-color: #27ae60;
}

/* ===== TABLES ===== */
QTableWidget {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    gridline-color: #ecf0f1;
    selection-background-color: #3498db;
    selection-color: white;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 8px;
    border: 1px solid #2c3e50;
    font-weight: bold;
}

/* ===== LABELS ===== */
QLabel {
    color: #2c3e50;
    font-size: 11pt;
}

QLabel[title="true"] {
    font-size: 16pt;
    font-weight: bold;
    color: #2c3e50;
    padding: 10px;
    background-color: #3498db;
    color: white;
    border-radius: 6px;
}

/* ===== TEXT EDIT ===== */
QTextEdit {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', monospace;
}

/* ===== SPIN BOXES & COMBO BOXES ===== */
QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    min-height: 25px;
}

QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover, QLineEdit:hover {
    border-color: #3498db;
}

/* ===== SPLITTER ===== */
QSplitter::handle {
    background-color: #3498db;
    width: 4px;
}

QSplitter::handle:hover {
    background-color: #2980b9;
}

/* ===== CHECKBOX ===== */
QCheckBox {
    color: #2c3e50;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:checked {
    background-color: #3498db;
    border: 2px solid #2980b9;
    border-radius: 3px;
}

/* ===== STATUS BAR ===== */
QStatusBar {
    background-color: #34495e;
    color: white;
    font-size: 10pt;
}

/* ===== CUSTOM COLORS FOR EACH MODULE ===== */
/* Mailbox Module */
QTabBar::tab[mtype="mailbox"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #e74c3c, stop:1 #c0392b);
}

/* Telecom Module */
QTabBar::tab[mtype="telecom"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3498db, stop:1 #2980b9);
}

/* Antenna Module */
QTabBar::tab[mtype="antenna"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2ecc71, stop:1 #27ae60);
}

/* MIS Module */
QTabBar::tab[mtype="mis"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #9b59b6, stop:1 #8e44ad);
}
"""
