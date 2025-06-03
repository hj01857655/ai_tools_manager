"""
首页组件 - 显示整体统计和快速操作
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QGroupBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

from models.database import DatabaseManager
from models.account import AccountType, AccountStatus
from ui.automation_dialog import AutomationDialog
from automation.automation_manager import is_automation_supported


class StatCard(QFrame):
    """统计卡片组件"""
    
    clicked = Signal(str)  # 发送工具类型ID
    
    def __init__(self, title: str, count: int, icon: str, tool_id: str = None, parent=None):
        super().__init__(parent)
        self.tool_id = tool_id
        self.setup_ui(title, count, icon)
        self.apply_styles()
        
        if tool_id:
            self.setCursor(Qt.PointingHandCursor)
    
    def setup_ui(self, title: str, count: int, icon: str):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 图标和数量
        top_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        # 数量
        count_label = QLabel(str(count))
        count_label.setObjectName("cardCount")
        count_font = QFont()
        count_font.setPointSize(28)
        count_font.setBold(True)
        count_label.setFont(count_font)
        top_layout.addWidget(count_label)
        
        layout.addLayout(top_layout)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.tool_id and event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool_id)
        super().mousePressEvent(event)
    
    def apply_styles(self):
        """应用样式"""
        self.setObjectName("statCard")
        if self.tool_id:
            self.setProperty("clickable", True)


class QuickActionButton(QPushButton):
    """快速操作按钮"""
    
    def __init__(self, text: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        self.setup_ui(text, icon, description)
        self.apply_styles()
    
    def setup_ui(self, text: str, icon: str, description: str):
        """设置UI"""
        self.setFixedHeight(80)
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setObjectName("actionIcon")
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)
        
        # 文本区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # 主标题
        title_label = QLabel(text)
        title_label.setObjectName("actionTitle")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setObjectName("actionDescription")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def apply_styles(self):
        """应用样式"""
        self.setObjectName("quickActionButton")


class HomePage(QWidget):
    """首页组件"""
    
    # 信号定义
    tool_selected = Signal(str)  # 工具选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        
        self.setup_ui()
        self.apply_styles()
        self.refresh_data()
    
    def setup_ui(self):
        """设置UI"""
        # 主滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 滚动内容
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(30, 30, 30, 30)
        scroll_layout.setSpacing(30)
        
        # 欢迎标题
        self.create_welcome_section(scroll_layout)
        
        # 统计卡片
        self.create_stats_section(scroll_layout)
        
        # 快速操作
        self.create_quick_actions_section(scroll_layout)
        
        # 最近活动
        self.create_recent_activity_section(scroll_layout)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def create_welcome_section(self, layout):
        """创建欢迎区域"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        
        # 主标题
        title_label = QLabel("🚀 AI工具管理器")
        title_label.setObjectName("welcomeTitle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        welcome_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("统一管理您的AI开发工具账号")
        subtitle_label.setObjectName("welcomeSubtitle")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        welcome_layout.addWidget(subtitle_label)
        
        layout.addWidget(welcome_widget)
    
    def create_stats_section(self, layout):
        """创建统计区域"""
        stats_group = QGroupBox("📊 账号统计")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(20)
        
        # 统计卡片数据
        self.stat_cards = {}
        
        # 总计卡片
        total_card = StatCard("总账号数", 0, "📦")
        stats_layout.addWidget(total_card, 0, 0)
        self.stat_cards['total'] = total_card
        
        # Cursor卡片
        cursor_card = StatCard("Cursor", 0, "🎯", "cursor")
        cursor_card.clicked.connect(self.tool_selected.emit)
        stats_layout.addWidget(cursor_card, 0, 1)
        self.stat_cards['cursor'] = cursor_card
        
        # Windsurf卡片
        windsurf_card = StatCard("Windsurf", 0, "🏄", "windsurf")
        windsurf_card.clicked.connect(self.tool_selected.emit)
        stats_layout.addWidget(windsurf_card, 0, 2)
        self.stat_cards['windsurf'] = windsurf_card
        
        # Augment卡片
        augment_card = StatCard("Augment", 0, "⚡", "augment")
        augment_card.clicked.connect(self.tool_selected.emit)
        stats_layout.addWidget(augment_card, 0, 3)
        self.stat_cards['augment'] = augment_card
        
        # 活跃账号卡片
        active_card = StatCard("活跃账号", 0, "✅")
        stats_layout.addWidget(active_card, 1, 0)
        self.stat_cards['active'] = active_card
        
        # 过期账号卡片
        expired_card = StatCard("过期账号", 0, "⚠️")
        stats_layout.addWidget(expired_card, 1, 1)
        self.stat_cards['expired'] = expired_card
        
        # 本月新增卡片
        monthly_card = StatCard("本月新增", 0, "📈")
        stats_layout.addWidget(monthly_card, 1, 2)
        self.stat_cards['monthly'] = monthly_card
        
        # 自动化支持卡片
        auto_card = StatCard("支持自动化", 3, "🤖")
        stats_layout.addWidget(auto_card, 1, 3)
        self.stat_cards['automation'] = auto_card
        
        layout.addWidget(stats_group)
    
    def create_quick_actions_section(self, layout):
        """创建快速操作区域"""
        actions_group = QGroupBox("⚡ 快速操作")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(15)
        
        # 自动化操作
        auto_register_btn = QuickActionButton(
            "🤖 批量自动注册", "🚀", 
            "为所有支持的AI工具快速创建账号"
        )
        auto_register_btn.clicked.connect(self.show_batch_automation)
        actions_layout.addWidget(auto_register_btn)
        
        # 账号管理
        manage_btn = QuickActionButton(
            "📋 账号总览", "👁️", 
            "查看和管理所有AI工具账号"
        )
        manage_btn.clicked.connect(lambda: self.tool_selected.emit("cursor"))
        actions_layout.addWidget(manage_btn)
        
        # 数据导入导出
        import_btn = QuickActionButton(
            "📥 导入导出", "💾", 
            "批量导入或导出账号数据"
        )
        import_btn.clicked.connect(self.show_import_export)
        actions_layout.addWidget(import_btn)
        
        layout.addWidget(actions_group)
    
    def create_recent_activity_section(self, layout):
        """创建最近活动区域"""
        activity_group = QGroupBox("📅 最近活动")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_label = QLabel("暂无最近活动")
        self.activity_label.setObjectName("activityText")
        activity_layout.addWidget(self.activity_label)
        
        layout.addWidget(activity_group)
    
    def refresh_data(self):
        """刷新数据"""
        try:
            # 获取所有账号
            accounts = self.db_manager.get_all_accounts()
            
            # 统计总数
            total_count = len(accounts)
            self.stat_cards['total'].findChild(QLabel, "cardCount").setText(str(total_count))
            
            # 按工具类型统计
            cursor_count = len([acc for acc in accounts if acc.account_type == AccountType.CURSOR])
            windsurf_count = len([acc for acc in accounts if acc.account_type == AccountType.WINDSURF])
            augment_count = len([acc for acc in accounts if acc.account_type == AccountType.AUGMENT])
            
            self.stat_cards['cursor'].findChild(QLabel, "cardCount").setText(str(cursor_count))
            self.stat_cards['windsurf'].findChild(QLabel, "cardCount").setText(str(windsurf_count))
            self.stat_cards['augment'].findChild(QLabel, "cardCount").setText(str(augment_count))
            
            # 按状态统计
            active_count = len([acc for acc in accounts if acc.status == AccountStatus.ACTIVE])
            expired_count = len([acc for acc in accounts if acc.status == AccountStatus.EXPIRED])
            
            self.stat_cards['active'].findChild(QLabel, "cardCount").setText(str(active_count))
            self.stat_cards['expired'].findChild(QLabel, "cardCount").setText(str(expired_count))
            
            # 本月新增（简化统计）
            monthly_count = len([acc for acc in accounts if acc.created_at and 
                               acc.created_at.month == __import__('datetime').datetime.now().month])
            self.stat_cards['monthly'].findChild(QLabel, "cardCount").setText(str(monthly_count))
            
            # 更新活动信息
            if accounts:
                latest_account = max(accounts, key=lambda x: x.created_at or __import__('datetime').datetime.min)
                activity_text = f"最新添加: {latest_account.name} ({latest_account.account_type.value})"
                self.activity_label.setText(activity_text)
            
        except Exception as e:
            print(f"刷新数据失败: {e}")
    
    def show_batch_automation(self):
        """显示批量自动化对话框"""
        try:
            dialog = AutomationDialog(self)
            dialog.exec()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"打开自动化对话框失败: {str(e)}")
    
    def show_import_export(self):
        """显示导入导出功能"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "提示", "导入导出功能正在开发中...")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            #welcomeTitle {
                color: #1976d2;
                margin-bottom: 10px;
            }
            
            #welcomeSubtitle {
                color: #666;
                margin-bottom: 20px;
            }
            
            QFrame#statCard {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                min-height: 120px;
                max-height: 120px;
            }
            
            QFrame#statCard[clickable="true"]:hover {
                border-color: #1976d2;
                background-color: #f8f9ff;
            }
            
            #cardIcon {
                color: #1976d2;
            }
            
            #cardCount {
                color: #1976d2;
            }
            
            #cardTitle {
                color: #333;
            }
            
            QPushButton#quickActionButton {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                text-align: left;
                padding: 0;
            }
            
            QPushButton#quickActionButton:hover {
                border-color: #1976d2;
                background-color: #f8f9ff;
            }
            
            #actionIcon {
                color: #1976d2;
                margin-right: 15px;
            }
            
            #actionTitle {
                color: #333;
            }
            
            #actionDescription {
                color: #666;
                font-size: 11px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #1976d2;
            }
            
            #activityText {
                color: #666;
                padding: 10px;
            }
        """)
