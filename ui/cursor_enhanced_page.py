"""
增强的Cursor页面 - 包含详细功能和信息
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QFrame, QScrollArea, QGridLayout,
    QTabWidget, QListWidget, QListWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from models.account import AccountType
from ui.account_page import AccountPage
from utils.logger import get_logger


class CursorInfoWidget(QFrame):
    """Cursor信息展示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🎯 Cursor - AI驱动的代码编辑器")
        title_label.setObjectName("cursorTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel("Cursor是一款革命性的AI代码编辑器，集成了先进的人工智能技术，为开发者提供智能代码补全、重构建议和实时协作功能。")
        desc_label.setWordWrap(True)
        desc_label.setObjectName("cursorDesc")
        layout.addWidget(desc_label)
        
        # 功能特性
        features_group = QGroupBox("✨ 主要特性")
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "🤖 AI智能代码补全 - 基于上下文的智能建议",
            "🔄 实时代码重构 - 自动优化代码结构",
            "💬 AI对话编程 - 与AI助手直接对话编程",
            "🔍 智能错误检测 - 提前发现潜在问题",
            "📚 代码解释功能 - AI解释复杂代码逻辑",
            "🚀 快速原型开发 - 加速开发流程",
            "🔗 Git集成 - 无缝版本控制",
            "🎨 自定义主题 - 个性化编辑环境"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setObjectName("featureItem")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_group)
        
        # 官方链接
        links_group = QGroupBox("🔗 官方链接")
        links_layout = QGridLayout(links_group)
        
        # 主页链接
        homepage_btn = QPushButton("🏠 官方主页")
        homepage_btn.setObjectName("linkButton")
        homepage_btn.clicked.connect(lambda: self.open_url("https://www.cursor.com/"))
        links_layout.addWidget(homepage_btn, 0, 0)
        
        # 注册链接
        register_btn = QPushButton("📝 注册账号")
        register_btn.setObjectName("linkButton")
        register_btn.clicked.connect(lambda: self.open_url("https://authenticator.cursor.sh/sign-up"))
        links_layout.addWidget(register_btn, 0, 1)

        # 自动注册按钮
        auto_register_btn = QPushButton("🤖 自动注册")
        auto_register_btn.setObjectName("primaryButton")
        auto_register_btn.clicked.connect(self.start_auto_register)
        links_layout.addWidget(auto_register_btn, 0, 2)
        
        # 登录链接
        login_btn = QPushButton("🔐 登录账号")
        login_btn.setObjectName("linkButton")
        login_btn.clicked.connect(lambda: self.open_url("https://www.cursor.com/api/auth/login"))
        links_layout.addWidget(login_btn, 1, 0)
        
        # 文档链接
        docs_btn = QPushButton("📖 使用文档")
        docs_btn.setObjectName("linkButton")
        docs_btn.clicked.connect(lambda: self.open_url("https://docs.cursor.com/"))
        links_layout.addWidget(docs_btn, 1, 1)
        
        layout.addWidget(links_group)
        
        layout.addStretch()
    
    def open_url(self, url: str):
        """打开URL"""
        try:
            import webbrowser
            webbrowser.open(url)

            # 记录日志
            logger = get_logger()
            logger.info(f"打开Cursor链接: {url}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开链接: {str(e)}")

    def start_auto_register(self):
        """开始自动注册"""
        try:
            from automation.cursor_automation import CursorAutomation
            from utils.config import get_config_manager

            # 获取配置
            config_manager = get_config_manager()
            domain = config_manager.get('cursor.domain', 'hjj0185.email')
            pin = config_manager.get('cursor.pin', '')

            logger = get_logger()
            logger.info("🤖 开始Cursor自动注册")

            # 创建自动化实例
            cursor_automation = CursorAutomation()

            # 执行自动注册
            result = cursor_automation.register_with_generated_account(
                domain=domain,
                include_pin=bool(pin),
                pin=pin,
                headless=False  # 可视模式
            )

            # 处理结果
            if result.status.name in ['SUCCESS', 'EMAIL_VERIFICATION_REQUIRED']:
                if result.data and 'generated_account' in result.data:
                    account_data = result.data['generated_account']
                    message = f"✅ 自动注册成功！\n\n"
                    message += f"邮箱: {account_data['email']}\n"
                    message += f"密码: {account_data['password']}\n"
                    message += f"姓名: {account_data['first_name']} {account_data['last_name']}\n"
                    if account_data.get('pin'):
                        message += f"PIN: {account_data['pin']}\n"

                    if result.status.name == 'EMAIL_VERIFICATION_REQUIRED':
                        message += f"\n📧 需要邮箱验证，请检查邮箱并点击验证链接"

                    QMessageBox.information(self, "自动注册成功", message)
                    logger.info(f"✅ Cursor自动注册成功: {account_data['email']}")
                else:
                    QMessageBox.information(self, "注册成功", result.message)
            else:
                QMessageBox.warning(self, "注册失败", f"自动注册失败: {result.message}")
                logger.error(f"❌ Cursor自动注册失败: {result.message}")

        except Exception as e:
            error_msg = f"自动注册异常: {str(e)}"
            logger = get_logger()
            logger.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
            }
            
            #cursorTitle {
                color: #1976d2;
                margin-bottom: 10px;
            }
            
            #cursorDesc {
                color: #666;
                line-height: 1.5;
                margin-bottom: 15px;
            }
            
            #featureItem {
                color: #333;
                padding: 5px 0;
                font-size: 13px;
            }
            
            QPushButton#linkButton {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                text-align: left;
            }
            
            QPushButton#linkButton:hover {
                background-color: #e9ecef;
                border-color: #1976d2;
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
        """)


class CursorStatsWidget(QFrame):
    """Cursor统计信息组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_styles()
        self.update_stats()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("📊 Cursor账号统计")
        title_label.setObjectName("statsTitle")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 统计卡片网格
        stats_layout = QGridLayout()
        
        # 总账号数
        self.total_card = self.create_stat_card("总账号", "0", "#1976d2")
        stats_layout.addWidget(self.total_card, 0, 0)
        
        # 活跃账号
        self.active_card = self.create_stat_card("活跃账号", "0", "#4caf50")
        stats_layout.addWidget(self.active_card, 0, 1)
        
        # 过期账号
        self.expired_card = self.create_stat_card("过期账号", "0", "#f44336")
        stats_layout.addWidget(self.expired_card, 1, 0)
        
        # 本月新增
        self.monthly_card = self.create_stat_card("本月新增", "0", "#ff9800")
        stats_layout.addWidget(self.monthly_card, 1, 1)
        
        layout.addLayout(stats_layout)
        
        # 最近活动
        activity_group = QGroupBox("📅 最近活动")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(150)
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        layout.addStretch()
    
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """创建统计卡片"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 数值
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        layout.addWidget(title_label)
        
        return card
    
    def update_stats(self):
        """更新统计信息"""
        try:
            from models.database import DatabaseManager
            from models.account import AccountStatus
            from datetime import datetime
            
            db_manager = DatabaseManager()
            accounts = db_manager.get_all_accounts()
            cursor_accounts = [acc for acc in accounts if acc.account_type == AccountType.CURSOR]
            
            # 更新统计
            total_count = len(cursor_accounts)
            active_count = len([acc for acc in cursor_accounts if acc.status == AccountStatus.ACTIVE])
            expired_count = len([acc for acc in cursor_accounts if acc.status == AccountStatus.EXPIRED])
            
            # 本月新增
            current_month = datetime.now().month
            monthly_count = len([acc for acc in cursor_accounts if acc.created_at and 
                               acc.created_at.month == current_month])
            
            # 更新卡片
            self.total_card.findChild(QLabel, "statValue").setText(str(total_count))
            self.active_card.findChild(QLabel, "statValue").setText(str(active_count))
            self.expired_card.findChild(QLabel, "statValue").setText(str(expired_count))
            self.monthly_card.findChild(QLabel, "statValue").setText(str(monthly_count))
            
            # 更新活动列表
            self.activity_list.clear()
            recent_accounts = sorted(cursor_accounts, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
            
            for account in recent_accounts:
                item_text = f"📝 {account.name} - {account.email}"
                if account.created_at:
                    item_text += f" ({account.created_at.strftime('%m-%d %H:%M')})"
                
                item = QListWidgetItem(item_text)
                if account.status == AccountStatus.ACTIVE:
                    item.setForeground(QColor("#4caf50"))
                elif account.status == AccountStatus.EXPIRED:
                    item.setForeground(QColor("#f44336"))
                else:
                    item.setForeground(QColor("#ff9800"))
                
                self.activity_list.addItem(item)
            
            if not recent_accounts:
                item = QListWidgetItem("暂无Cursor账号")
                item.setForeground(QColor("#999"))
                self.activity_list.addItem(item)
                
        except Exception as e:
            logger = get_logger()
            logger.error(f"更新Cursor统计失败: {e}")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
            }
            
            #statsTitle {
                color: #1976d2;
                margin-bottom: 15px;
            }
            
            QFrame#statCard {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
            
            #statTitle {
                color: #666;
                font-size: 12px;
            }
            
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QListWidget::item:hover {
                background-color: #f5f5f5;
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
        """)


class CursorEnhancedPage(QWidget):
    """增强的Cursor页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.account_type = AccountType.CURSOR
        self.account_type_id = "cursor"
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 账号管理标签页
        self.account_page = AccountPage("cursor")
        self.tab_widget.addTab(self.account_page, "📋 账号管理")
        
        # Cursor信息标签页
        info_scroll = QScrollArea()
        info_scroll.setWidgetResizable(True)
        info_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        info_widget = CursorInfoWidget()
        info_scroll.setWidget(info_widget)
        self.tab_widget.addTab(info_scroll, "ℹ️ 产品信息")
        
        # 统计信息标签页
        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.stats_widget = CursorStatsWidget()
        stats_scroll.setWidget(self.stats_widget)
        self.tab_widget.addTab(stats_scroll, "📊 统计信息")
        
        layout.addWidget(self.tab_widget)
        
        # 应用样式
        self.apply_styles()
    
    def setup_timer(self):
        """设置定时器"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(30000)  # 30秒刷新一次
    
    def refresh_accounts(self):
        """刷新账号数据"""
        self.account_page.refresh_accounts()
        self.refresh_stats()
    
    def refresh_stats(self):
        """刷新统计信息"""
        try:
            self.stats_widget.update_stats()
        except Exception as e:
            logger = get_logger()
            logger.error(f"刷新Cursor统计失败: {e}")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #f5f5f5;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid white;
                color: #1976d2;
            }
            
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
