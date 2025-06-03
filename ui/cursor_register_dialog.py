"""
Cursor注册配置对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QCheckBox, QSpinBox, QGroupBox,
    QFormLayout, QTextEdit, QMessageBox, QProgressBar,
    QTabWidget, QWidget, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont

from utils.account_generator import get_account_generator
from utils.logger import get_logger


class AccountGenerationWorker(QThread):
    """账号生成工作线程"""
    
    finished = Signal(list)  # 生成的账号列表
    progress = Signal(str)   # 进度消息
    error = Signal(str)      # 错误消息
    
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.generator = get_account_generator()
    
    def run(self):
        """执行账号生成"""
        try:
            count = self.config.get('count', 1)
            domain = self.config.get('domain', '')
            include_pin = self.config.get('include_pin', False)
            username_prefix = self.config.get('username_prefix', 'cursor')
            
            self.progress.emit(f"开始生成 {count} 个账号...")
            
            accounts = []
            for i in range(count):
                self.progress.emit(f"生成第 {i+1}/{count} 个账号...")
                
                try:
                    account = self.generator.generate_account(
                        domain=domain if domain else None,
                        username_prefix=f"{username_prefix}{i+1:03d}" if count > 1 else username_prefix,
                        include_pin=include_pin
                    )
                    accounts.append(account)
                    
                except Exception as e:
                    self.error.emit(f"生成第 {i+1} 个账号失败: {str(e)}")
                    continue
            
            self.progress.emit(f"账号生成完成: {len(accounts)}/{count}")
            self.finished.emit(accounts)
            
        except Exception as e:
            self.error.emit(f"账号生成失败: {str(e)}")


class CursorRegisterDialog(QDialog):
    """Cursor注册配置对话框"""
    
    accounts_generated = Signal(list)  # 账号生成完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.generator = get_account_generator()
        self.generated_accounts = []
        self.worker = None
        
        self.setWindowTitle("Cursor账号注册配置")
        self.setModal(True)
        self.resize(600, 700)
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("🎯 Cursor账号注册配置")
        title_label.setObjectName("dialogTitle")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 基础配置标签页
        self.create_basic_config_tab()
        
        # 高级配置标签页
        self.create_advanced_config_tab()
        
        # 生成结果标签页
        self.create_results_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 进度区域
        self.create_progress_area(layout)
        
        # 按钮区域
        self.create_buttons(layout)
    
    def create_basic_config_tab(self):
        """创建基础配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 账号数量配置
        count_group = QGroupBox("账号数量")
        count_layout = QFormLayout(count_group)
        
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 50)
        self.count_spinbox.setValue(1)
        count_layout.addRow("生成数量:", self.count_spinbox)
        
        layout.addWidget(count_group)
        
        # 邮箱配置
        email_group = QGroupBox("邮箱配置")
        email_layout = QFormLayout(email_group)

        # 域名输入框
        self.domain_edit = QLineEdit()
        self.domain_edit.setText("hjj0185.email")  # 默认域名
        self.domain_edit.setPlaceholderText("输入邮箱域名，如: hjj0185.email")
        email_layout.addRow("邮箱域名:", self.domain_edit)

        # 说明文本
        info_label = QLabel("生成的邮箱格式: username@您的域名")
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        email_layout.addRow("", info_label)

        # 域名示例
        example_label = QLabel("示例: hjj0185.email → cursor123@hjj0185.email")
        example_label.setStyleSheet("color: #999; font-size: 11px; font-style: italic;")
        email_layout.addRow("", example_label)

        layout.addWidget(email_group)
        
        # 用户名配置
        username_group = QGroupBox("用户名配置")
        username_layout = QFormLayout(username_group)
        
        self.username_prefix_edit = QLineEdit()
        self.username_prefix_edit.setText("cursor")
        self.username_prefix_edit.setPlaceholderText("用户名前缀")
        username_layout.addRow("用户名前缀:", self.username_prefix_edit)
        
        layout.addWidget(username_group)
        
        # PIN配置
        pin_group = QGroupBox("PIN配置")
        pin_layout = QFormLayout(pin_group)
        
        self.include_pin_checkbox = QCheckBox("生成PIN码")
        self.include_pin_checkbox.setToolTip("为账号生成4位数字PIN码（可选）")
        pin_layout.addRow("PIN选项:", self.include_pin_checkbox)
        
        layout.addWidget(pin_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔧 基础配置")
    
    def create_advanced_config_tab(self):
        """创建高级配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 密码配置
        password_group = QGroupBox("密码配置")
        password_layout = QFormLayout(password_group)
        
        self.password_length_spinbox = QSpinBox()
        self.password_length_spinbox.setRange(8, 32)
        self.password_length_spinbox.setValue(12)
        password_layout.addRow("密码长度:", self.password_length_spinbox)
        
        self.include_uppercase_checkbox = QCheckBox("包含大写字母")
        self.include_uppercase_checkbox.setChecked(True)
        password_layout.addRow("", self.include_uppercase_checkbox)
        
        self.include_numbers_checkbox = QCheckBox("包含数字")
        self.include_numbers_checkbox.setChecked(True)
        password_layout.addRow("", self.include_numbers_checkbox)
        
        self.include_symbols_checkbox = QCheckBox("包含特殊符号")
        self.include_symbols_checkbox.setChecked(True)
        password_layout.addRow("", self.include_symbols_checkbox)
        
        layout.addWidget(password_group)
        
        # 生成选项
        options_group = QGroupBox("生成选项")
        options_layout = QFormLayout(options_group)
        
        self.auto_export_checkbox = QCheckBox("自动导出到文件")
        self.auto_export_checkbox.setChecked(True)
        options_layout.addRow("导出选项:", self.auto_export_checkbox)
        
        self.add_to_manager_checkbox = QCheckBox("自动添加到账号管理器")
        self.add_to_manager_checkbox.setChecked(True)
        options_layout.addRow("管理器选项:", self.add_to_manager_checkbox)
        
        layout.addWidget(options_group)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_button = QPushButton("🔍 预览生成效果")
        self.preview_button.clicked.connect(self.preview_generation)
        preview_layout.addWidget(self.preview_button)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "⚙️ 高级配置")
    
    def create_results_tab(self):
        """创建结果标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 结果列表
        results_group = QGroupBox("生成结果")
        results_layout = QVBoxLayout(results_group)
        
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(300)
        results_layout.addWidget(self.results_list)
        
        # 结果操作按钮
        results_buttons_layout = QHBoxLayout()
        
        self.copy_selected_btn = QPushButton("📋 复制选中")
        self.copy_selected_btn.clicked.connect(self.copy_selected_account)
        results_buttons_layout.addWidget(self.copy_selected_btn)
        
        self.copy_all_btn = QPushButton("📋 复制全部")
        self.copy_all_btn.clicked.connect(self.copy_all_accounts)
        results_buttons_layout.addWidget(self.copy_all_btn)
        
        self.export_btn = QPushButton("📤 导出文件")
        self.export_btn.clicked.connect(self.export_accounts)
        results_buttons_layout.addWidget(self.export_btn)
        
        results_buttons_layout.addStretch()
        results_layout.addLayout(results_buttons_layout)
        
        layout.addWidget(results_group)
        
        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QFormLayout(stats_group)
        
        self.stats_total_label = QLabel("0")
        stats_layout.addRow("总生成数:", self.stats_total_label)
        
        self.stats_success_label = QLabel("0")
        stats_layout.addRow("成功数:", self.stats_success_label)
        
        layout.addWidget(stats_group)
        
        self.tab_widget.addTab(tab, "📊 生成结果")
    
    def create_progress_area(self, layout):
        """创建进度区域"""
        progress_group = QGroupBox("操作进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(100)
        self.progress_text.setReadOnly(True)
        progress_layout.addWidget(self.progress_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
    
    def create_buttons(self, layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("🚀 开始生成")
        self.generate_btn.setObjectName("primaryButton")
        self.generate_btn.clicked.connect(self.start_generation)
        button_layout.addWidget(self.generate_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_generation)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    

    
    def preview_generation(self):
        """预览生成效果"""
        try:
            config = self.get_generation_config()

            # 生成一个示例账号
            account = self.generator.generate_account(
                domain=config['domain'],
                username_prefix=config['username_prefix'],
                include_pin=config['include_pin']
            )

            preview_text = f"预览生成效果:\n\n"
            preview_text += f"用户名: {account.username}\n"
            preview_text += f"邮箱: {account.email}\n"
            preview_text += f"密码: {account.password}\n"
            preview_text += f"域名: {config['domain']}\n"
            if account.pin:
                preview_text += f"PIN: {account.pin}\n"

            self.preview_text.setText(preview_text)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"预览失败: {str(e)}")
    
    def get_generation_config(self) -> dict:
        """获取生成配置"""
        domain = self.domain_edit.text().strip()
        if not domain:
            domain = "hjj0185.email"  # 默认域名

        return {
            'count': self.count_spinbox.value(),
            'domain': domain,
            'username_prefix': self.username_prefix_edit.text().strip() or "cursor",
            'include_pin': self.include_pin_checkbox.isChecked(),
            'password_length': self.password_length_spinbox.value(),
            'auto_export': self.auto_export_checkbox.isChecked(),
            'add_to_manager': self.add_to_manager_checkbox.isChecked()
        }
    
    def start_generation(self):
        """开始生成账号"""
        try:
            config = self.get_generation_config()
            
            # 禁用生成按钮
            self.generate_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            
            # 清空进度文本
            self.progress_text.clear()
            self.progress_text.append("开始生成账号...")
            
            # 创建工作线程
            self.worker = AccountGenerationWorker(config)
            self.worker.finished.connect(self.on_generation_finished)
            self.worker.progress.connect(self.on_generation_progress)
            self.worker.error.connect(self.on_generation_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动生成失败: {str(e)}")
            self.reset_ui()
    
    def stop_generation(self):
        """停止生成"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.progress_text.append("⏹️ 生成已停止")
        
        self.reset_ui()
    
    def on_generation_progress(self, message: str):
        """生成进度更新"""
        self.progress_text.append(message)
        # 滚动到底部
        cursor = self.progress_text.textCursor()
        cursor.movePosition(cursor.End)
        self.progress_text.setTextCursor(cursor)
    
    def on_generation_error(self, error: str):
        """生成错误处理"""
        self.progress_text.append(f"❌ {error}")
    
    def on_generation_finished(self, accounts: list):
        """生成完成处理"""
        try:
            self.generated_accounts = accounts
            
            # 更新结果列表
            self.update_results_list()
            
            # 更新统计
            self.update_stats()
            
            # 切换到结果标签页
            self.tab_widget.setCurrentIndex(2)
            
            # 自动导出（如果启用）
            config = self.get_generation_config()
            if config['auto_export'] and accounts:
                self.export_accounts()
            
            # 发送信号
            if config['add_to_manager'] and accounts:
                self.accounts_generated.emit(accounts)
            
            self.progress_text.append(f"✅ 生成完成: {len(accounts)} 个账号")
            
        except Exception as e:
            self.logger.error(f"处理生成结果失败: {e}")
        
        finally:
            self.reset_ui()
    
    def update_results_list(self):
        """更新结果列表"""
        self.results_list.clear()
        
        for i, account in enumerate(self.generated_accounts, 1):
            item_text = f"账号 {i}: {account.email}\n"
            item_text += f"  用户名: {account.username}\n"
            item_text += f"  密码: {account.password}\n"
            if account.pin:
                item_text += f"  PIN: {account.pin}\n"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, account)
            self.results_list.addItem(item)
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.generated_accounts)
        self.stats_total_label.setText(str(total))
        self.stats_success_label.setText(str(total))
    
    def copy_selected_account(self):
        """复制选中的账号"""
        current_item = self.results_list.currentItem()
        if current_item:
            account = current_item.data(Qt.UserRole)
            if account:
                text = f"邮箱: {account.email}\n密码: {account.password}"
                if account.pin:
                    text += f"\nPIN: {account.pin}"
                
                from PySide6.QtGui import QClipboard
                from PySide6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                
                self.progress_text.append("📋 已复制选中账号到剪贴板")
    
    def copy_all_accounts(self):
        """复制所有账号"""
        if not self.generated_accounts:
            return
        
        text_lines = []
        for i, account in enumerate(self.generated_accounts, 1):
            text_lines.append(f"账号 {i}:")
            text_lines.append(f"  邮箱: {account.email}")
            text_lines.append(f"  密码: {account.password}")
            if account.pin:
                text_lines.append(f"  PIN: {account.pin}")
            text_lines.append("")
        
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(text_lines))
        
        self.progress_text.append("📋 已复制所有账号到剪贴板")
    
    def export_accounts(self):
        """导出账号到文件"""
        if not self.generated_accounts:
            QMessageBox.information(self, "提示", "没有账号可导出")
            return
        
        try:
            filename = self.generator.export_accounts(self.generated_accounts)
            if filename:
                self.progress_text.append(f"📤 账号已导出到: {filename}")
                QMessageBox.information(self, "导出成功", f"账号已导出到: {filename}")
            else:
                QMessageBox.warning(self, "导出失败", "导出账号失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def reset_ui(self):
        """重置UI状态"""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            #dialogTitle {
                color: #1976d2;
                margin-bottom: 10px;
            }
            
            QPushButton#primaryButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #1565c0;
            }
            
            QPushButton#primaryButton:disabled {
                background-color: #ccc;
                color: #666;
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
            
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            
            QListWidget {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 4px solid #1976d2;
            }
        """)
