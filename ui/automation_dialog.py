"""
自动化注册登录对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QTextEdit,
    QMessageBox, QProgressBar, QGroupBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont
from models.account import AccountType
from automation.automation_manager import (
    get_automation_manager, AutomationResult, AutomationStatus,
    RegistrationData, LoginData
)
import os


class AutomationWorker(QThread):
    """自动化工作线程"""
    
    finished = Signal(object)  # AutomationResult
    progress = Signal(str)  # 进度消息
    
    def __init__(self, operation_type: str, account_type: AccountType, data, headless: bool = False):
        super().__init__()
        self.operation_type = operation_type  # 'register' or 'login'
        self.account_type = account_type
        self.data = data
        self.headless = headless
        self.automation_manager = get_automation_manager()
    
    def run(self):
        try:
            self.progress.emit(f"开始{self.operation_type}...")
            
            if self.operation_type == 'register':
                result = self.automation_manager.register_account(
                    self.account_type, 
                    self.data, 
                    headless=self.headless
                )
            else:  # login
                result = self.automation_manager.login_account(
                    self.account_type, 
                    self.data, 
                    headless=self.headless
                )
            
            self.finished.emit(result)
            
        except Exception as e:
            error_result = AutomationResult(
                status=AutomationStatus.UNKNOWN_ERROR,
                message=f"自动化过程中发生错误: {str(e)}"
            )
            self.finished.emit(error_result)


class AutomationDialog(QDialog):
    """自动化注册登录对话框"""
    
    automation_completed = Signal(object)  # AutomationResult
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.automation_manager = get_automation_manager()
        self.worker = None
        
        self.setWindowTitle("AI工具自动化注册登录")
        self.setFixedSize(600, 700)
        self.setModal(True)
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        self.update_supported_types()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("AI工具自动化注册登录")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 说明
        desc_label = QLabel("使用DrissionPage自动化技术，支持Cursor、Windsurf、Augment的自动注册和登录")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 注册选项卡
        register_tab = QWidget()
        self.setup_register_tab(register_tab)
        self.tab_widget.addTab(register_tab, "自动注册")
        
        # 登录选项卡
        login_tab = QWidget()
        self.setup_login_tab(login_tab)
        self.tab_widget.addTab(login_tab, "自动登录")
        
        layout.addWidget(self.tab_widget)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # 结果显示
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(150)
        self.result_text.setVisible(False)
        layout.addWidget(self.result_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("关闭")
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def setup_register_tab(self, tab):
        """设置注册选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.reg_type_combo = QComboBox()
        basic_layout.addRow("AI工具类型:", self.reg_type_combo)
        
        self.reg_email_edit = QLineEdit()
        self.reg_email_edit.setPlaceholderText("请输入邮箱地址")
        basic_layout.addRow("邮箱:", self.reg_email_edit)
        
        self.reg_password_edit = QLineEdit()
        self.reg_password_edit.setEchoMode(QLineEdit.Password)
        self.reg_password_edit.setPlaceholderText("请输入密码")
        basic_layout.addRow("密码:", self.reg_password_edit)
        
        layout.addWidget(basic_group)
        
        # 可选信息组
        optional_group = QGroupBox("可选信息")
        optional_layout = QFormLayout(optional_group)
        
        self.reg_username_edit = QLineEdit()
        self.reg_username_edit.setPlaceholderText("用户名（可选）")
        optional_layout.addRow("用户名:", self.reg_username_edit)
        
        self.reg_first_name_edit = QLineEdit()
        self.reg_first_name_edit.setPlaceholderText("名字（可选）")
        optional_layout.addRow("名字:", self.reg_first_name_edit)
        
        self.reg_last_name_edit = QLineEdit()
        self.reg_last_name_edit.setPlaceholderText("姓氏（可选）")
        optional_layout.addRow("姓氏:", self.reg_last_name_edit)
        
        self.reg_company_edit = QLineEdit()
        self.reg_company_edit.setPlaceholderText("公司（可选）")
        optional_layout.addRow("公司:", self.reg_company_edit)
        
        layout.addWidget(optional_group)
        
        # 选项
        options_layout = QHBoxLayout()
        
        self.reg_headless_cb = QCheckBox("后台运行（不显示浏览器）")
        self.reg_headless_cb.setChecked(True)
        options_layout.addWidget(self.reg_headless_cb)
        
        layout.addLayout(options_layout)
        
        # 注册按钮
        self.register_button = QPushButton("开始自动注册")
        self.register_button.setObjectName("primaryButton")
        layout.addWidget(self.register_button)
        
        layout.addStretch()
    
    def setup_login_tab(self, tab):
        """设置登录选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 登录信息组
        login_group = QGroupBox("登录信息")
        login_layout = QFormLayout(login_group)
        
        self.login_type_combo = QComboBox()
        login_layout.addRow("AI工具类型:", self.login_type_combo)
        
        self.login_email_edit = QLineEdit()
        self.login_email_edit.setPlaceholderText("请输入邮箱地址")
        login_layout.addRow("邮箱:", self.login_email_edit)
        
        self.login_password_edit = QLineEdit()
        self.login_password_edit.setEchoMode(QLineEdit.Password)
        self.login_password_edit.setPlaceholderText("请输入密码")
        login_layout.addRow("密码:", self.login_password_edit)
        
        layout.addWidget(login_group)
        
        # 选项
        options_layout = QHBoxLayout()
        
        self.login_remember_cb = QCheckBox("记住我")
        options_layout.addWidget(self.login_remember_cb)
        
        self.login_headless_cb = QCheckBox("后台运行（不显示浏览器）")
        self.login_headless_cb.setChecked(True)
        options_layout.addWidget(self.login_headless_cb)
        
        layout.addLayout(options_layout)
        
        # 登录按钮
        self.login_button = QPushButton("开始自动登录")
        self.login_button.setObjectName("primaryButton")
        layout.addWidget(self.login_button)
        
        layout.addStretch()
    
    def setup_connections(self):
        """设置信号连接"""
        self.register_button.clicked.connect(self.start_register)
        self.login_button.clicked.connect(self.start_login)
        self.close_button.clicked.connect(self.close)
    
    def update_supported_types(self):
        """更新支持的类型"""
        supported_types = self.automation_manager.get_supported_types()
        
        # 清空现有选项
        self.reg_type_combo.clear()
        self.login_type_combo.clear()
        
        # 添加支持的类型
        for account_type in supported_types:
            self.reg_type_combo.addItem(account_type.value, account_type)
            self.login_type_combo.addItem(account_type.value, account_type)
    
    def start_register(self):
        """开始自动注册"""
        # 验证输入
        if not self.validate_register_input():
            return
        
        # 准备数据
        account_type = self.reg_type_combo.currentData()
        registration_data = RegistrationData(
            email=self.reg_email_edit.text().strip(),
            password=self.reg_password_edit.text(),
            username=self.reg_username_edit.text().strip() or None,
            first_name=self.reg_first_name_edit.text().strip() or None,
            last_name=self.reg_last_name_edit.text().strip() or None,
            company=self.reg_company_edit.text().strip() or None
        )
        
        headless = self.reg_headless_cb.isChecked()
        
        # 开始自动化
        self.start_automation('register', account_type, registration_data, headless)
    
    def start_login(self):
        """开始自动登录"""
        # 验证输入
        if not self.validate_login_input():
            return
        
        # 准备数据
        account_type = self.login_type_combo.currentData()
        login_data = LoginData(
            email=self.login_email_edit.text().strip(),
            password=self.login_password_edit.text(),
            remember_me=self.login_remember_cb.isChecked()
        )
        
        headless = self.login_headless_cb.isChecked()
        
        # 开始自动化
        self.start_automation('login', account_type, login_data, headless)
    
    def start_automation(self, operation_type: str, account_type: AccountType, data, headless: bool):
        """开始自动化操作"""
        # 禁用按钮
        self.register_button.setEnabled(False)
        self.login_button.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 隐藏结果
        self.result_text.setVisible(False)
        
        # 创建工作线程
        self.worker = AutomationWorker(operation_type, account_type, data, headless)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_automation_finished)
        self.worker.start()
    
    def update_progress(self, message: str):
        """更新进度"""
        self.status_label.setText(message)
    
    def on_automation_finished(self, result: AutomationResult):
        """自动化完成"""
        # 启用按钮
        self.register_button.setEnabled(True)
        self.login_button.setEnabled(True)
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 显示结果
        self.show_result(result)
        
        # 发送信号
        self.automation_completed.emit(result)
        
        # 清理工作线程
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def show_result(self, result: AutomationResult):
        """显示结果"""
        self.result_text.setVisible(True)
        
        # 设置状态颜色
        if result.is_success:
            self.status_label.setText("✅ 操作成功")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif result.needs_manual_intervention:
            self.status_label.setText("⚠️ 需要手动干预")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.status_label.setText("❌ 操作失败")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # 显示详细信息
        result_text = f"状态: {result.status.value}\n"
        result_text += f"消息: {result.message}\n"
        
        if result.data:
            result_text += f"数据: {result.data}\n"
        
        if result.screenshot_path and os.path.exists(result.screenshot_path):
            result_text += f"截图: {result.screenshot_path}\n"
        
        self.result_text.setPlainText(result_text)
    
    def validate_register_input(self) -> bool:
        """验证注册输入"""
        if not self.reg_email_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入邮箱地址！")
            return False
        
        if not self.reg_password_edit.text():
            QMessageBox.warning(self, "警告", "请输入密码！")
            return False
        
        return True
    
    def validate_login_input(self) -> bool:
        """验证登录输入"""
        if not self.login_email_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入邮箱地址！")
            return False
        
        if not self.login_password_edit.text():
            QMessageBox.warning(self, "警告", "请输入密码！")
            return False
        
        return True
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1976d2;
            }
            QPushButton#primaryButton {
                padding: 12px;
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background-color: #1565c0;
            }
            QPushButton#primaryButton:disabled {
                background-color: #ccc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1976d2;
            }
        """)
