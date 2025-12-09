from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QFrame,
                               QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSpinBox, QSplitter, QTableWidget,
                               QTabWidget, QTextEdit, QVBoxLayout, QWidget)


class MISUI(QWidget):
    """UI pour l'Ensemble Indépendant Maximum (ordonnancement de tâches)"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QLabel("📊 Maximum Independent Set Scheduling")
        header.setProperty("title", "true")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e67e22, stop:0.5 #d35400, stop:1 #e67e22);
                color: white;
                font-size: 18pt;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL - Inputs
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # Optimization Parameters Card
        param_card = QGroupBox("⚙️ Optimization Parameters")
        param_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #e67e22;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        param_layout = QFormLayout()
        param_layout.setVerticalSpacing(10)
        param_layout.setContentsMargins(15, 20, 15, 15)

        self.comboObjective = QComboBox()
        self.comboObjective.addItems(["Maximiser le nombre de tâches", "Maximiser la somme des priorités"])
        self.comboObjective.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
                min-height: 30px;
            }
            QComboBox:hover {
                border-color: #e67e22;
            }
            QComboBox:focus {
                border-color: #d35400;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                width: 0;
                height: 0;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #e67e22;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #e67e22;
                selection-color: white;
            }
        """)
        param_layout.addRow("🎯 Objective Function:", self.comboObjective)

        self.spinTimeLimit = QSpinBox()
        self.spinTimeLimit.setMinimum(1)
        self.spinTimeLimit.setMaximum(300)
        self.spinTimeLimit.setValue(30)
        self.spinTimeLimit.setSuffix(" s")
        self.spinTimeLimit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QSpinBox:hover {
                border-color: #e67e22;
            }
            QSpinBox:focus {
                border-color: #d35400;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e67e22;
                border-color: #d35400;
            }
        """)
        param_layout.addRow("⏱️ Time Limit:", self.spinTimeLimit)

        self.chkUseWeights = QCheckBox("Utiliser les priorités comme poids")
        self.chkUseWeights.setChecked(True)
        self.chkUseWeights.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-weight: bold;
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #e67e22;
                border-color: #d35400;
            }
            QCheckBox::indicator:hover {
                border-color: #e67e22;
            }
        """)
        param_layout.addRow("", self.chkUseWeights)

        param_card.setLayout(param_layout)
        left_layout.addWidget(param_card)

        # Data Input Tables Card
        data_card = QGroupBox("📋 Task Data")
        data_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #e67e22;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        data_layout = QVBoxLayout(data_card)
        data_layout.setSpacing(10)
        data_layout.setContentsMargins(15, 20, 15, 15)

        # Tasks section
        tasks_label = QLabel("📝 Tasks")
        tasks_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt;")
        data_layout.addWidget(tasks_label)

        self.tableTasks = QTableWidget()
        self.tableTasks.setColumnCount(4)
        self.tableTasks.setHorizontalHeaderLabels(["Name", "Duration", "Priority", "Resource"])
        self.tableTasks.horizontalHeader().setStretchLastSection(True)
        self.tableTasks.setMinimumHeight(150)
        self.tableTasks.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #e67e22;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        data_layout.addWidget(self.tableTasks)

        # Conflicts section
        conflicts_label = QLabel("⚠️ Conflicts")
        conflicts_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt; margin-top: 15px;")
        data_layout.addWidget(conflicts_label)

        self.tableConflicts = QTableWidget()
        self.tableConflicts.setColumnCount(2)
        self.tableConflicts.setHorizontalHeaderLabels(["Task 1", "Task 2"])
        self.tableConflicts.horizontalHeader().setStretchLastSection(True)
        self.tableConflicts.setMinimumHeight(120)
        self.tableConflicts.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #e67e22;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        data_layout.addWidget(self.tableConflicts)

        left_layout.addWidget(data_card)

        # Buttons
        button_layout = QHBoxLayout()

        self.btnAddTask = QPushButton("➕ Add Task")
        self.btnAddTask.setProperty("class", "action")

        self.btnAddConflict = QPushButton("⚠️ Add Conflict")
        self.btnAddConflict.setProperty("class", "action")

        button_layout.addWidget(self.btnAddTask)
        button_layout.addWidget(self.btnAddConflict)
        left_layout.addLayout(button_layout)

        self.btnAutoDetect = QPushButton("🔍 Auto-Detect by Resource")
        self.btnAutoDetect.setProperty("class", "action")
        self.btnAutoDetect.setMinimumHeight(35)
        left_layout.addWidget(self.btnAutoDetect)

        self.btnSolveMIS = QPushButton("🚀 Find Maximum Independent Set")
        self.btnSolveMIS.setProperty("special", "true")
        self.btnSolveMIS.setMinimumHeight(40)
        left_layout.addWidget(self.btnSolveMIS)

        left_layout.addStretch()

        # RIGHT PANEL - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        results_header = QLabel("📊 Results & Visualization")
        results_header.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 5px solid #e67e22;
            }
        """)
        right_layout.addWidget(results_header)

        self.textMISResults = QTextEdit()
        self.textMISResults.setReadOnly(True)
        self.textMISResults.setMinimumHeight(250)
        self.textMISResults.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                padding: 10px;
                font-size: 10pt;
            }
        """)
        right_layout.addWidget(self.textMISResults)

        # Visualization area
        viz_label = QLabel("📈 Conflict Graph Visualization")
        viz_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        right_layout.addWidget(viz_label)

        self.misGraphWidget = QWidget()
        self.misGraphWidget.setMinimumHeight(400)
        self.misGraphWidget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
        right_layout.addWidget(self.misGraphWidget)

        right_layout.addStretch()

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e67e22;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #d35400;
            }
        """)

        main_layout.addWidget(splitter)

    def create_styled_spinbox(self, min_val, max_val, default):
        """Utility method for styled spinboxes (kept for consistency)"""
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QSpinBox:hover {
                border-color: #e67e22;
            }
            QSpinBox:focus {
                border-color: #d35400;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e67e22;
                border-color: #d35400;
            }
        """)
        return spinbox

    def create_styled_doublespinbox(self, min_val, max_val, default):
        """Utility method for styled double spinboxes"""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QDoubleSpinBox:hover {
                border-color: #e67e22;
            }
            QDoubleSpinBox:focus {
                border-color: #d35400;
                background-color: #f8f9fa;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e67e22;
                border-color: #d35400;
            }
        """)
        return spinbox
