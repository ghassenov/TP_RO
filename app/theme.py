from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPalette


class Theme:
    """Theme manager for the application"""

    @staticmethod
    def setup_dark_theme(app):
        """Apply dark theme to application"""
        app.setStyle("Fusion")

        dark_palette = QPalette()

        # Base colors
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Disabled colors
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.gray)
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.gray)
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.gray)

        app.setPalette(dark_palette)

        # Set font
        font = QFont("Segoe UI", 10)
        app.setFont(font)

    @staticmethod
    def setup_light_theme(app):
        """Apply light theme to application"""
        app.setStyle("Fusion")

        light_palette = QPalette()

        # Base colors
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.WindowText, Qt.black)
        light_palette.setColor(QPalette.Base, Qt.white)
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ToolTipText, Qt.black)
        light_palette.setColor(QPalette.Text, Qt.black)
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, Qt.black)
        light_palette.setColor(QPalette.BrightText, Qt.red)
        light_palette.setColor(QPalette.Link, QColor(0, 122, 204))
        light_palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        light_palette.setColor(QPalette.HighlightedText, Qt.white)

        app.setPalette(light_palette)

        # Set font
        font = QFont("Segoe UI", 10)
        app.setFont(font)

    @staticmethod
    def get_module_colors(module_name):
        """Get color scheme for each module"""
        colors = {
            "mailbox": {
                "primary": "#e74c3c",
                "secondary": "#c0392b",
                "light": "#fddfdc",
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #c0392b)"
            },
            "telecom": {
                "primary": "#3498db",
                "secondary": "#2980b9",
                "light": "#d6eaf8",
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9)"
            },
            "antenna": {
                "primary": "#2ecc71",
                "secondary": "#27ae60",
                "light": "#d5f4e6",
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60)"
            },
            "mis": {
                "primary": "#9b59b6",
                "secondary": "#8e44ad",
                "light": "#e8daef",
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9b59b6, stop:1 #8e44ad)"
            }
        }
        return colors.get(module_name, colors["mailbox"])
