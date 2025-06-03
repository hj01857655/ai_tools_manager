"""
侧边导航栏组件
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SidebarNavigation(QWidget):
    """侧边导航栏组件"""
    
    # 信号定义
    page_changed = Signal(str)  # 页面切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = None
        self.nav_buttons = {}
        
        self.setup_ui()
        self.apply_styles()
        
        # 默认选择首页
        self.select_page("home")
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题区域
        header_widget = QWidget()
        header_widget.setObjectName("sidebarHeader")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 15)
        
        # 应用标题
        title_label = QLabel("AI工具管理器")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setObjectName("appTitle")
        header_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("管理您的AI开发工具账号")
        subtitle_label.setObjectName("appSubtitle")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_widget)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        layout.addWidget(separator)
        
        # 导航区域
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        nav_scroll.setObjectName("navScrollArea")
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)
        
        # 首页
        self.add_category_header(nav_layout, "🏠 概览")

        # 首页
        home_btn = self.create_nav_button(
            "home", "首页", "账号统计和快速操作", "🏠"
        )
        nav_layout.addWidget(home_btn)

        # AI编程助手分组
        self.add_category_header(nav_layout, "🤖 AI编程助手")

        # Cursor
        cursor_btn = self.create_nav_button(
            "cursor", "Cursor", "AI驱动的代码编辑器", "🎯"
        )
        nav_layout.addWidget(cursor_btn)

        # Windsurf
        windsurf_btn = self.create_nav_button(
            "windsurf", "Windsurf", "AI代码编辑器和开发环境", "🏄"
        )
        nav_layout.addWidget(windsurf_btn)

        # Augment
        augment_btn = self.create_nav_button(
            "augment", "Augment", "AI代码补全和开发工具", "⚡"
        )
        nav_layout.addWidget(augment_btn)

        # 系统功能分组
        self.add_category_header(nav_layout, "🔧 系统")

        # 日志页面
        logs_btn = self.create_nav_button(
            "logs", "日志", "查看系统日志和操作记录", "📋"
        )
        nav_layout.addWidget(logs_btn)

        # 设置页面
        settings_btn = self.create_nav_button(
            "settings", "设置", "应用程序配置和偏好设置", "⚙️"
        )
        nav_layout.addWidget(settings_btn)

        # 弹性空间
        nav_layout.addStretch()
        
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll)
        
        # 底部信息
        footer_widget = QWidget()
        footer_widget.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(20, 15, 20, 20)
        
        version_label = QLabel("版本 1.0.0")
        version_label.setObjectName("versionLabel")
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer_widget)
    
    def add_category_header(self, layout, title):
        """添加分类标题"""
        header_label = QLabel(title)
        header_label.setObjectName("categoryHeader")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(11)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
    
    def create_nav_button(self, page_id, title, description, icon):
        """创建导航按钮"""
        button = QPushButton()
        button.setObjectName("navButton")
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setFixedHeight(70)
        
        # 创建按钮内容
        button_layout = QHBoxLayout(button)
        button_layout.setContentsMargins(15, 10, 15, 10)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setObjectName("navIcon")
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        button_layout.addWidget(icon_label)
        
        # 文本区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setObjectName("navTitle")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setObjectName("navDescription")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        button_layout.addLayout(text_layout)
        button_layout.addStretch()
        
        # 连接信号
        button.clicked.connect(lambda: self.select_page(page_id))
        
        # 保存按钮引用
        self.nav_buttons[page_id] = button
        
        return button
    
    def select_page(self, page_id):
        """选择页面"""
        if self.current_page == page_id:
            return
        
        # 更新按钮状态
        for btn_id, button in self.nav_buttons.items():
            if btn_id == page_id:
                button.setProperty("selected", True)
            else:
                button.setProperty("selected", False)
            button.style().unpolish(button)
            button.style().polish(button)
        
        self.current_page = page_id
        self.page_changed.emit(page_id)
    
    def get_current_page(self):
        """获取当前页面"""
        return self.current_page

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            SidebarNavigation {
                background-color: #f8f9fa;
                border-right: 1px solid #e9ecef;
                min-width: 280px;
                max-width: 280px;
            }

            #sidebarHeader {
                background-color: #1976d2;
                color: white;
            }

            #appTitle {
                color: white;
                margin-bottom: 5px;
            }

            #appSubtitle {
                color: #e3f2fd;
                font-size: 12px;
            }

            #separator {
                background-color: #e9ecef;
                border: none;
                height: 1px;
            }

            #navScrollArea {
                background-color: transparent;
                border: none;
            }

            #categoryHeader {
                color: #6c757d;
                margin: 15px 0 8px 10px;
                font-weight: bold;
            }

            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                margin: 2px 5px;
                text-align: left;
                padding: 0;
            }

            QPushButton#navButton:hover {
                background-color: #e9ecef;
            }

            QPushButton#navButton[selected="true"] {
                background-color: #1976d2;
                color: white;
            }

            QPushButton#navButton[selected="true"] #navTitle {
                color: white;
            }

            QPushButton#navButton[selected="true"] #navDescription {
                color: #e3f2fd;
            }

            QPushButton#navButton[selected="true"] #navIcon {
                color: white;
            }

            #navIcon {
                color: #1976d2;
                margin-right: 10px;
            }

            #navTitle {
                color: #212529;
                margin-bottom: 2px;
            }

            #navDescription {
                color: #6c757d;
                font-size: 11px;
            }

            #sidebarFooter {
                background-color: #f1f3f4;
                border-top: 1px solid #e9ecef;
            }

            #versionLabel {
                color: #6c757d;
                font-size: 11px;
            }
        """)
