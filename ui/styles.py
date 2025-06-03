"""
UI样式定义
"""

# 主题样式
LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}

QTableWidget {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    gridline-color: #e0e0e0;
    selection-background-color: #e3f2fd;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f0f0f0;
}

QTableWidget::item:selected {
    background-color: #e3f2fd;
    color: #1976d2;
}

QHeaderView::section {
    background-color: #f8f9fa;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #e0e0e0;
    font-weight: bold;
    color: #333;
}

QPushButton {
    background-color: #1976d2;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0d47a1;
}

QPushButton:disabled {
    background-color: #ccc;
    color: #666;
}

QPushButton.danger {
    background-color: #d32f2f;
}

QPushButton.danger:hover {
    background-color: #c62828;
}

QPushButton.success {
    background-color: #388e3c;
}

QPushButton.success:hover {
    background-color: #2e7d32;
}

QLineEdit, QTextEdit, QComboBox {
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    padding: 8px;
    background-color: white;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #1976d2;
}

QLabel {
    color: #333;
    font-size: 14px;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #1976d2;
}

QToolBar {
    background-color: white;
    border-bottom: 1px solid #e0e0e0;
    spacing: 5px;
    padding: 5px;
}

QStatusBar {
    background-color: #f8f9fa;
    border-top: 1px solid #e0e0e0;
    color: #666;
}

QMenuBar {
    background-color: white;
    border-bottom: 1px solid #e0e0e0;
}

QMenuBar::item {
    padding: 8px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #e3f2fd;
    color: #1976d2;
}

QMenu {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 6px;
}

QMenu::item {
    padding: 8px 20px;
}

QMenu::item:selected {
    background-color: #e3f2fd;
    color: #1976d2;
}

QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 6px;
    background-color: white;
}

QTabBar::tab {
    background-color: #f8f9fa;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid #1976d2;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #ccc;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #999;
}
"""

DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QTableWidget {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 8px;
    gridline-color: #555;
    selection-background-color: #4a4a4a;
    color: #ffffff;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #555;
}

QTableWidget::item:selected {
    background-color: #4a4a4a;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #404040;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #555;
    font-weight: bold;
    color: #ffffff;
}

QPushButton {
    background-color: #0d7377;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #14a085;
}

QPushButton:pressed {
    background-color: #0a5d61;
}

QLineEdit, QTextEdit, QComboBox {
    border: 2px solid #555;
    border-radius: 6px;
    padding: 8px;
    background-color: #3c3c3c;
    color: #ffffff;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #0d7377;
}

QLabel {
    color: #ffffff;
    font-size: 14px;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #555;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #0d7377;
}
"""


def get_theme_style(theme: str = "light") -> str:
    """获取主题样式"""
    if theme.lower() == "dark":
        return DARK_THEME
    return LIGHT_THEME
