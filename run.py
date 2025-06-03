#!/usr/bin/env python3
"""
启动脚本
"""
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # 直接导入并运行主程序
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    from ui.main_window import MainWindow

    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序属性
    app.setApplicationName("AI开发工具账号管理器")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AI Tools Manager")

    # 设置高DPI支持（兼容Qt6）
    try:
        # Qt6中这些属性已弃用，但为了兼容性保留
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # Qt6中可能不存在这些属性
        pass

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())
