"""
PharmIQ — Dark Theme (Catppuccin Mocha)
"""

DARK_STYLE = """
    QMainWindow, QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: Arial;
        font-size: 13px;
    }
    QPushButton {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 6px 14px;
    }
    QPushButton:hover   { background-color: #45475a; border: 1px solid #89b4fa; }
    QPushButton:pressed { background-color: #89b4fa; color: #1e1e2e; }
    QPushButton:disabled{ background-color: #1e1e2e; color: #45475a; border: 1px solid #313244; }

    QTableWidget {
        background-color: #181825;
        color: #cdd6f4;
        gridline-color: #313244;
        border: 1px solid #313244;
        border-radius: 6px;
    }
    QTableWidget::item          { padding: 5px; }
    QTableWidget::item:selected { background-color: #89b4fa; color: #1e1e2e; }
    QHeaderView::section {
        background-color: #313244;
        color: #89b4fa;
        padding: 7px;
        border: none;
        font-weight: bold;
    }
    QLineEdit {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 6px 10px;
    }
    QLineEdit:focus { border: 1px solid #89b4fa; }

    QComboBox {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 5px 10px;
    }
    QComboBox:focus { border: 1px solid #89b4fa; }
    QComboBox QAbstractItemView {
        background-color: #313244;
        color: #cdd6f4;
        selection-background-color: #89b4fa;
        selection-color: #1e1e2e;
    }
    QSpinBox {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 4px 8px;
    }
    QSpinBox:focus { border: 1px solid #89b4fa; }

    QLabel   { color: #cdd6f4; }
    QListWidget {
        background-color: #181825;
        color: #cdd6f4;
        border: 1px solid #313244;
        border-radius: 6px;
    }
    QListWidget::item:selected { background-color: #89b4fa; color: #1e1e2e; }

    QStatusBar { background-color: #181825; color: #a6e3a1; padding: 3px; }

    QTabWidget::pane { border: 1px solid #313244; border-radius: 6px; }
    QTabBar::tab {
        background-color: #313244;
        color: #cdd6f4;
        padding: 8px 16px;
        border-radius: 4px;
        margin-right: 2px;
    }
    QTabBar::tab:selected { background-color: #89b4fa; color: #1e1e2e; font-weight: bold; }
    QTabBar::tab:hover    { background-color: #45475a; }

    QFrame        { border-radius: 8px; }
    QMessageBox   { background-color: #1e1e2e; color: #cdd6f4; }
    QMessageBox QPushButton { min-width: 80px; min-height: 30px; }
    QInputDialog  { background-color: #1e1e2e; color: #cdd6f4; }

    QScrollBar:vertical {
        background-color: #181825; width: 10px; border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background-color: #45475a; border-radius: 5px; min-height: 20px;
    }
    QScrollBar::handle:vertical:hover { background-color: #89b4fa; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar:horizontal {
        background-color: #181825; height: 10px; border-radius: 5px;
    }
    QScrollBar::handle:horizontal {
        background-color: #45475a; border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover { background-color: #89b4fa; }
"""

# ── ألوان الأزرار ────────────────────────────────────────────────────────────
BTN_GREEN  = "background-color: #a6e3a1; color: #1e1e2e; font-weight: bold;"
BTN_RED    = "background-color: #f38ba8; color: #1e1e2e; font-weight: bold;"
BTN_BLUE   = "background-color: #89b4fa; color: #1e1e2e; font-weight: bold;"
BTN_PURPLE = "background-color: #cba6f7; color: #1e1e2e; font-weight: bold;"
BTN_YELLOW = "background-color: #f9e2af; color: #1e1e2e; font-weight: bold;"
BTN_TEAL   = "background-color: #94e2d5; color: #1e1e2e; font-weight: bold;"
BTN_ORANGE = "background-color: #fab387; color: #1e1e2e; font-weight: bold;"
BTN_CYAN   = "background-color: #74c7ec; color: #1e1e2e; font-weight: bold;"
