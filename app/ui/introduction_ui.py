"""
Home/Introduction Tab for Optimization Suite
Briefly introduces problems and credits team members
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QSizePolicy,
                               QSpacerItem, QVBoxLayout, QWidget)


class IntroductionTab(QWidget):
    """Introduction tab with problem explanations and team credits"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 20, 25, 20)

        # App Header
        header = QLabel("🚀 Optimization Suite")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        main_layout.addWidget(header)

        subtitle = QLabel("Operations Research Project")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(subtitle)

        # Brief description
        desc_label = QLabel(
            "Five classical optimization problems implemented with Integer Linear Programming"
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #34495e;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(desc_label)

        # Problems section
        problems_label = QLabel("Optimization Problems")
        problems_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }
        """)
        problems_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(problems_label)

        # Problems list - simple and clean
        problems = [
            ("Maximum Independent Set", "Chabbouh Ahmed", "Find largest set of non-connected vertices", "#e67e22"),
            ("Network Design", "Dardouri Louay", "Locate facilities to maximize coverage", "#3498db"),
            ("Maximal Covering Location", "Naouar Ghassen", "Position facilities to maximize demand", "#e74c3c"),
            ("Location and Allocation", "Chiboub Omar", "Place facilities and assign clients", "#9b59b6"),
            ("Network Triangulation", "Khalsi Mohammed Amin", "Decompose surfaces to minimize cost", "#1abc9c")
        ]

        for i, (title, member, desc, color) in enumerate(problems):
            problem_item = self.create_problem_item(title, member, desc, color)
            main_layout.addWidget(problem_item)

            # Add small space between items
            if i < len(problems) - 1:
                main_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Add stretch at bottom
        main_layout.addStretch()

    def create_problem_item(self, title, member, desc, color):
        """Create a clean, simple problem item"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(item)
        layout.setSpacing(6)

        # Title row
        title_layout = QHBoxLayout()

        # Colored dot before title
        dot = QLabel("•")
        dot.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
            }}
        """)
        title_layout.addWidget(dot)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {color};
            }}
        """)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Member
        member_label = QLabel(f"by {member}")
        member_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
            }
        """)
        title_layout.addWidget(member_label)

        layout.addLayout(title_layout)

        # Description
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #34495e;
                padding-left: 10px;
            }
        """)
        layout.addWidget(desc_label)

        return item


class IntroductionController:
    """Controller for introduction tab"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.ui = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI in parent widget"""
        # Clear existing layout
        if self.parent.layout():
            while self.parent.layout().count():
                item = self.parent.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Create new introduction tab
        self.ui = IntroductionTab()

        # Create layout and add tab
        layout = QVBoxLayout(self.parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def refresh(self):
        """Refresh the introduction tab if needed"""
        # Recreate the UI
        self.setup_ui()
