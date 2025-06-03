"""
主窗口
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QComboBox, QLabel, QHeaderView, QSplitter, QGroupBox,
    QFormLayout, QFrame, QStatusBar, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QAction
from typing import List, Optional

from models.account import Account, AccountType, AccountStatus
from models.database import DatabaseManager
from utils.config import get_config_manager
from utils.encryption import get_encryption_manager
from ui.styles import get_theme_style
from ui.account_dialog import AccountDialog
from ui.login_dialog import LoginDialog
from ui.navigation_bar import NavigationBar
from utils.session import get_session_manager


class AccountTableWidget(QTableWidget):
    """自定义账号表格"""
    
    account_double_clicked = Signal(Account)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accounts: List[Account] = []
        self.setup_table()
    
    def setup_table(self):
        """设置表格"""
        # 设置列
        headers = [
            "ID", "名称", "类型", "分类", "邮箱", "用户名", "状态",
            "订阅类型", "到期日期", "标签", "最后使用", "使用次数", "创建时间"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # 设置表格属性
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # 设置列宽
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # 名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # 邮箱
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 用户名
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 状态
        
        # 隐藏ID列
        self.setColumnHidden(0, True)
        
        # 连接信号
        self.cellDoubleClicked.connect(self.on_cell_double_clicked)
    
    def load_accounts(self, accounts: List[Account]):
        """加载账号数据"""
        self.accounts = accounts
        self.setRowCount(len(accounts))
        
        for row, account in enumerate(accounts):
            self.setItem(row, 0, QTableWidgetItem(str(account.id or "")))
            self.setItem(row, 1, QTableWidgetItem(account.name))
            self.setItem(row, 2, QTableWidgetItem(account.account_type.value))
            self.setItem(row, 3, QTableWidgetItem(account.get_category()))
            self.setItem(row, 4, QTableWidgetItem(account.email))
            self.setItem(row, 5, QTableWidgetItem(account.username))
            
            # 状态列添加颜色
            status_item = QTableWidgetItem(account.status.value)
            if account.status == AccountStatus.ACTIVE:
                status_item.setForeground(QColor("#4caf50"))
            elif account.status == AccountStatus.EXPIRED:
                status_item.setForeground(QColor("#f44336"))
            elif account.status == AccountStatus.SUSPENDED:
                status_item.setForeground(QColor("#ff9800"))
            self.setItem(row, 6, status_item)

            self.setItem(row, 7, QTableWidgetItem(account.subscription_type))
            
            # 到期日期
            expiry_text = ""
            if account.expiry_date:
                expiry_text = account.expiry_date.strftime("%Y-%m-%d")
                if account.is_expired():
                    expiry_item = QTableWidgetItem(expiry_text)
                    expiry_item.setForeground(QColor("#f44336"))
                    self.setItem(row, 8, expiry_item)
                else:
                    self.setItem(row, 8, QTableWidgetItem(expiry_text))
            else:
                self.setItem(row, 8, QTableWidgetItem("无限期"))

            self.setItem(row, 9, QTableWidgetItem(account.tags))

            # 最后使用时间
            last_used_text = ""
            if account.last_used:
                last_used_text = account.last_used.strftime("%Y-%m-%d %H:%M")
            self.setItem(row, 10, QTableWidgetItem(last_used_text))

            self.setItem(row, 11, QTableWidgetItem(str(account.usage_count)))

            # 创建时间
            created_text = ""
            if account.created_at:
                created_text = account.created_at.strftime("%Y-%m-%d %H:%M")
            self.setItem(row, 12, QTableWidgetItem(created_text))
    
    def get_selected_account(self) -> Optional[Account]:
        """获取选中的账号"""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.accounts):
            return self.accounts[current_row]
        return None
    
    def on_cell_double_clicked(self, row: int, column: int):
        """处理单元格双击"""
        if row < len(self.accounts):
            self.account_double_clicked.emit(self.accounts[row])


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.config_manager = get_config_manager()
        self.encryption_manager = get_encryption_manager()
        self.session_manager = get_session_manager()

        self.setWindowTitle("AI开发工具账号管理器")
        self.setMinimumSize(1000, 600)

        # 从配置加载窗口几何信息
        x, y, width, height = self.config_manager.get_window_geometry()
        self.setGeometry(x, y, width, height)

        # 首先显示登录对话框
        if not self.show_login_dialog():
            # 如果登录失败或取消，退出应用
            QApplication.quit()
            return

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_connections()
        self.apply_theme()

        # 加载数据
        self.refresh_accounts()

        # 设置定时器用于自动刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_accounts)
        self.refresh_timer.start(30000)  # 30秒刷新一次

    def show_login_dialog(self) -> bool:
        """显示登录对话框"""
        login_dialog = LoginDialog(self)
        login_dialog.login_successful.connect(self.on_login_successful)
        return login_dialog.exec() == login_dialog.Accepted

    def on_login_successful(self):
        """登录成功处理"""
        # 更新导航栏用户信息（如果已创建）
        if hasattr(self, 'navigation_bar'):
            self.navigation_bar.refresh_user_info()

    def setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 导航栏
        self.navigation_bar = NavigationBar()
        main_layout.addWidget(self.navigation_bar)

        # 搜索和筛选区域
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)

        # 搜索框
        filter_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索账号名称、邮箱、用户名...")
        filter_layout.addWidget(self.search_edit)

        # 类型筛选
        filter_layout.addWidget(QLabel("类型:"))
        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItem("全部", None)
        for account_type in AccountType:
            self.type_filter_combo.addItem(account_type.value, account_type)
        filter_layout.addWidget(self.type_filter_combo)

        # 状态筛选
        filter_layout.addWidget(QLabel("状态:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("全部", None)
        for status in AccountStatus:
            self.status_filter_combo.addItem(status.value, status)
        filter_layout.addWidget(self.status_filter_combo)

        # 分类筛选
        filter_layout.addWidget(QLabel("分类:"))
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("全部", None)
        # 添加常见分类
        categories = ["AI编程助手", "AI聊天助手", "AI API服务", "AI助手", "其他"]
        for category in categories:
            self.category_filter_combo.addItem(category, category)
        filter_layout.addWidget(self.category_filter_combo)

        filter_layout.addStretch()

        main_layout.addWidget(filter_frame)

        # 分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：账号表格
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 表格工具栏
        table_toolbar = QHBoxLayout()

        self.add_button = QPushButton("添加账号")
        self.add_button.setObjectName("success")
        table_toolbar.addWidget(self.add_button)

        self.edit_button = QPushButton("编辑")
        table_toolbar.addWidget(self.edit_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setObjectName("danger")
        table_toolbar.addWidget(self.delete_button)

        table_toolbar.addStretch()

        self.refresh_button = QPushButton("刷新")
        table_toolbar.addWidget(self.refresh_button)

        left_layout.addLayout(table_toolbar)

        # 账号表格
        self.account_table = AccountTableWidget()
        left_layout.addWidget(self.account_table)

        splitter.addWidget(left_widget)

        # 右侧：账号详情
        self.detail_widget = self.create_detail_widget()
        splitter.addWidget(self.detail_widget)

        # 设置分割器比例
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

    def create_detail_widget(self) -> QWidget:
        """创建详情面板"""
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)

        # 标题
        title_label = QLabel("账号详情")
        title_label.setFont(QFont("", 14, QFont.Bold))
        detail_layout.addWidget(title_label)

        # 详情表单
        detail_group = QGroupBox()
        detail_form = QFormLayout(detail_group)

        self.detail_name_label = QLabel("-")
        detail_form.addRow("名称:", self.detail_name_label)

        self.detail_type_label = QLabel("-")
        detail_form.addRow("类型:", self.detail_type_label)

        self.detail_email_label = QLabel("-")
        detail_form.addRow("邮箱:", self.detail_email_label)

        self.detail_username_label = QLabel("-")
        detail_form.addRow("用户名:", self.detail_username_label)

        self.detail_status_label = QLabel("-")
        detail_form.addRow("状态:", self.detail_status_label)

        self.detail_subscription_label = QLabel("-")
        detail_form.addRow("订阅:", self.detail_subscription_label)

        self.detail_expiry_label = QLabel("-")
        detail_form.addRow("到期:", self.detail_expiry_label)

        self.detail_usage_label = QLabel("-")
        detail_form.addRow("使用次数:", self.detail_usage_label)

        self.detail_last_used_label = QLabel("-")
        detail_form.addRow("最后使用:", self.detail_last_used_label)

        self.detail_created_label = QLabel("-")
        detail_form.addRow("创建时间:", self.detail_created_label)

        detail_layout.addWidget(detail_group)

        # 标签
        tags_group = QGroupBox("标签")
        tags_layout = QVBoxLayout(tags_group)
        self.detail_tags_label = QLabel("-")
        self.detail_tags_label.setWordWrap(True)
        tags_layout.addWidget(self.detail_tags_label)
        detail_layout.addWidget(tags_group)

        # 备注
        notes_group = QGroupBox("备注")
        notes_layout = QVBoxLayout(notes_group)
        self.detail_notes_label = QLabel("-")
        self.detail_notes_label.setWordWrap(True)
        self.detail_notes_label.setAlignment(Qt.AlignTop)
        notes_layout.addWidget(self.detail_notes_label)
        detail_layout.addWidget(notes_group)

        # 操作按钮
        action_layout = QHBoxLayout()

        self.use_account_button = QPushButton("标记为已使用")
        action_layout.addWidget(self.use_account_button)

        action_layout.addStretch()
        detail_layout.addLayout(action_layout)

        detail_layout.addStretch()

        return detail_widget

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

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")

        add_action = QAction("添加账号", self)
        add_action.triggered.connect(self.add_account)
        edit_menu.addAction(add_action)

        edit_action = QAction("编辑账号", self)
        edit_action.triggered.connect(self.edit_account)
        edit_menu.addAction(edit_action)

        delete_action = QAction("删除账号", self)
        delete_action.triggered.connect(self.delete_account)
        edit_menu.addAction(delete_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图")

        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.refresh_accounts)
        view_menu.addAction(refresh_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setMovable(False)

        # 添加账号
        add_action = QAction("添加", self)
        add_action.triggered.connect(self.add_account)
        toolbar.addAction(add_action)

        # 编辑账号
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self.edit_account)
        toolbar.addAction(edit_action)

        # 删除账号
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_account)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # 刷新
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.refresh_accounts)
        toolbar.addAction(refresh_action)

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
        # 导航栏连接
        self.navigation_bar.add_account_clicked.connect(self.add_account)
        self.navigation_bar.refresh_clicked.connect(self.refresh_accounts)
        self.navigation_bar.import_accounts_clicked.connect(self.import_accounts)
        self.navigation_bar.export_accounts_clicked.connect(self.export_accounts)
        self.navigation_bar.automation_clicked.connect(self.show_automation_dialog)
        self.navigation_bar.about_clicked.connect(self.show_about)
        self.navigation_bar.logout_clicked.connect(self.handle_logout)

        # 按钮连接
        self.add_button.clicked.connect(self.add_account)
        self.edit_button.clicked.connect(self.edit_account)
        self.delete_button.clicked.connect(self.delete_account)
        self.refresh_button.clicked.connect(self.refresh_accounts)
        self.use_account_button.clicked.connect(self.mark_account_used)

        # 表格连接
        self.account_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.account_table.account_double_clicked.connect(self.edit_account_by_object)

        # 筛选连接
        self.search_edit.textChanged.connect(self.apply_filters)
        self.type_filter_combo.currentTextChanged.connect(self.apply_filters)
        self.status_filter_combo.currentTextChanged.connect(self.apply_filters)
        self.category_filter_combo.currentTextChanged.connect(self.apply_filters)

    def apply_theme(self):
        """应用主题"""
        theme = self.config_manager.get('ui.theme', 'light')
        style = get_theme_style(theme)
        self.setStyleSheet(style)

    def refresh_accounts(self):
        """刷新账号列表"""
        try:
            # 获取当前用户的账号
            current_user = self.session_manager.get_current_user()
            if current_user:
                accounts = self.db_manager.get_accounts_by_user(current_user.id)
            else:
                accounts = []

            self.account_table.load_accounts(accounts)
            self.count_label.setText(f"账号数量: {len(accounts)}")
            self.status_label.setText("数据已刷新")

            # 更新会话活动时间
            self.session_manager.update_activity()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据失败: {str(e)}")

    def apply_filters(self):
        """应用筛选条件"""
        search_text = self.search_edit.text().strip()
        selected_type = self.type_filter_combo.currentData()
        selected_status = self.status_filter_combo.currentData()
        selected_category = self.category_filter_combo.currentData()

        try:
            # 获取当前用户的账号
            current_user = self.session_manager.get_current_user()
            if current_user:
                if search_text:
                    # TODO: 需要修改search_accounts方法以支持用户筛选
                    accounts = self.db_manager.search_accounts(search_text)
                    # 临时筛选当前用户的账号 - 需要修改数据库查询
                    accounts = [acc for acc in accounts]  # 暂时保留所有账号，后续需要修改
                else:
                    accounts = self.db_manager.get_accounts_by_user(current_user.id)
            else:
                accounts = []

            # 应用类型筛选
            if selected_type:
                accounts = [acc for acc in accounts if acc.account_type == selected_type]

            # 应用状态筛选
            if selected_status:
                accounts = [acc for acc in accounts if acc.status == selected_status]

            # 应用分类筛选
            if selected_category:
                accounts = [acc for acc in accounts if acc.get_category() == selected_category]

            self.account_table.load_accounts(accounts)
            self.count_label.setText(f"账号数量: {len(accounts)}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"筛选数据失败: {str(e)}")

    def on_selection_changed(self):
        """处理选择变化"""
        selected_account = self.account_table.get_selected_account()

        # 更新按钮状态
        has_selection = selected_account is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.use_account_button.setEnabled(has_selection)

        # 更新详情面板
        self.update_detail_panel(selected_account)

    def update_detail_panel(self, account: Optional[Account]):
        """更新详情面板"""
        if account is None:
            self.detail_name_label.setText("-")
            self.detail_type_label.setText("-")
            self.detail_email_label.setText("-")
            self.detail_username_label.setText("-")
            self.detail_status_label.setText("-")
            self.detail_subscription_label.setText("-")
            self.detail_expiry_label.setText("-")
            self.detail_usage_label.setText("-")
            self.detail_last_used_label.setText("-")
            self.detail_created_label.setText("-")
            self.detail_tags_label.setText("-")
            self.detail_notes_label.setText("-")
            return

        self.detail_name_label.setText(account.name)
        self.detail_type_label.setText(account.account_type.value)
        self.detail_email_label.setText(account.email or "-")
        self.detail_username_label.setText(account.username or "-")
        self.detail_status_label.setText(account.status.value)
        self.detail_subscription_label.setText(account.subscription_type or "-")

        if account.expiry_date:
            expiry_text = account.expiry_date.strftime("%Y-%m-%d")
            if account.is_expired():
                expiry_text += " (已过期)"
            self.detail_expiry_label.setText(expiry_text)
        else:
            self.detail_expiry_label.setText("无限期")

        self.detail_usage_label.setText(str(account.usage_count))

        if account.last_used:
            self.detail_last_used_label.setText(account.last_used.strftime("%Y-%m-%d %H:%M"))
        else:
            self.detail_last_used_label.setText("-")

        if account.created_at:
            self.detail_created_label.setText(account.created_at.strftime("%Y-%m-%d %H:%M"))
        else:
            self.detail_created_label.setText("-")

        self.detail_tags_label.setText(account.tags or "-")
        self.detail_notes_label.setText(account.notes or "-")

    def add_account(self):
        """添加账号"""
        dialog = AccountDialog(parent=self)
        if dialog.exec() == dialog.Accepted:
            account = dialog.get_account()
            try:
                # 获取当前用户ID
                current_user = self.session_manager.get_current_user()
                if not current_user:
                    QMessageBox.warning(self, "警告", "用户会话已过期，请重新登录！")
                    return

                account_id = self.db_manager.add_account(account, current_user.id)
                account.id = account_id
                self.refresh_accounts()
                self.status_label.setText(f"账号 '{account.name}' 添加成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加账号失败: {str(e)}")

    def edit_account(self):
        """编辑选中的账号"""
        selected_account = self.account_table.get_selected_account()
        if not selected_account:
            QMessageBox.warning(self, "警告", "请先选择要编辑的账号！")
            return

        self.edit_account_by_object(selected_account)

    def edit_account_by_object(self, account: Account):
        """编辑指定的账号对象"""
        dialog = AccountDialog(account, parent=self)
        if dialog.exec() == dialog.Accepted:
            updated_account = dialog.get_account()
            try:
                if self.db_manager.update_account(updated_account):
                    self.refresh_accounts()
                    self.status_label.setText(f"账号 '{updated_account.name}' 更新成功")
                else:
                    QMessageBox.warning(self, "警告", "更新账号失败，账号可能不存在！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新账号失败: {str(e)}")

    def delete_account(self):
        """删除选中的账号"""
        selected_account = self.account_table.get_selected_account()
        if not selected_account:
            QMessageBox.warning(self, "警告", "请先选择要删除的账号！")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除账号 '{selected_account.name}' 吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_account(selected_account.id):
                    self.refresh_accounts()
                    self.status_label.setText(f"账号 '{selected_account.name}' 删除成功")
                else:
                    QMessageBox.warning(self, "警告", "删除账号失败，账号可能不存在！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除账号失败: {str(e)}")

    def mark_account_used(self):
        """标记账号为已使用"""
        selected_account = self.account_table.get_selected_account()
        if not selected_account:
            QMessageBox.warning(self, "警告", "请先选择要标记的账号！")
            return

        try:
            selected_account.update_last_used()
            if self.db_manager.update_account(selected_account):
                self.refresh_accounts()
                self.status_label.setText(f"账号 '{selected_account.name}' 已标记为使用")
            else:
                QMessageBox.warning(self, "警告", "标记失败，账号可能不存在！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"标记账号失败: {str(e)}")

    def import_accounts(self):
        """导入账号"""
        # TODO: 实现导入功能
        QMessageBox.information(self, "提示", "导入功能正在开发中...")

    def export_accounts(self):
        """导出账号"""
        # TODO: 实现导出功能
        QMessageBox.information(self, "提示", "导出功能正在开发中...")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "AI开发工具账号管理器 v1.0\n\n"
            "一个用于管理各种AI开发工具账号的应用程序。\n"
            "支持Cursor、Windsurf、Augment等工具的账号管理。\n\n"
            "功能特性：\n"
            "• 安全的账号信息存储\n"
            "• 账号分类和标签管理\n"
            "• 搜索和筛选功能\n"
            "• 使用情况统计\n"
            "• 现代化的用户界面"
        )

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口几何信息
        geometry = self.geometry()
        self.config_manager.set_window_geometry(
            geometry.x(), geometry.y(),
            geometry.width(), geometry.height()
        )

        event.accept()

    def handle_logout(self):
        """处理退出登录"""
        self.session_manager.logout()
        # 重新显示登录对话框
        if self.show_login_dialog():
            # 登录成功，刷新界面
            self.navigation_bar.refresh_user_info()
            self.refresh_accounts()
        else:
            # 登录失败或取消，退出应用
            QApplication.quit()

    def show_automation_dialog(self):
        """显示自动化对话框"""
        try:
            dialog = AutomationDialog(self)
            dialog.automation_completed.connect(self.on_automation_completed)
            dialog.exec()
        except ImportError:
            QMessageBox.warning(
                self, "功能不可用",
                "自动化功能需要安装DrissionPage库。\n\n"
                "请运行以下命令安装：\n"
                "pip install DrissionPage"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开自动化对话框失败: {str(e)}")

    def on_automation_completed(self, result):
        """自动化完成处理"""
        from automation.automation_manager import AutomationStatus

        if result.is_success:
            # 如果自动化成功，可以选择自动添加账号到系统
            reply = QMessageBox.question(
                self, "自动化成功",
                f"自动化操作成功完成！\n\n"
                f"是否要将此账号添加到系统中进行管理？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes and result.data:
                # 创建账号对象并添加到系统
                self.add_account_from_automation_result(result)

        elif result.needs_manual_intervention:
            QMessageBox.information(
                self, "需要手动干预",
                f"自动化过程需要手动干预：\n\n{result.message}\n\n"
                f"请按照提示完成相应操作。"
            )
        else:
            QMessageBox.warning(
                self, "自动化失败",
                f"自动化操作失败：\n\n{result.message}"
            )

    def add_account_from_automation_result(self, result):
        """从自动化结果添加账号"""
        try:
            # 这里可以根据自动化结果创建账号
            # 由于自动化结果可能不包含完整的账号信息，
            # 可以打开账号对话框让用户补充信息

            dialog = AccountDialog(parent=self)

            # 预填充已知信息
            if result.data:
                if 'email' in result.data:
                    dialog.email_edit.setText(result.data['email'])
                if 'password' in result.data:
                    dialog.password_edit.setText(result.data['password'])
                if 'username' in result.data:
                    dialog.username_edit.setText(result.data['username'])

            # 设置对话框标题
            dialog.setWindowTitle("添加自动化创建的账号")

            if dialog.exec() == dialog.Accepted:
                account = dialog.get_account()
                current_user = self.session_manager.get_current_user()
                if current_user:
                    account_id = self.db_manager.add_account(account, current_user.id)
                    account.id = account_id
                    self.refresh_accounts()
                    self.status_label.setText(f"账号 '{account.name}' 添加成功")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加账号失败: {str(e)}")
