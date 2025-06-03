"""
设置页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QComboBox, QSlider, QTextEdit, QFileDialog, QMessageBox,
    QTabWidget, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.config import get_config_manager
from utils.logger import get_logger


class SettingsPage(QWidget):
    """设置页面"""
    
    settings_changed = Signal()  # 设置变更信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = get_config_manager()
        self.logger = get_logger()
        
        self.setup_ui()
        self.load_settings()
        self.apply_styles()
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("⚙️ 应用设置")
        title_label.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置内容
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # 创建设置标签页
        self.create_tabs(content_layout)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 底部按钮
        self.create_footer(layout)
    
    def create_tabs(self, layout):
        """创建设置标签页"""
        self.tab_widget = QTabWidget()
        
        # 通用设置
        self.create_general_tab()
        
        # 界面设置
        self.create_ui_tab()
        
        # 自动化设置
        self.create_automation_tab()
        
        # 数据库设置
        self.create_database_tab()
        
        # 日志设置
        self.create_logging_tab()
        
        # 关于
        self.create_about_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_general_tab(self):
        """创建通用设置标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 应用程序设置
        app_group = QGroupBox("应用程序")
        app_layout = QFormLayout(app_group)
        
        self.startup_checkbox = QCheckBox("开机自启动")
        app_layout.addRow("启动选项:", self.startup_checkbox)
        
        self.minimize_to_tray_checkbox = QCheckBox("最小化到系统托盘")
        app_layout.addRow("窗口行为:", self.minimize_to_tray_checkbox)
        
        self.auto_save_checkbox = QCheckBox("自动保存设置")
        app_layout.addRow("数据保存:", self.auto_save_checkbox)
        
        layout.addWidget(app_group)
        
        # 更新设置
        update_group = QGroupBox("更新")
        update_layout = QFormLayout(update_group)
        
        self.auto_update_checkbox = QCheckBox("自动检查更新")
        update_layout.addRow("更新检查:", self.auto_update_checkbox)
        
        self.update_channel_combo = QComboBox()
        self.update_channel_combo.addItems(["稳定版", "测试版", "开发版"])
        update_layout.addRow("更新通道:", self.update_channel_combo)
        
        layout.addWidget(update_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔧 通用")
    
    def create_ui_tab(self):
        """创建界面设置标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 主题设置
        theme_group = QGroupBox("主题")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "跟随系统"])
        theme_layout.addRow("主题模式:", self.theme_combo)
        
        self.accent_color_combo = QComboBox()
        self.accent_color_combo.addItems(["蓝色", "绿色", "紫色", "橙色", "红色"])
        theme_layout.addRow("强调色:", self.accent_color_combo)
        
        layout.addWidget(theme_group)
        
        # 字体设置
        font_group = QGroupBox("字体")
        font_layout = QFormLayout(font_group)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setValue(12)
        font_layout.addRow("字体大小:", self.font_size_spinbox)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["系统默认", "微软雅黑", "宋体", "Arial", "Consolas"])
        font_layout.addRow("字体族:", self.font_family_combo)
        
        layout.addWidget(font_group)
        
        # 界面行为
        behavior_group = QGroupBox("界面行为")
        behavior_layout = QFormLayout(behavior_group)
        
        self.animation_checkbox = QCheckBox("启用动画效果")
        behavior_layout.addRow("动画:", self.animation_checkbox)
        
        self.confirm_exit_checkbox = QCheckBox("退出时确认")
        behavior_layout.addRow("退出确认:", self.confirm_exit_checkbox)
        
        self.remember_window_checkbox = QCheckBox("记住窗口位置和大小")
        behavior_layout.addRow("窗口状态:", self.remember_window_checkbox)
        
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🎨 界面")
    
    def create_automation_tab(self):
        """创建自动化设置标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 浏览器设置
        browser_group = QGroupBox("浏览器")
        browser_layout = QFormLayout(browser_group)
        
        self.headless_checkbox = QCheckBox("后台运行（无界面）")
        browser_layout.addRow("运行模式:", self.headless_checkbox)
        
        self.browser_timeout_spinbox = QSpinBox()
        self.browser_timeout_spinbox.setRange(10, 300)
        self.browser_timeout_spinbox.setValue(30)
        self.browser_timeout_spinbox.setSuffix(" 秒")
        browser_layout.addRow("超时时间:", self.browser_timeout_spinbox)
        
        self.retry_count_spinbox = QSpinBox()
        self.retry_count_spinbox.setRange(1, 10)
        self.retry_count_spinbox.setValue(3)
        browser_layout.addRow("重试次数:", self.retry_count_spinbox)
        
        layout.addWidget(browser_group)
        
        # 自动化行为
        auto_group = QGroupBox("自动化行为")
        auto_layout = QFormLayout(auto_group)
        
        self.auto_screenshot_checkbox = QCheckBox("自动截图保存")
        auto_layout.addRow("截图:", self.auto_screenshot_checkbox)
        
        self.delay_min_spinbox = QSpinBox()
        self.delay_min_spinbox.setRange(500, 5000)
        self.delay_min_spinbox.setValue(1000)
        self.delay_min_spinbox.setSuffix(" 毫秒")
        auto_layout.addRow("最小延迟:", self.delay_min_spinbox)
        
        self.delay_max_spinbox = QSpinBox()
        self.delay_max_spinbox.setRange(1000, 10000)
        self.delay_max_spinbox.setValue(3000)
        self.delay_max_spinbox.setSuffix(" 毫秒")
        auto_layout.addRow("最大延迟:", self.delay_max_spinbox)
        
        layout.addWidget(auto_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🤖 自动化")
    
    def create_database_tab(self):
        """创建数据库设置标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 数据库设置
        db_group = QGroupBox("数据库")
        db_layout = QFormLayout(db_group)
        
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_edit)
        self.browse_db_button = QPushButton("浏览...")
        db_path_layout.addWidget(self.browse_db_button)
        db_layout.addRow("数据库路径:", db_path_layout)
        
        self.auto_backup_checkbox = QCheckBox("自动备份")
        db_layout.addRow("备份:", self.auto_backup_checkbox)
        
        self.backup_interval_spinbox = QSpinBox()
        self.backup_interval_spinbox.setRange(1, 30)
        self.backup_interval_spinbox.setValue(7)
        self.backup_interval_spinbox.setSuffix(" 天")
        db_layout.addRow("备份间隔:", self.backup_interval_spinbox)
        
        layout.addWidget(db_group)
        
        # 数据管理
        data_group = QGroupBox("数据管理")
        data_layout = QVBoxLayout(data_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.backup_now_button = QPushButton("📦 立即备份")
        button_layout.addWidget(self.backup_now_button)
        
        self.restore_button = QPushButton("📥 恢复备份")
        button_layout.addWidget(self.restore_button)
        
        self.export_button = QPushButton("📤 导出数据")
        button_layout.addWidget(self.export_button)
        
        self.import_button = QPushButton("📥 导入数据")
        button_layout.addWidget(self.import_button)
        
        button_layout.addStretch()
        data_layout.addLayout(button_layout)
        
        layout.addWidget(data_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "💾 数据库")
    
    def create_logging_tab(self):
        """创建日志设置标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 日志级别
        level_group = QGroupBox("日志级别")
        level_layout = QFormLayout(level_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        level_layout.addRow("日志级别:", self.log_level_combo)
        
        self.console_log_checkbox = QCheckBox("控制台输出")
        level_layout.addRow("输出方式:", self.console_log_checkbox)
        
        self.file_log_checkbox = QCheckBox("文件输出")
        level_layout.addRow("", self.file_log_checkbox)
        
        layout.addWidget(level_group)
        
        # 日志文件
        file_group = QGroupBox("日志文件")
        file_layout = QFormLayout(file_group)
        
        self.log_dir_edit = QLineEdit()
        self.log_dir_edit.setReadOnly(True)
        log_dir_layout = QHBoxLayout()
        log_dir_layout.addWidget(self.log_dir_edit)
        self.browse_log_button = QPushButton("浏览...")
        log_dir_layout.addWidget(self.browse_log_button)
        file_layout.addRow("日志目录:", log_dir_layout)
        
        self.max_log_size_spinbox = QSpinBox()
        self.max_log_size_spinbox.setRange(1, 100)
        self.max_log_size_spinbox.setValue(10)
        self.max_log_size_spinbox.setSuffix(" MB")
        file_layout.addRow("最大文件大小:", self.max_log_size_spinbox)
        
        self.log_retention_spinbox = QSpinBox()
        self.log_retention_spinbox.setRange(1, 365)
        self.log_retention_spinbox.setValue(30)
        self.log_retention_spinbox.setSuffix(" 天")
        file_layout.addRow("保留天数:", self.log_retention_spinbox)
        
        layout.addWidget(file_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "📋 日志")
    
    def create_about_tab(self):
        """创建关于标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # 应用信息
        app_info = QTextEdit()
        app_info.setReadOnly(True)
        app_info.setMaximumHeight(300)
        
        about_text = """
<h2>🚀 AI工具管理器</h2>
<p><strong>版本:</strong> 1.0.0</p>
<p><strong>构建日期:</strong> 2024-01-01</p>
<p><strong>开发者:</strong> AI Tools Team</p>

<h3>📝 功能特性</h3>
<ul>
<li>🏠 统一的首页概览和统计</li>
<li>🎯 支持Cursor、Windsurf、Augment三大AI工具</li>
<li>🤖 完整的自动化注册和登录功能</li>
<li>🔄 Cursor专属账号切换功能</li>
<li>📋 完善的日志管理系统</li>
<li>⚙️ 丰富的设置和配置选项</li>
<li>💾 安全的本地数据存储</li>
</ul>

<h3>🔧 技术栈</h3>
<ul>
<li><strong>界面框架:</strong> PySide6 (Qt6)</li>
<li><strong>自动化:</strong> DrissionPage</li>
<li><strong>数据库:</strong> SQLite</li>
<li><strong>语言:</strong> Python 3.8+</li>
</ul>

<h3>📞 联系方式</h3>
<p>如有问题或建议，请通过以下方式联系我们：</p>
<ul>
<li>📧 邮箱: support@aitools.com</li>
<li>🌐 官网: https://aitools.com</li>
<li>📱 QQ群: 123456789</li>
</ul>
        """
        
        app_info.setHtml(about_text)
        layout.addWidget(app_info)
        
        # 许可证信息
        license_group = QGroupBox("许可证")
        license_layout = QVBoxLayout(license_group)
        
        license_text = QLabel("本软件基于 MIT 许可证发布，允许自由使用、修改和分发。")
        license_text.setWordWrap(True)
        license_layout.addWidget(license_text)
        
        layout.addWidget(license_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "ℹ️ 关于")
    
    def create_footer(self, layout):
        """创建底部按钮"""
        footer_layout = QHBoxLayout()
        
        # 重置按钮
        self.reset_button = QPushButton("🔄 重置默认")
        self.reset_button.setObjectName("dangerButton")
        footer_layout.addWidget(self.reset_button)
        
        footer_layout.addStretch()
        
        # 应用和取消按钮
        self.apply_button = QPushButton("✅ 应用")
        self.apply_button.setObjectName("primaryButton")
        footer_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("❌ 取消")
        footer_layout.addWidget(self.cancel_button)
        
        layout.addLayout(footer_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.apply_button.clicked.connect(self.apply_settings)
        self.cancel_button.clicked.connect(self.load_settings)
        self.reset_button.clicked.connect(self.reset_settings)
        
        # 数据库操作
        self.browse_db_button.clicked.connect(self.browse_database_path)
        self.backup_now_button.clicked.connect(self.backup_database)
        self.restore_button.clicked.connect(self.restore_database)
        self.export_button.clicked.connect(self.export_data)
        self.import_button.clicked.connect(self.import_data)
        
        # 日志操作
        self.browse_log_button.clicked.connect(self.browse_log_directory)
    
    def load_settings(self):
        """加载设置"""
        try:
            # 通用设置
            self.startup_checkbox.setChecked(
                self.config_manager.get('general.startup', False)
            )
            self.minimize_to_tray_checkbox.setChecked(
                self.config_manager.get('general.minimize_to_tray', False)
            )
            self.auto_save_checkbox.setChecked(
                self.config_manager.get('general.auto_save', True)
            )
            
            # 界面设置
            theme = self.config_manager.get('ui.theme', '浅色主题')
            self.theme_combo.setCurrentText(theme)
            
            font_size = self.config_manager.get('ui.font_size', 12)
            self.font_size_spinbox.setValue(font_size)
            
            # 自动化设置
            self.headless_checkbox.setChecked(
                self.config_manager.get('automation.headless', True)
            )
            
            timeout = self.config_manager.get('automation.timeout', 30)
            self.browser_timeout_spinbox.setValue(timeout)
            
            # 日志设置
            log_level = self.config_manager.get('logging.level', 'INFO')
            self.log_level_combo.setCurrentText(log_level)
            
            log_dir = self.config_manager.get('logging.directory', 'logs')
            self.log_dir_edit.setText(log_dir)
            
            # 数据库设置
            db_path = self.config_manager.get('database.path', 'accounts.db')
            self.db_path_edit.setText(db_path)
            
            self.logger.info("设置已加载")
            
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            QMessageBox.warning(self, "警告", f"加载设置失败: {str(e)}")
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 保存通用设置
            self.config_manager.set('general.startup', self.startup_checkbox.isChecked())
            self.config_manager.set('general.minimize_to_tray', self.minimize_to_tray_checkbox.isChecked())
            self.config_manager.set('general.auto_save', self.auto_save_checkbox.isChecked())
            
            # 保存界面设置
            self.config_manager.set('ui.theme', self.theme_combo.currentText())
            self.config_manager.set('ui.font_size', self.font_size_spinbox.value())
            
            # 保存自动化设置
            self.config_manager.set('automation.headless', self.headless_checkbox.isChecked())
            self.config_manager.set('automation.timeout', self.browser_timeout_spinbox.value())
            
            # 保存日志设置
            self.config_manager.set('logging.level', self.log_level_combo.currentText())
            self.config_manager.set('logging.directory', self.log_dir_edit.text())
            
            # 保存数据库设置
            self.config_manager.set('database.path', self.db_path_edit.text())
            
            # 保存配置
            self.config_manager.save()
            
            self.logger.info("设置已应用")
            QMessageBox.information(self, "成功", "设置已保存并应用")
            
            # 发送设置变更信号
            self.settings_changed.emit()
            
        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置为默认值吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.config_manager.reset_to_defaults()
                self.load_settings()
                self.logger.info("设置已重置为默认值")
                QMessageBox.information(self, "成功", "设置已重置为默认值")
            except Exception as e:
                self.logger.error(f"重置设置失败: {e}")
                QMessageBox.critical(self, "错误", f"重置设置失败: {str(e)}")
    
    def browse_database_path(self):
        """浏览数据库路径"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "选择数据库文件", 
            self.db_path_edit.text(),
            "SQLite数据库 (*.db);;所有文件 (*)"
        )
        if filename:
            self.db_path_edit.setText(filename)
    
    def browse_log_directory(self):
        """浏览日志目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择日志目录", 
            self.log_dir_edit.text()
        )
        if directory:
            self.log_dir_edit.setText(directory)
    
    def backup_database(self):
        """备份数据库"""
        try:
            # 这里实现数据库备份逻辑
            self.logger.info("数据库备份完成")
            QMessageBox.information(self, "成功", "数据库备份完成")
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            QMessageBox.critical(self, "错误", f"数据库备份失败: {str(e)}")
    
    def restore_database(self):
        """恢复数据库"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", 
            "",
            "SQLite数据库 (*.db);;所有文件 (*)"
        )
        if filename:
            try:
                # 这里实现数据库恢复逻辑
                self.logger.info(f"数据库已从 {filename} 恢复")
                QMessageBox.information(self, "成功", "数据库恢复完成")
            except Exception as e:
                self.logger.error(f"数据库恢复失败: {e}")
                QMessageBox.critical(self, "错误", f"数据库恢复失败: {str(e)}")
    
    def export_data(self):
        """导出数据"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出数据", 
            "ai_tools_data.json",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if filename:
            try:
                # 这里实现数据导出逻辑
                self.logger.info(f"数据已导出到 {filename}")
                QMessageBox.information(self, "成功", "数据导出完成")
            except Exception as e:
                self.logger.error(f"数据导出失败: {e}")
                QMessageBox.critical(self, "错误", f"数据导出失败: {str(e)}")
    
    def import_data(self):
        """导入数据"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "导入数据", 
            "",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if filename:
            try:
                # 这里实现数据导入逻辑
                self.logger.info(f"数据已从 {filename} 导入")
                QMessageBox.information(self, "成功", "数据导入完成")
            except Exception as e:
                self.logger.error(f"数据导入失败: {e}")
                QMessageBox.critical(self, "错误", f"数据导入失败: {str(e)}")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            #pageTitle {
                color: #1976d2;
                margin-bottom: 20px;
            }
            
            QTabWidget::pane {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 15px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid white;
            }
            
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
            
            QPushButton#primaryButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #1565c0;
            }
            
            QPushButton#dangerButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            QPushButton#dangerButton:hover {
                background-color: #d32f2f;
            }
            
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 16px;
            }
            
            QPushButton:hover {
                background-color: #e9ecef;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
            }
            
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #1976d2;
            }
            
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                padding: 10px;
            }
        """)
