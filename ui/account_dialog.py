"""
账号编辑对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QDateEdit, QGroupBox, QCheckBox,
    QMessageBox
)
from PySide6.QtCore import QDate
from datetime import datetime
from typing import Optional

from models.account import Account, AccountType, AccountStatus


class AccountDialog(QDialog):
    """账号编辑对话框"""
    
    def __init__(self, account: Optional[Account] = None, parent=None):
        super().__init__(parent)
        self.account = account
        self.is_edit_mode = account is not None
        
        self.setWindowTitle("编辑账号" if self.is_edit_mode else "添加账号")
        self.setModal(True)
        self.resize(500, 600)
        
        self.setup_ui()
        self.setup_connections()
        
        if self.is_edit_mode:
            self.load_account_data()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("账号名称（必填）")
        basic_layout.addRow("账号名称*:", self.name_edit)
        
        self.type_combo = QComboBox()
        for account_type in AccountType:
            self.type_combo.addItem(account_type.value, account_type)
        basic_layout.addRow("账号类型*:", self.type_combo)

        # 账号类型描述标签
        self.type_description_label = QLineEdit()
        self.type_description_label.setReadOnly(True)
        self.type_description_label.setStyleSheet("background-color: #f0f0f0; border: none; color: #666;")
        basic_layout.addRow("描述:", self.type_description_label)
        
        self.status_combo = QComboBox()
        for status in AccountStatus:
            self.status_combo.addItem(status.value, status)
        basic_layout.addRow("状态:", self.status_combo)
        
        layout.addWidget(basic_group)
        
        # 登录信息组
        login_group = QGroupBox("登录信息")
        login_layout = QFormLayout(login_group)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("邮箱地址")
        login_layout.addRow("邮箱:", self.email_edit)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("用户名")
        login_layout.addRow("用户名:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("密码")
        login_layout.addRow("密码:", self.password_edit)
        
        self.show_password_cb = QCheckBox("显示密码")
        login_layout.addRow("", self.show_password_cb)
        
        layout.addWidget(login_group)
        
        # API信息组
        api_group = QGroupBox("API信息")
        api_layout = QFormLayout(api_group)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("API密钥")
        api_layout.addRow("API密钥:", self.api_key_edit)
        
        self.show_api_key_cb = QCheckBox("显示API密钥")
        api_layout.addRow("", self.show_api_key_cb)
        
        layout.addWidget(api_group)
        
        # 订阅信息组
        subscription_group = QGroupBox("订阅信息")
        subscription_layout = QFormLayout(subscription_group)

        self.subscription_combo = QComboBox()
        self.subscription_combo.setEditable(True)
        subscription_layout.addRow("订阅类型:", self.subscription_combo)
        
        self.expiry_date_edit = QDateEdit()
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        subscription_layout.addRow("到期日期:", self.expiry_date_edit)
        
        self.no_expiry_cb = QCheckBox("无到期日期")
        subscription_layout.addRow("", self.no_expiry_cb)
        
        layout.addWidget(subscription_group)
        
        # 其他信息组
        other_group = QGroupBox("其他信息")
        other_layout = QFormLayout(other_group)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("标签，用逗号分隔")
        other_layout.addRow("标签:", self.tags_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("备注信息")
        self.notes_edit.setMaximumHeight(80)
        other_layout.addRow("备注:", self.notes_edit)
        
        layout.addWidget(other_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("success")
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.save_button.clicked.connect(self.save_account)
        self.cancel_button.clicked.connect(self.reject)

        self.show_password_cb.toggled.connect(self.toggle_password_visibility)
        self.show_api_key_cb.toggled.connect(self.toggle_api_key_visibility)
        self.no_expiry_cb.toggled.connect(self.toggle_expiry_date)

        # 账号类型变化处理
        self.type_combo.currentTextChanged.connect(self.on_account_type_changed)

        # 验证必填字段
        self.name_edit.textChanged.connect(self.validate_form)
        self.validate_form()

        # 初始化账号类型信息
        self.on_account_type_changed()
    
    def toggle_password_visibility(self, checked: bool):
        """切换密码可见性"""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
    
    def toggle_api_key_visibility(self, checked: bool):
        """切换API密钥可见性"""
        if checked:
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
    
    def toggle_expiry_date(self, checked: bool):
        """切换到期日期启用状态"""
        self.expiry_date_edit.setEnabled(not checked)
    
    def on_account_type_changed(self):
        """账号类型变化处理"""
        current_type = self.type_combo.currentData()
        if not current_type:
            return

        # 创建临时账号对象以获取类型信息
        temp_account = Account()
        temp_account.account_type = current_type
        type_info = temp_account.get_account_type_info()

        # 更新描述
        self.type_description_label.setText(type_info["description"])

        # 更新订阅类型选项
        self.subscription_combo.clear()
        for sub_type in type_info["subscription_types"]:
            self.subscription_combo.addItem(sub_type)

        # 根据是否需要API密钥显示/隐藏相关字段
        requires_api = type_info["requires_api_key"]
        self.api_key_edit.setVisible(requires_api)
        self.show_api_key_cb.setVisible(requires_api)

        # 更新占位符文本
        if requires_api:
            self.api_key_edit.setPlaceholderText(f"{current_type.value} API密钥")

        # 更新提示信息
        if current_type == AccountType.CURSOR:
            self.email_edit.setPlaceholderText("Cursor账号邮箱")
            self.password_edit.setPlaceholderText("Cursor账号密码")
        elif current_type == AccountType.WINDSURF:
            self.email_edit.setPlaceholderText("Windsurf账号邮箱")
            self.password_edit.setPlaceholderText("Windsurf账号密码")
        elif current_type == AccountType.AUGMENT:
            self.email_edit.setPlaceholderText("Augment账号邮箱")
            self.password_edit.setPlaceholderText("Augment账号密码")
        elif current_type == AccountType.GITHUB_COPILOT:
            self.email_edit.setPlaceholderText("GitHub邮箱")
            self.username_edit.setPlaceholderText("GitHub用户名")
            self.password_edit.setPlaceholderText("GitHub密码或Token")
        elif current_type == AccountType.CLAUDE:
            self.email_edit.setPlaceholderText("Claude账号邮箱")
            self.password_edit.setPlaceholderText("Claude账号密码")
        elif current_type == AccountType.CHATGPT:
            self.email_edit.setPlaceholderText("OpenAI账号邮箱")
            self.password_edit.setPlaceholderText("OpenAI账号密码")
        elif current_type in [AccountType.OPENAI_API, AccountType.ANTHROPIC_API]:
            self.email_edit.setPlaceholderText("注册邮箱")
            self.password_edit.setPlaceholderText("账号密码")
        else:
            self.email_edit.setPlaceholderText("邮箱地址")
            self.password_edit.setPlaceholderText("密码")

    def validate_form(self):
        """验证表单"""
        is_valid = bool(self.name_edit.text().strip())
        self.save_button.setEnabled(is_valid)
    
    def load_account_data(self):
        """加载账号数据"""
        if not self.account:
            return
        
        self.name_edit.setText(self.account.name)
        
        # 设置账号类型
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == self.account.account_type:
                self.type_combo.setCurrentIndex(i)
                break
        
        # 设置状态
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == self.account.status:
                self.status_combo.setCurrentIndex(i)
                break
        
        self.email_edit.setText(self.account.email)
        self.username_edit.setText(self.account.username)
        self.password_edit.setText(self.account.password)
        self.api_key_edit.setText(self.account.api_key)

        # 设置订阅类型
        if self.account.subscription_type:
            self.subscription_combo.setCurrentText(self.account.subscription_type)
        
        if self.account.expiry_date:
            self.expiry_date_edit.setDate(QDate.fromString(
                self.account.expiry_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
            ))
        else:
            self.no_expiry_cb.setChecked(True)
        
        self.tags_edit.setText(self.account.tags)
        self.notes_edit.setPlainText(self.account.notes)
    
    def save_account(self):
        """保存账号"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入账号名称！")
            return
        
        if not self.account:
            self.account = Account()
        
        # 更新账号信息
        self.account.name = self.name_edit.text().strip()
        self.account.account_type = self.type_combo.currentData()
        self.account.status = self.status_combo.currentData()
        self.account.email = self.email_edit.text().strip()
        self.account.username = self.username_edit.text().strip()
        self.account.password = self.password_edit.text()
        self.account.api_key = self.api_key_edit.text()
        self.account.subscription_type = self.subscription_combo.currentText().strip()
        
        if not self.no_expiry_cb.isChecked():
            expiry_date = self.expiry_date_edit.date().toPython()
            self.account.expiry_date = datetime.combine(expiry_date, datetime.min.time())
        else:
            self.account.expiry_date = None
        
        self.account.tags = self.tags_edit.text().strip()
        self.account.notes = self.notes_edit.toPlainText().strip()
        
        self.accept()
    
    def get_account(self) -> Account:
        """获取账号对象"""
        return self.account
