"""
切换账号对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QTextEdit, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor

from models.account import Account, AccountType, AccountStatus
from models.database import DatabaseManager
from automation.automation_manager import get_automation_manager, AutomationResult


class SwitchAccountWorker(QThread):
    """切换账号工作线程"""
    
    finished = Signal(object)  # AutomationResult
    progress = Signal(str)  # 进度消息
    
    def __init__(self, account: Account, parent=None):
        super().__init__(parent)
        self.account = account
    
    def run(self):
        """执行切换账号操作"""
        try:
            self.progress.emit("正在启动浏览器...")
            
            # 获取自动化管理器
            automation_manager = get_automation_manager()
            
            self.progress.emit("正在登录账号...")
            
            # 执行登录操作
            login_data = {
                'email': self.account.email,
                'password': self.account.password
            }
            
            result = automation_manager.login(
                self.account.account_type, 
                login_data, 
                headless=True
            )
            
            if result.is_success:
                self.progress.emit("账号切换成功！")
            else:
                self.progress.emit(f"切换失败: {result.message}")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_result = AutomationResult(
                success=False,
                message=f"切换账号时发生错误: {str(e)}"
            )
            self.finished.emit(error_result)


class SwitchAccountDialog(QDialog):
    """切换账号对话框"""
    
    account_switched = Signal(object)  # Account对象
    
    def __init__(self, current_accounts, parent=None):
        super().__init__(parent)
        self.current_accounts = current_accounts
        self.db_manager = DatabaseManager()
        self.worker = None
        
        self.setWindowTitle("切换Cursor账号")
        self.setModal(True)
        self.resize(500, 600)
        
        self.setup_ui()
        self.load_accounts()
        self.apply_styles()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("选择要切换的Cursor账号")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 说明
        desc_label = QLabel("选择一个账号进行自动登录切换。系统将自动打开Cursor并登录到选定的账号。")
        desc_label.setWordWrap(True)
        desc_label.setObjectName("descriptionLabel")
        layout.addWidget(desc_label)
        
        # 账号列表
        accounts_group = QGroupBox("可用账号")
        accounts_layout = QVBoxLayout(accounts_group)
        
        self.accounts_list = QListWidget()
        self.accounts_list.setMinimumHeight(300)
        accounts_layout.addWidget(self.accounts_list)
        
        layout.addWidget(accounts_group)
        
        # 进度区域
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
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.switch_button = QPushButton("🔄 切换到选定账号")
        self.switch_button.setObjectName("primaryButton")
        self.switch_button.setEnabled(False)
        button_layout.addWidget(self.switch_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("关闭")
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.accounts_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.switch_button.clicked.connect(self.switch_account)
        self.close_button.clicked.connect(self.close)
    
    def load_accounts(self):
        """加载账号列表"""
        try:
            # 获取所有Cursor账号
            all_accounts = self.db_manager.get_all_accounts()
            cursor_accounts = [acc for acc in all_accounts if acc.account_type == AccountType.CURSOR]
            
            self.accounts_list.clear()
            
            for account in cursor_accounts:
                item = QListWidgetItem()
                
                # 创建账号显示文本
                status_text = "✅" if account.status == AccountStatus.ACTIVE else "❌"
                display_text = f"{status_text} {account.name}\n"
                display_text += f"   📧 {account.email}\n"
                display_text += f"   👤 {account.username or '未设置'}\n"
                
                if account.subscription_type:
                    display_text += f"   💎 {account.subscription_type}\n"
                
                if account.last_used:
                    display_text += f"   🕒 最后使用: {account.last_used.strftime('%Y-%m-%d %H:%M')}"
                else:
                    display_text += f"   🕒 从未使用"
                
                item.setText(display_text)
                item.setData(Qt.UserRole, account)
                
                # 设置颜色
                if account.status == AccountStatus.ACTIVE:
                    item.setForeground(QColor("#2e7d32"))
                elif account.status == AccountStatus.EXPIRED:
                    item.setForeground(QColor("#d32f2f"))
                else:
                    item.setForeground(QColor("#f57c00"))
                
                self.accounts_list.addItem(item)
            
            if not cursor_accounts:
                item = QListWidgetItem("暂无Cursor账号，请先添加账号")
                item.setForeground(QColor("#666"))
                self.accounts_list.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载账号列表失败: {str(e)}")
    
    def on_selection_changed(self):
        """选择变化处理"""
        selected_items = self.accounts_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        if has_selection:
            item = selected_items[0]
            account = item.data(Qt.UserRole)
            has_valid_account = account is not None
            self.switch_button.setEnabled(has_valid_account)
        else:
            self.switch_button.setEnabled(False)
    
    def switch_account(self):
        """切换账号"""
        selected_items = self.accounts_list.selectedItems()
        if not selected_items:
            return
        
        account = selected_items[0].data(Qt.UserRole)
        if not account:
            return
        
        # 检查账号信息
        if not account.email or not account.password:
            QMessageBox.warning(
                self, "信息不完整", 
                "选定的账号缺少邮箱或密码信息，无法自动登录。\n请先编辑账号补充完整信息。"
            )
            return
        
        # 确认切换
        reply = QMessageBox.question(
            self, "确认切换", 
            f"确定要切换到账号 '{account.name}' 吗？\n\n"
            f"邮箱: {account.email}\n"
            f"系统将自动打开Cursor并登录到此账号。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 开始切换
        self.start_switch(account)
    
    def start_switch(self, account: Account):
        """开始切换账号"""
        try:
            # 禁用按钮
            self.switch_button.setEnabled(False)
            self.close_button.setEnabled(False)
            
            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            
            self.progress_text.clear()
            self.progress_text.append(f"开始切换到账号: {account.name}")
            
            # 创建工作线程
            self.worker = SwitchAccountWorker(account)
            self.worker.progress.connect(self.on_progress)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动切换操作失败: {str(e)}")
            self.reset_ui()
    
    def on_progress(self, message: str):
        """进度更新"""
        self.progress_text.append(message)
        # 滚动到底部
        cursor = self.progress_text.textCursor()
        cursor.movePosition(cursor.End)
        self.progress_text.setTextCursor(cursor)
    
    def on_finished(self, result: AutomationResult):
        """切换完成"""
        try:
            if result.is_success:
                self.progress_text.append("✅ 账号切换成功！")
                
                # 更新账号使用时间
                selected_items = self.accounts_list.selectedItems()
                if selected_items:
                    account = selected_items[0].data(Qt.UserRole)
                    if account:
                        account.update_last_used()
                        self.db_manager.update_account(account)
                        self.account_switched.emit(account)
                
                QMessageBox.information(
                    self, "切换成功", 
                    "账号切换成功！Cursor应该已经打开并登录到选定的账号。"
                )
            else:
                self.progress_text.append(f"❌ 切换失败: {result.message}")
                QMessageBox.warning(self, "切换失败", f"账号切换失败:\n\n{result.message}")
            
        except Exception as e:
            self.progress_text.append(f"❌ 处理结果时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"处理切换结果失败: {str(e)}")
        
        finally:
            self.reset_ui()
    
    def reset_ui(self):
        """重置UI状态"""
        self.switch_button.setEnabled(True)
        self.close_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 重新检查选择状态
        self.on_selection_changed()
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "确认关闭", 
                "切换操作正在进行中，确定要关闭对话框吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            #descriptionLabel {
                color: #666;
                font-size: 13px;
                margin-bottom: 10px;
            }
            
            QListWidget {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 4px solid #1976d2;
            }
            
            QListWidget::item:hover {
                background-color: #f5f5f5;
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
                padding: 10px 20px;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background-color: #e9ecef;
            }
            
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
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
        """)
