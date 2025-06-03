"""
账号管理页面组件
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QGroupBox, QFormLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from models.account import Account, AccountType, AccountStatus
from models.database import DatabaseManager
from ui.account_dialog import AccountDialog
from ui.automation_dialog import AutomationDialog
from automation.automation_manager import is_automation_supported
from datetime import datetime


class AccountTableWidget(QTableWidget):
    """账号表格组件"""
    
    account_double_clicked = Signal(object)  # Account对象
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accounts = []
        self.setup_table()
    
    def setup_table(self):
        """设置表格"""
        # 设置列
        headers = [
            "ID", "名称", "邮箱", "用户名", "状态", 
            "订阅类型", "到期日期", "标签", "最后使用", "使用次数", "创建时间"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # 设置表格属性
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSortingEnabled(True)
        
        # 设置列宽
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 名称
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 邮箱
        
        # 连接双击信号
        self.cellDoubleClicked.connect(self.on_cell_double_clicked)
    
    def load_accounts(self, accounts):
        """加载账号数据"""
        self.accounts = accounts
        self.setRowCount(len(accounts))
        
        for row, account in enumerate(accounts):
            self.setItem(row, 0, QTableWidgetItem(str(account.id or "")))
            self.setItem(row, 1, QTableWidgetItem(account.name))
            self.setItem(row, 2, QTableWidgetItem(account.email))
            self.setItem(row, 3, QTableWidgetItem(account.username))
            
            # 状态列添加颜色
            status_item = QTableWidgetItem(account.status.value)
            if account.status == AccountStatus.ACTIVE:
                status_item.setForeground(QColor("#4caf50"))
            elif account.status == AccountStatus.EXPIRED:
                status_item.setForeground(QColor("#f44336"))
            elif account.status == AccountStatus.SUSPENDED:
                status_item.setForeground(QColor("#ff9800"))
            self.setItem(row, 4, status_item)
            
            self.setItem(row, 5, QTableWidgetItem(account.subscription_type))
            
            # 到期日期
            expiry_text = ""
            if account.expiry_date:
                expiry_text = account.expiry_date.strftime("%Y-%m-%d")
                if account.is_expired():
                    expiry_item = QTableWidgetItem(expiry_text)
                    expiry_item.setForeground(QColor("#f44336"))
                    self.setItem(row, 6, expiry_item)
                else:
                    self.setItem(row, 6, QTableWidgetItem(expiry_text))
            else:
                self.setItem(row, 6, QTableWidgetItem("无限期"))
            
            self.setItem(row, 7, QTableWidgetItem(account.tags))
            
            # 最后使用时间
            last_used_text = ""
            if account.last_used:
                last_used_text = account.last_used.strftime("%Y-%m-%d %H:%M")
            self.setItem(row, 8, QTableWidgetItem(last_used_text))
            
            self.setItem(row, 9, QTableWidgetItem(str(account.usage_count)))
            
            # 创建时间
            created_text = ""
            if account.created_at:
                created_text = account.created_at.strftime("%Y-%m-%d %H:%M")
            self.setItem(row, 10, QTableWidgetItem(created_text))
    
    def get_selected_account(self):
        """获取选中的账号"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.accounts):
            return self.accounts[current_row]
        return None
    
    def on_cell_double_clicked(self, row: int, column: int):
        """处理单元格双击"""
        if row < len(self.accounts):
            self.account_double_clicked.emit(self.accounts[row])


class AccountPage(QWidget):
    """账号管理页面"""
    
    def __init__(self, account_type_id: str, parent=None):
        super().__init__(parent)
        self.account_type_id = account_type_id
        self.account_type = self.get_account_type_from_id(account_type_id)
        self.db_manager = DatabaseManager()
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        self.refresh_accounts()
    
    def get_account_type_from_id(self, type_id: str) -> AccountType:
        """根据ID获取账号类型"""
        type_mapping = {
            "cursor": AccountType.CURSOR,
            "windsurf": AccountType.WINDSURF,
            "augment": AccountType.AUGMENT,
            "github_copilot": AccountType.GITHUB_COPILOT,
            "claude": AccountType.CLAUDE,
            "chatgpt": AccountType.CHATGPT,
            "openai_api": AccountType.OPENAI_API,
            "anthropic_api": AccountType.ANTHROPIC_API,
            "other": AccountType.OTHER
        }
        return type_mapping.get(type_id, AccountType.OTHER)
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 页面标题
        title_layout = QHBoxLayout()
        
        title_label = QLabel(f"{self.account_type.value} 账号管理")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 统计信息
        self.count_label = QLabel("账号数量: 0")
        self.count_label.setStyleSheet("color: #666; font-size: 14px;")
        title_layout.addWidget(self.count_label)
        
        layout.addLayout(title_layout)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        
        # 添加账号按钮
        self.add_button = QPushButton("➕ 添加账号")
        self.add_button.setObjectName("primaryButton")
        button_layout.addWidget(self.add_button)
        
        # 自动化按钮（如果支持）
        if is_automation_supported(self.account_type):
            self.auto_register_button = QPushButton("🤖 自动注册")
            self.auto_register_button.setObjectName("automationButton")
            button_layout.addWidget(self.auto_register_button)
            
            self.auto_login_button = QPushButton("🔐 自动登录")
            self.auto_login_button.setObjectName("automationButton")
            button_layout.addWidget(self.auto_login_button)
        
        button_layout.addStretch()
        
        # 编辑和删除按钮
        self.edit_button = QPushButton("✏️ 编辑")
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("🗑️ 删除")
        self.delete_button.setEnabled(False)
        self.delete_button.setObjectName("dangerButton")
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # 筛选区域
        filter_group = QGroupBox("筛选条件")
        filter_layout = QHBoxLayout(filter_group)
        
        # 搜索框
        filter_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入名称、邮箱或标签进行搜索...")
        filter_layout.addWidget(self.search_edit)
        
        # 状态筛选
        filter_layout.addWidget(QLabel("状态:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("全部", None)
        for status in AccountStatus:
            self.status_filter_combo.addItem(status.value, status)
        filter_layout.addWidget(self.status_filter_combo)
        
        filter_layout.addStretch()
        
        # 刷新按钮
        self.refresh_button = QPushButton("🔄 刷新")
        filter_layout.addWidget(self.refresh_button)
        
        layout.addWidget(filter_group)
        
        # 账号表格
        self.account_table = AccountTableWidget()
        layout.addWidget(self.account_table)
    
    def setup_connections(self):
        """设置信号连接"""
        # 按钮连接
        self.add_button.clicked.connect(self.add_account)
        self.edit_button.clicked.connect(self.edit_account)
        self.delete_button.clicked.connect(self.delete_account)
        self.refresh_button.clicked.connect(self.refresh_accounts)
        
        # 自动化按钮连接（如果存在）
        if hasattr(self, 'auto_register_button'):
            self.auto_register_button.clicked.connect(self.show_auto_register)
        if hasattr(self, 'auto_login_button'):
            self.auto_login_button.clicked.connect(self.show_auto_login)
        
        # 表格连接
        self.account_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.account_table.account_double_clicked.connect(self.edit_account_by_object)
        
        # 筛选连接
        self.search_edit.textChanged.connect(self.apply_filters)
        self.status_filter_combo.currentTextChanged.connect(self.apply_filters)
    
    def refresh_accounts(self):
        """刷新账号列表"""
        try:
            # 获取指定类型的账号
            all_accounts = self.db_manager.get_all_accounts()
            accounts = [acc for acc in all_accounts if acc.account_type == self.account_type]
            
            self.account_table.load_accounts(accounts)
            self.count_label.setText(f"账号数量: {len(accounts)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据失败: {str(e)}")
    
    def apply_filters(self):
        """应用筛选条件"""
        search_text = self.search_edit.text().strip()
        selected_status = self.status_filter_combo.currentData()
        
        try:
            # 获取所有账号
            all_accounts = self.db_manager.get_all_accounts()
            accounts = [acc for acc in all_accounts if acc.account_type == self.account_type]
            
            # 应用搜索筛选
            if search_text:
                accounts = [
                    acc for acc in accounts 
                    if search_text.lower() in acc.name.lower() 
                    or search_text.lower() in acc.email.lower()
                    or search_text.lower() in acc.tags.lower()
                ]
            
            # 应用状态筛选
            if selected_status:
                accounts = [acc for acc in accounts if acc.status == selected_status]
            
            self.account_table.load_accounts(accounts)
            self.count_label.setText(f"账号数量: {len(accounts)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"筛选数据失败: {str(e)}")
    
    def on_selection_changed(self):
        """选择变化处理"""
        has_selection = self.account_table.get_selected_account() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def add_account(self):
        """添加账号"""
        dialog = AccountDialog(parent=self)
        # 预设账号类型
        for i in range(dialog.type_combo.count()):
            if dialog.type_combo.itemData(i) == self.account_type:
                dialog.type_combo.setCurrentIndex(i)
                break
        
        if dialog.exec() == dialog.Accepted:
            account = dialog.get_account()
            try:
                account_id = self.db_manager.add_account(account)
                account.id = account_id
                self.refresh_accounts()
                QMessageBox.information(self, "成功", f"账号 '{account.name}' 添加成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加账号失败: {str(e)}")
    
    def edit_account(self):
        """编辑账号"""
        account = self.account_table.get_selected_account()
        if not account:
            return
        
        self.edit_account_by_object(account)
    
    def edit_account_by_object(self, account: Account):
        """根据账号对象编辑"""
        dialog = AccountDialog(account=account, parent=self)
        if dialog.exec() == dialog.Accepted:
            updated_account = dialog.get_account()
            try:
                self.db_manager.update_account(updated_account)
                self.refresh_accounts()
                QMessageBox.information(self, "成功", f"账号 '{updated_account.name}' 更新成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新账号失败: {str(e)}")
    
    def delete_account(self):
        """删除账号"""
        account = self.account_table.get_selected_account()
        if not account:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除账号 '{account.name}' 吗？\n\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_account(account.id)
                self.refresh_accounts()
                QMessageBox.information(self, "成功", f"账号 '{account.name}' 删除成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除账号失败: {str(e)}")
    
    def show_auto_register(self):
        """显示自动注册对话框"""
        try:
            dialog = AutomationDialog(self)
            # 预设账号类型并切换到注册选项卡
            for i in range(dialog.reg_type_combo.count()):
                if dialog.reg_type_combo.itemData(i) == self.account_type:
                    dialog.reg_type_combo.setCurrentIndex(i)
                    break
            dialog.tab_widget.setCurrentIndex(0)  # 注册选项卡
            dialog.automation_completed.connect(self.on_automation_completed)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开自动注册对话框失败: {str(e)}")
    
    def show_auto_login(self):
        """显示自动登录对话框"""
        try:
            dialog = AutomationDialog(self)
            # 预设账号类型并切换到登录选项卡
            for i in range(dialog.login_type_combo.count()):
                if dialog.login_type_combo.itemData(i) == self.account_type:
                    dialog.login_type_combo.setCurrentIndex(i)
                    break
            dialog.tab_widget.setCurrentIndex(1)  # 登录选项卡
            dialog.automation_completed.connect(self.on_automation_completed)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开自动登录对话框失败: {str(e)}")
    
    def on_automation_completed(self, result):
        """自动化完成处理"""
        if result.is_success:
            # 询问是否添加到系统
            reply = QMessageBox.question(
                self, "自动化成功", 
                f"自动化操作成功完成！\n\n是否要将此账号添加到系统中进行管理？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes and result.data:
                self.add_account_from_automation_result(result)
        
        # 刷新账号列表
        self.refresh_accounts()
    
    def add_account_from_automation_result(self, result):
        """从自动化结果添加账号"""
        try:
            dialog = AccountDialog(parent=self)
            
            # 预设账号类型
            for i in range(dialog.type_combo.count()):
                if dialog.type_combo.itemData(i) == self.account_type:
                    dialog.type_combo.setCurrentIndex(i)
                    break
            
            # 预填充信息
            if result.data:
                if 'email' in result.data:
                    dialog.email_edit.setText(result.data['email'])
                if 'password' in result.data:
                    dialog.password_edit.setText(result.data['password'])
                if 'username' in result.data:
                    dialog.username_edit.setText(result.data['username'])
            
            dialog.setWindowTitle("添加自动化创建的账号")
            
            if dialog.exec() == dialog.Accepted:
                account = dialog.get_account()
                account_id = self.db_manager.add_account(account)
                account.id = account_id
                self.refresh_accounts()
                QMessageBox.information(self, "成功", f"账号 '{account.name}' 添加成功")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加账号失败: {str(e)}")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #1565c0;
            }
            
            QPushButton#automationButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#automationButton:hover {
                background-color: #45a049;
            }
            
            QPushButton#dangerButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#dangerButton:hover {
                background-color: #d32f2f;
            }
            
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background-color: #e9ecef;
            }
            
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
                border-color: #dee2e6;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border-color: #1976d2;
            }
            
            QComboBox {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                font-size: 13px;
                min-width: 120px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                gridline-color: #f1f3f4;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
            }
        """)
