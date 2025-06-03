"""
AI开发工具账号管理器主程序
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("AI开发工具账号管理器")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AI Tools Manager")
    
    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
