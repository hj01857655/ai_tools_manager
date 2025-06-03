"""
主窗口
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QStackedWidget, QStatusBar, QMessageBox,
    QLabel
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction

from models.database import DatabaseManager
from utils.config import get_config_manager
from utils.encryption import get_encryption_manager
from ui.styles import get_theme_style
from ui.sidebar_navigation import SidebarNavigation
from ui.account_page import AccountPage
from ui.home_page import HomePage
from ui.logs_page import LogsPage
from ui.settings_page import SettingsPage
from ui.cursor_enhanced_page import CursorEnhancedPage





class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.config_manager = get_config_manager()
        self.encryption_manager = get_encryption_manager()
        # self.session_manager = get_session_manager()  # 暂时禁用

        self.setWindowTitle("AI开发工具账号管理器")
        self.setMinimumSize(1000, 600)

        # 从配置加载窗口几何信息
        x, y, width, height = self.config_manager.get_window_geometry()
        self.setGeometry(x, y, width, height)

        # 暂时跳过登录功能（开发阶段）
        # if not self.show_login_dialog():
        #     QApplication.quit()
        #     return

        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        self.apply_theme()

        # 设置定时器用于自动刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_current_page)
        self.refresh_timer.start(30000)  # 30秒刷新一次

    # 登录功能暂时禁用（开发阶段）
    # def show_login_dialog(self) -> bool:
    #     """显示登录对话框"""
    #     login_dialog = LoginDialog(self)
    #     login_dialog.login_successful.connect(self.on_login_successful)
    #     return login_dialog.exec() == login_dialog.Accepted

    def setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 水平分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边导航
        self.sidebar = SidebarNavigation()
        main_layout.addWidget(self.sidebar)

        # 页面容器
        self.page_stack = QStackedWidget()
        main_layout.addWidget(self.page_stack)

        # 创建各个页面
        self.pages = {}
        self.create_pages()

    def create_pages(self):
        """创建所有页面"""
        # 创建首页
        home_page = HomePage()
        home_page.tool_selected.connect(self.switch_page)
        self.pages["home"] = home_page
        self.page_stack.addWidget(home_page)

        # 创建工具页面
        # Cursor使用增强页面
        cursor_page = CursorEnhancedPage()
        self.pages["cursor"] = cursor_page
        self.page_stack.addWidget(cursor_page)

        # 其他工具使用标准页面
        other_page_configs = [
            ("windsurf", "Windsurf"),
            ("augment", "Augment")
        ]

        for page_id, _ in other_page_configs:
            page = AccountPage(page_id)
            self.pages[page_id] = page
            self.page_stack.addWidget(page)

        # 创建系统页面
        # 日志页面
        logs_page = LogsPage()
        self.pages["logs"] = logs_page
        self.page_stack.addWidget(logs_page)

        # 设置页面
        settings_page = SettingsPage()
        settings_page.settings_changed.connect(self.on_settings_changed)
        self.pages["settings"] = settings_page
        self.page_stack.addWidget(settings_page)





    def setup_menu(self):
        """设置菜单"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        import_action = QAction("导入账号", self)
        import_action.triggered.connect(self.import_accounts)
        file_menu.addAction(import_action)

        export_action = QAction("导出账号", self)
        export_action.triggered.connect(self.export_accounts)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图")

        refresh_action = QAction("刷新当前页面", self)
        refresh_action.triggered.connect(self.refresh_current_page)
        view_menu.addAction(refresh_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.status_label = QLabel("就绪")
        self.statusbar.addWidget(self.status_label)

        self.count_label = QLabel("账号数量: 0")
        self.statusbar.addPermanentWidget(self.count_label)

    def setup_connections(self):
        """设置信号连接"""
        # 侧边导航连接
        self.sidebar.page_changed.connect(self.switch_page)

    def switch_page(self, page_id: str):
        """切换页面"""
        if page_id in self.pages:
            page = self.pages[page_id]
            self.page_stack.setCurrentWidget(page)

            # 更新状态栏
            if page_id == "home":
                self.status_label.setText("当前页面: 首页")
                # 刷新首页数据
                page.refresh_data()
            elif page_id == "logs":
                self.status_label.setText("当前页面: 日志")
                # 刷新日志数据
                page.refresh_logs()
            elif page_id == "settings":
                self.status_label.setText("当前页面: 设置")
                # 加载设置数据
                page.load_settings()
            elif page_id == "cursor":
                self.status_label.setText("当前页面: Cursor")
                # 刷新Cursor增强页面数据
                page.refresh_accounts()
            else:
                page_name = page.account_type.value
                self.status_label.setText(f"当前页面: {page_name}")
                # 刷新页面数据
                page.refresh_accounts()

            # 更新侧边导航选择状态
            self.sidebar.select_page(page_id)

    def refresh_current_page(self):
        """刷新当前页面"""
        current_widget = self.page_stack.currentWidget()
        if isinstance(current_widget, AccountPage):
            current_widget.refresh_accounts()
        elif isinstance(current_widget, HomePage):
            current_widget.refresh_data()
        elif isinstance(current_widget, LogsPage):
            current_widget.refresh_logs()
        elif isinstance(current_widget, SettingsPage):
            current_widget.load_settings()
        elif isinstance(current_widget, CursorEnhancedPage):
            current_widget.refresh_accounts()

    def on_settings_changed(self):
        """设置变更处理"""
        try:
            # 重新应用主题
            self.apply_theme()

            # 刷新所有页面
            self.refresh_current_page()

            # 记录日志
            from utils.logger import get_logger
            logger = get_logger()
            logger.info("应用设置已更新")

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "警告", f"应用设置变更失败: {str(e)}")

    def apply_theme(self):
        """应用主题"""
        theme = self.config_manager.get('ui.theme', 'light')
        style = get_theme_style(theme)
        self.setStyleSheet(style)

    def import_accounts(self):
        """导入账号"""
        QMessageBox.information(self, "提示", "导入功能正在开发中...")

    def export_accounts(self):
        """导出账号"""
        QMessageBox.information(self, "提示", "导出功能正在开发中...")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于AI工具管理器",
            "<h3>AI工具管理器 v1.0.0</h3>"
            "<p>一个专业的AI开发工具账号管理平台</p>"
            "<p><b>主要功能：</b></p>"
            "<ul>"
            "<li>🤖 支持15种AI工具类型</li>"
            "<li>🔐 安全的账号存储和管理</li>"
            "<li>⚡ 自动化注册登录（Cursor、Windsurf、Augment）</li>"
            "<li>📊 智能分类和筛选</li>"
            "<li>🎨 现代化用户界面</li>"
            "</ul>"
            "<p><b>技术栈：</b></p>"
            "<p>PySide6 + SQLite + DrissionPage</p>"
            "<p><b>开发者：</b> AI工具管理器团队</p>"
        )

    def closeEvent(self, event):
        """关闭事件"""
        # 保存窗口几何信息
        geometry = self.geometry()
        self.config_manager.set_window_geometry(
            geometry.x(), geometry.y(),
            geometry.width(), geometry.height()
        )

        event.accept()
