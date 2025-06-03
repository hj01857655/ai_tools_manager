"""
登录对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QMessageBox,
    QTabWidget, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from utils.session import get_session_manager
from models.database import DatabaseManager
from models.user import User, UserRole
import re


class LoginDialog(QDialog):
    """登录对话框"""
    
    login_successful = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_manager = get_session_manager()
        self.db_manager = DatabaseManager()
        
        self.setWindowTitle("AI工具管理器 - 登录")
        self.setFixedSize(400, 500)
        self.setModal(True)
        
        # 检查是否需要创建默认管理员
        self.check_and_create_default_admin()
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
    
    def check_and_create_default_admin(self):
        """检查并创建默认管理员"""
        users = self.db_manager.get_all_users()
        if not users:
            self.session_manager.create_default_admin()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("AI工具管理器")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("安全管理您的AI开发工具账号")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 登录选项卡
        login_tab = QWidget()
        self.setup_login_tab(login_tab)
        self.tab_widget.addTab(login_tab, "登录")
        
        # 注册选项卡
        register_tab = QWidget()
        self.setup_register_tab(register_tab)
        self.tab_widget.addTab(register_tab, "注册")
        
        layout.addWidget(self.tab_widget)
        
        # 底部信息
        info_label = QLabel("首次使用？默认管理员账号：admin / admin123")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 10px;")
        layout.addWidget(info_label)
    
    def setup_login_tab(self, tab):
        """设置登录选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 登录表单
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # 记住密码
        self.remember_checkbox = QCheckBox("记住密码")
        layout.addWidget(self.remember_checkbox)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setDefault(True)
        layout.addWidget(self.login_button)
        
        layout.addStretch()
    
    def setup_register_tab(self, tab):
        """设置注册选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 注册表单
        form_layout = QFormLayout()
        
        self.reg_username_edit = QLineEdit()
        self.reg_username_edit.setPlaceholderText("3-20个字符，字母数字下划线")
        form_layout.addRow("用户名:", self.reg_username_edit)
        
        self.reg_email_edit = QLineEdit()
        self.reg_email_edit.setPlaceholderText("请输入邮箱地址")
        form_layout.addRow("邮箱:", self.reg_email_edit)
        
        self.reg_password_edit = QLineEdit()
        self.reg_password_edit.setPlaceholderText("至少6个字符")
        self.reg_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.reg_password_edit)
        
        self.reg_confirm_edit = QLineEdit()
        self.reg_confirm_edit.setPlaceholderText("请再次输入密码")
        self.reg_confirm_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("确认密码:", self.reg_confirm_edit)
        
        layout.addLayout(form_layout)
        
        # 密码强度提示
        self.password_strength_label = QLabel("")
        self.password_strength_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.password_strength_label)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        layout.addWidget(self.register_button)
        
        layout.addStretch()
    
    def setup_connections(self):
        """设置信号连接"""
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)
        self.password_edit.returnPressed.connect(self.handle_login)
        self.reg_confirm_edit.returnPressed.connect(self.handle_register)
        self.reg_password_edit.textChanged.connect(self.check_password_strength)
    
    def handle_login(self):
        """处理登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码！")
            return
        
        if self.session_manager.login(username, password):
            self.login_successful.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误，或账号已被禁用！")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def handle_register(self):
        """处理注册"""
        username = self.reg_username_edit.text().strip()
        email = self.reg_email_edit.text().strip()
        password = self.reg_password_edit.text()
        confirm = self.reg_confirm_edit.text()
        
        # 验证输入
        if not self.validate_register_input(username, email, password, confirm):
            return
        
        # 检查用户名是否已存在
        if self.db_manager.get_user_by_username(username):
            QMessageBox.warning(self, "注册失败", "用户名已存在！")
            return
        
        # 检查邮箱是否已存在
        if self.db_manager.get_user_by_email(email):
            QMessageBox.warning(self, "注册失败", "邮箱已被注册！")
            return
        
        # 创建用户
        user = User()
        user.username = username
        user.email = email
        user.role = UserRole.USER
        user.set_password(password)
        
        try:
            user_id = self.db_manager.add_user(user)
            if user_id > 0:
                QMessageBox.information(self, "注册成功", "账号注册成功！请使用新账号登录。")
                self.tab_widget.setCurrentIndex(0)  # 切换到登录选项卡
                self.username_edit.setText(username)
                self.clear_register_form()
            else:
                QMessageBox.critical(self, "注册失败", "注册失败，请稍后重试！")
        except Exception as e:
            QMessageBox.critical(self, "注册失败", f"注册失败：{str(e)}")
    
    def validate_register_input(self, username: str, email: str, password: str, confirm: str) -> bool:
        """验证注册输入"""
        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "警告", "请填写所有字段！")
            return False
        
        # 验证用户名
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            QMessageBox.warning(self, "警告", "用户名必须是3-20个字符，只能包含字母、数字和下划线！")
            return False
        
        # 验证邮箱
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            QMessageBox.warning(self, "警告", "请输入有效的邮箱地址！")
            return False
        
        # 验证密码
        if len(password) < 6:
            QMessageBox.warning(self, "警告", "密码至少需要6个字符！")
            return False
        
        # 验证密码确认
        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致！")
            return False
        
        return True
    
    def check_password_strength(self):
        """检查密码强度"""
        password = self.reg_password_edit.text()
        
        if len(password) == 0:
            self.password_strength_label.setText("")
            return
        
        strength = 0
        feedback = []
        
        if len(password) >= 6:
            strength += 1
        else:
            feedback.append("至少6个字符")
        
        if re.search(r'[a-z]', password):
            strength += 1
        else:
            feedback.append("包含小写字母")
        
        if re.search(r'[A-Z]', password):
            strength += 1
        else:
            feedback.append("包含大写字母")
        
        if re.search(r'\d', password):
            strength += 1
        else:
            feedback.append("包含数字")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength += 1
        else:
            feedback.append("包含特殊字符")
        
        if strength <= 2:
            self.password_strength_label.setText("密码强度: 弱")
            self.password_strength_label.setStyleSheet("color: red; font-size: 12px;")
        elif strength <= 3:
            self.password_strength_label.setText("密码强度: 中等")
            self.password_strength_label.setStyleSheet("color: orange; font-size: 12px;")
        else:
            self.password_strength_label.setText("密码强度: 强")
            self.password_strength_label.setStyleSheet("color: green; font-size: 12px;")
    
    def clear_register_form(self):
        """清空注册表单"""
        self.reg_username_edit.clear()
        self.reg_email_edit.clear()
        self.reg_password_edit.clear()
        self.reg_confirm_edit.clear()
        self.password_strength_label.clear()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1976d2;
            }
            QPushButton {
                padding: 12px;
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
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
