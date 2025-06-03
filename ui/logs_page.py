"""
日志管理页面
"""
import os
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QGroupBox, QSplitter, QListWidget,
    QListWidgetItem, QMessageBox, QFileDialog, QCheckBox,
    QDateEdit, QSpinBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QColor, QTextCursor

from utils.logger import get_logger, LogLevel


class LogsPage(QWidget):
    """日志管理页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.auto_refresh_timer = QTimer()
        
        self.setup_ui()
        self.apply_styles()
        self.setup_connections()
        self.load_logs()
        
        # 设置自动刷新
        self.auto_refresh_timer.timeout.connect(self.refresh_logs)
        self.start_auto_refresh()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        self.create_header(layout)
        
        # 控制区域
        self.create_controls(layout)
        
        # 主要内容区域
        self.create_content_area(layout)
        
        # 底部操作区域
        self.create_footer(layout)
    
    def create_header(self, layout):
        """创建标题区域"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("📋 系统日志")
        title_label.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 状态指示器
        self.status_label = QLabel("🟢 日志系统正常")
        self.status_label.setObjectName("statusLabel")
        header_layout.addWidget(self.status_label)
        
        layout.addWidget(header_widget)
    
    def create_controls(self, layout):
        """创建控制区域"""
        controls_group = QGroupBox("日志控制")
        controls_layout = QHBoxLayout(controls_group)
        
        # 日志级别筛选
        level_label = QLabel("级别:")
        controls_layout.addWidget(level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.addItem("全部", "ALL")
        self.level_combo.addItem("🔴 错误", "ERROR")
        self.level_combo.addItem("⚠️ 警告", "WARNING")
        self.level_combo.addItem("ℹ️ 信息", "INFO")
        self.level_combo.addItem("🐛 调试", "DEBUG")
        controls_layout.addWidget(self.level_combo)
        
        controls_layout.addWidget(QLabel("  "))
        
        # 日期筛选
        date_label = QLabel("日期:")
        controls_layout.addWidget(date_label)
        
        self.date_combo = QComboBox()
        self.date_combo.addItem("今天", 0)
        self.date_combo.addItem("最近3天", 3)
        self.date_combo.addItem("最近7天", 7)
        self.date_combo.addItem("最近30天", 30)
        self.date_combo.addItem("全部", -1)
        controls_layout.addWidget(self.date_combo)
        
        controls_layout.addWidget(QLabel("  "))
        
        # 自动刷新
        self.auto_refresh_checkbox = QCheckBox("自动刷新")
        self.auto_refresh_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_refresh_checkbox)
        
        controls_layout.addStretch()
        
        # 操作按钮
        self.refresh_button = QPushButton("🔄 刷新")
        self.refresh_button.setObjectName("primaryButton")
        controls_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.setObjectName("dangerButton")
        controls_layout.addWidget(self.clear_button)
        
        self.export_button = QPushButton("📤 导出")
        controls_layout.addWidget(self.export_button)
        
        layout.addWidget(controls_group)
    
    def create_content_area(self, layout):
        """创建内容区域"""
        # 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：日志文件列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        files_label = QLabel("日志文件")
        files_label.setObjectName("sectionTitle")
        left_layout.addWidget(files_label)
        
        self.files_list = QListWidget()
        self.files_list.setMaximumWidth(250)
        left_layout.addWidget(self.files_list)
        
        splitter.addWidget(left_widget)
        
        # 右侧：日志内容
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        content_label = QLabel("日志内容")
        content_label.setObjectName("sectionTitle")
        right_layout.addWidget(content_label)
        
        self.log_content = QTextEdit()
        self.log_content.setReadOnly(True)
        self.log_content.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.log_content)
        
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([250, 600])
        
        layout.addWidget(splitter)
    
    def create_footer(self, layout):
        """创建底部区域"""
        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        # 统计信息
        self.stats_label = QLabel("总计: 0 条日志")
        self.stats_label.setObjectName("statsLabel")
        footer_layout.addWidget(self.stats_label)
        
        footer_layout.addStretch()
        
        # 日志级别说明
        legend_label = QLabel("🔴 错误  ⚠️ 警告  ℹ️ 信息  🐛 调试")
        legend_label.setObjectName("legendLabel")
        footer_layout.addWidget(legend_label)
        
        layout.addWidget(footer_widget)
    
    def setup_connections(self):
        """设置信号连接"""
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        self.date_combo.currentTextChanged.connect(self.filter_logs)
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        self.refresh_button.clicked.connect(self.refresh_logs)
        self.clear_button.clicked.connect(self.clear_logs)
        self.export_button.clicked.connect(self.export_logs)
        self.files_list.itemClicked.connect(self.load_selected_file)
    
    def load_logs(self):
        """加载日志"""
        try:
            # 加载日志文件列表
            self.load_log_files()
            
            # 加载当前日志内容
            self.load_current_logs()
            
        except Exception as e:
            self.log_content.setText(f"加载日志失败: {str(e)}")
    
    def load_log_files(self):
        """加载日志文件列表"""
        self.files_list.clear()
        
        # 获取日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            return
        
        # 扫描日志文件
        log_files = []
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(log_dir, filename)
                file_stat = os.stat(file_path)
                log_files.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime)
                })
        
        # 按修改时间排序
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        
        # 添加到列表
        for file_info in log_files:
            item = QListWidgetItem()
            
            # 格式化文件信息
            size_kb = file_info['size'] / 1024
            modified_str = file_info['modified'].strftime('%m-%d %H:%M')
            
            display_text = f"{file_info['name']}\n"
            display_text += f"📁 {size_kb:.1f}KB  🕒 {modified_str}"
            
            item.setText(display_text)
            item.setData(Qt.UserRole, file_info)
            
            # 设置颜色
            if 'error' in file_info['name'].lower():
                item.setForeground(QColor("#d32f2f"))
            elif 'warning' in file_info['name'].lower():
                item.setForeground(QColor("#f57c00"))
            else:
                item.setForeground(QColor("#1976d2"))
            
            self.files_list.addItem(item)
        
        # 默认选择第一个文件
        if self.files_list.count() > 0:
            self.files_list.setCurrentRow(0)
    
    def load_current_logs(self):
        """加载当前日志内容"""
        try:
            # 获取最新的日志内容
            log_entries = self.logger.get_recent_logs(limit=1000)
            
            # 应用筛选
            filtered_entries = self.apply_filters(log_entries)
            
            # 显示日志
            self.display_logs(filtered_entries)
            
            # 更新统计
            self.update_stats(len(filtered_entries))
            
        except Exception as e:
            self.log_content.setText(f"加载日志内容失败: {str(e)}")
    
    def load_selected_file(self, item):
        """加载选定的日志文件"""
        try:
            file_info = item.data(Qt.UserRole)
            if not file_info:
                return
            
            # 读取文件内容
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.log_content.setText(content)
            
            # 滚动到底部
            cursor = self.log_content.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_content.setTextCursor(cursor)
            
        except Exception as e:
            self.log_content.setText(f"读取文件失败: {str(e)}")
    
    def apply_filters(self, log_entries):
        """应用筛选条件"""
        filtered = log_entries
        
        # 级别筛选
        selected_level = self.level_combo.currentData()
        if selected_level != "ALL":
            filtered = [entry for entry in filtered if entry.get('level') == selected_level]
        
        # 日期筛选
        days = self.date_combo.currentData()
        if days >= 0:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered = [entry for entry in filtered 
                       if datetime.fromisoformat(entry.get('timestamp', '')) >= cutoff_date]
        
        return filtered
    
    def display_logs(self, log_entries):
        """显示日志条目"""
        self.log_content.clear()
        
        for entry in log_entries:
            # 格式化日志条目
            timestamp = entry.get('timestamp', '')
            level = entry.get('level', 'INFO')
            message = entry.get('message', '')
            
            # 添加级别图标
            level_icon = {
                'ERROR': '🔴',
                'WARNING': '⚠️',
                'INFO': 'ℹ️',
                'DEBUG': '🐛'
            }.get(level, 'ℹ️')
            
            # 格式化时间
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = timestamp
            
            # 添加到文本框
            log_line = f"[{time_str}] {level_icon} {level}: {message}\n"
            self.log_content.append(log_line.rstrip())
        
        # 滚动到底部
        cursor = self.log_content.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_content.setTextCursor(cursor)
    
    def filter_logs(self):
        """筛选日志"""
        self.load_current_logs()
    
    def refresh_logs(self):
        """刷新日志"""
        self.load_logs()
        self.status_label.setText("🟢 日志已刷新")
        
        # 3秒后恢复状态
        QTimer.singleShot(3000, lambda: self.status_label.setText("🟢 日志系统正常"))
    
    def clear_logs(self):
        """清空日志"""
        reply = QMessageBox.question(
            self, "确认清空", 
            "确定要清空所有日志吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.logger.clear_logs()
                self.log_content.clear()
                self.load_log_files()
                self.update_stats(0)
                QMessageBox.information(self, "成功", "日志已清空")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清空日志失败: {str(e)}")
    
    def export_logs(self):
        """导出日志"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "导出日志", 
                f"ai_tools_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "文本文件 (*.txt);;所有文件 (*)"
            )
            
            if filename:
                content = self.log_content.toPlainText()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                QMessageBox.information(self, "成功", f"日志已导出到: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出日志失败: {str(e)}")
    
    def toggle_auto_refresh(self, enabled):
        """切换自动刷新"""
        if enabled:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """开始自动刷新"""
        self.auto_refresh_timer.start(30000)  # 30秒刷新一次
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.auto_refresh_timer.stop()
    
    def update_stats(self, count):
        """更新统计信息"""
        self.stats_label.setText(f"总计: {count} 条日志")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            #pageTitle {
                color: #1976d2;
                margin-bottom: 10px;
            }
            
            #statusLabel {
                color: #4caf50;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
                background-color: #e8f5e8;
            }
            
            #sectionTitle {
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }
            
            #statsLabel {
                color: #666;
                font-size: 12px;
            }
            
            #legendLabel {
                color: #666;
                font-size: 11px;
            }
            
            QListWidget {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                font-size: 11px;
            }
            
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 4px solid #1976d2;
            }
            
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: #fafafa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
            
            QPushButton#primaryButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
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
                padding: 8px 16px;
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
            
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
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
