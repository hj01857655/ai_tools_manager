"""
导航栏组件
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QMenu, QFrame, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from utils.session import get_session_manager
from models.user import UserRole


class NavigationBar(QWidget):
    """导航栏组件"""
    
    # 信号定义
    add_account_clicked = Signal()
    import_accounts_clicked = Signal()
    export_accounts_clicked = Signal()
    automation_clicked = Signal()
    settings_clicked = Signal()
    about_clicked = Signal()
    logout_clicked = Signal()
    refresh_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_manager = get_session_manager()
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        self.update_user_info()
    
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # 左侧：应用标题和快捷操作
        left_layout = QHBoxLayout()
        
        # 应用标题
        title_label = QLabel("AI工具管理器")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1976d2; margin-right: 20px;")
        left_layout.addWidget(title_label)
        
        # 分隔线
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("color: #ddd;")
        left_layout.addWidget(separator1)
        
        # 快捷操作按钮
        self.add_button = QPushButton("添加账号")
        self.add_button.setObjectName("actionButton")
        left_layout.addWidget(self.add_button)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setObjectName("actionButton")
        left_layout.addWidget(self.refresh_button)
        
        # 更多操作菜单
        self.more_button = QPushButton("更多操作")
        self.more_button.setObjectName("actionButton")
        self.setup_more_menu()
        left_layout.addWidget(self.more_button)
        
        layout.addLayout(left_layout)
        
        # 中间：弹性空间
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        # 右侧：用户信息和操作
        right_layout = QHBoxLayout()
        
        # 用户信息
        self.user_info_layout = QVBoxLayout()
        self.user_info_layout.setSpacing(2)
        
        self.username_label = QLabel("未登录")
        self.username_label.setAlignment(Qt.AlignRight)
        username_font = QFont()
        username_font.setBold(True)
        self.username_label.setFont(username_font)
        self.user_info_layout.addWidget(self.username_label)
        
        self.role_label = QLabel("")
        self.role_label.setAlignment(Qt.AlignRight)
        self.role_label.setStyleSheet("color: #666; font-size: 12px;")
        self.user_info_layout.addWidget(self.role_label)
        
        right_layout.addLayout(self.user_info_layout)
        
        # 分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("color: #ddd; margin: 0 10px;")
        right_layout.addWidget(separator2)
        
        # 用户操作菜单
        self.user_button = QPushButton("用户")
        self.user_button.setObjectName("userButton")
        self.setup_user_menu()
        right_layout.addWidget(self.user_button)
        
        layout.addLayout(right_layout)
    
    def setup_more_menu(self):
        """设置更多操作菜单"""
        self.more_menu = QMenu(self)

        # 自动化功能
        automation_action = self.more_menu.addAction("🤖 自动化注册登录")
        automation_action.triggered.connect(self.automation_clicked.emit)

        self.more_menu.addSeparator()

        import_action = self.more_menu.addAction("导入账号")
        import_action.triggered.connect(self.import_accounts_clicked.emit)

        export_action = self.more_menu.addAction("导出账号")
        export_action.triggered.connect(self.export_accounts_clicked.emit)

        self.more_menu.addSeparator()

        settings_action = self.more_menu.addAction("设置")
        settings_action.triggered.connect(self.settings_clicked.emit)

        about_action = self.more_menu.addAction("关于")
        about_action.triggered.connect(self.about_clicked.emit)

        self.more_button.setMenu(self.more_menu)
    
    def setup_user_menu(self):
        """设置用户菜单"""
        self.user_menu = QMenu(self)
        
        # 根据用户角色显示不同菜单项
        current_user = self.session_manager.get_current_user()
        if current_user and current_user.role == UserRole.ADMIN:
            user_mgmt_action = self.user_menu.addAction("用户管理")
            user_mgmt_action.triggered.connect(self.show_user_management)
            self.user_menu.addSeparator()
        
        profile_action = self.user_menu.addAction("个人资料")
        profile_action.triggered.connect(self.show_profile)
        
        change_password_action = self.user_menu.addAction("修改密码")
        change_password_action.triggered.connect(self.show_change_password)
        
        self.user_menu.addSeparator()
        
        logout_action = self.user_menu.addAction("退出登录")
        logout_action.triggered.connect(self.handle_logout)
        
        self.user_button.setMenu(self.user_menu)
    
    def setup_connections(self):
        """设置信号连接"""
        self.add_button.clicked.connect(self.add_account_clicked.emit)
        self.refresh_button.clicked.connect(self.refresh_clicked.emit)
    
    def update_user_info(self):
        """更新用户信息显示"""
        current_user = self.session_manager.get_current_user()
        if current_user:
            self.username_label.setText(current_user.username)
            role_text = current_user.role.value
            if current_user.role == UserRole.ADMIN:
                role_text += " 👑"
            self.role_label.setText(role_text)
        else:
            self.username_label.setText("未登录")
            self.role_label.setText("")
        
        # 重新设置用户菜单
        self.setup_user_menu()
    
    def show_user_management(self):
        """显示用户管理"""
        # TODO: 实现用户管理界面
        QMessageBox.information(self, "提示", "用户管理功能正在开发中...")
    
    def show_profile(self):
        """显示个人资料"""
        # TODO: 实现个人资料界面
        QMessageBox.information(self, "提示", "个人资料功能正在开发中...")
    
    def show_change_password(self):
        """显示修改密码"""
        # TODO: 实现修改密码界面
        QMessageBox.information(self, "提示", "修改密码功能正在开发中...")
    
    def handle_logout(self):
        """处理退出登录"""
        reply = QMessageBox.question(
            self, "确认退出", 
            "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session_manager.logout()
            self.logout_clicked.emit()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            NavigationBar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
                min-height: 60px;
                max-height: 60px;
            }
            
            QPushButton#actionButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                color: #495057;
                min-width: 80px;
            }
            
            QPushButton#actionButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            
            QPushButton#actionButton:pressed {
                background-color: #dee2e6;
            }
            
            QPushButton#userButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                min-width: 60px;
            }
            
            QPushButton#userButton:hover {
                background-color: #1565c0;
            }
            
            QPushButton#userButton:pressed {
                background-color: #0d47a1;
            }
            
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px 0;
            }
            
            QMenu::item {
                padding: 8px 20px;
                color: #333;
            }
            
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: #eee;
                margin: 5px 0;
            }
        """)
    
    def refresh_user_info(self):
        """刷新用户信息（外部调用）"""
        self.update_user_info()
