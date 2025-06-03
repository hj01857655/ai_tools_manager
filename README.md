# AI开发工具账号管理器

一个用PySide6开发的现代化AI开发工具账号管理应用程序，专门用于管理Cursor、Windsurf、Augment等AI开发工具的账号信息。

## 功能特性

### 🔐 安全管理
- 密码和API密钥加密存储
- 本地SQLite数据库
- 安全的数据访问控制

### 📋 账号管理
- 支持多种AI工具类型（Cursor、Windsurf、Augment、GitHub Copilot、Claude、ChatGPT等）
- 完整的账号信息管理（邮箱、用户名、密码、API密钥）
- 订阅类型和到期日期跟踪
- 账号状态管理（活跃、未激活、已过期、已暂停）

### 🏷️ 组织功能
- 自定义标签系统
- 账号分类和筛选
- 强大的搜索功能
- 备注信息管理

### 📊 使用统计
- 使用次数统计
- 最后使用时间记录
- 账号创建和更新时间跟踪

### 🎨 现代化界面
- 基于PySide6的现代UI
- 响应式布局设计
- 支持明暗主题切换
- 直观的操作体验

## 安装要求

### Python版本
- Python 3.8 或更高版本

### 依赖包
```bash
pip install -r requirements.txt
```

主要依赖：
- PySide6 >= 6.6.0
- cryptography >= 41.0.0

## 快速开始

### 1. 克隆或下载项目
```bash
git clone <repository-url>
cd ai_tools_manager
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python run.py
```

或者：
```bash
python main.py
```

## 使用指南

### 添加账号
1. 点击"添加账号"按钮
2. 填写账号信息：
   - 账号名称（必填）
   - 选择账号类型
   - 填写登录信息（邮箱、用户名、密码）
   - 添加API密钥（如果有）
   - 设置订阅信息和到期日期
   - 添加标签和备注
3. 点击"保存"

### 管理账号
- **编辑**：双击账号行或选中后点击"编辑"按钮
- **删除**：选中账号后点击"删除"按钮
- **标记使用**：选中账号后点击"标记为已使用"

### 搜索和筛选
- **搜索**：在搜索框中输入关键词
- **类型筛选**：选择特定的账号类型
- **状态筛选**：选择特定的账号状态

### 查看详情
选中任意账号，右侧面板会显示详细信息，包括：
- 基本信息
- 订阅状态
- 使用统计
- 标签和备注

## 项目结构

```
ai_tools_manager/
├── main.py              # 主程序入口
├── run.py               # 启动脚本
├── requirements.txt     # 依赖列表
├── README.md           # 说明文档
├── ui/                 # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py  # 主窗口
│   ├── account_dialog.py # 账号编辑对话框
│   └── styles.py       # 样式定义
├── models/             # 数据模型
│   ├── __init__.py
│   ├── account.py      # 账号数据模型
│   └── database.py     # 数据库操作
└── utils/              # 工具模块
    ├── __init__.py
    ├── encryption.py   # 加密工具
    └── config.py       # 配置管理
```

## 数据安全

### 加密存储
- 密码和API密钥使用AES加密存储
- 基于PBKDF2的密钥派生
- 本地数据库，不上传到云端

### 数据备份
- 数据库文件：`accounts.db`
- 配置文件：`config.json`
- 建议定期备份这些文件

## 开发说明

### 添加新的账号类型
在 `models/account.py` 中的 `AccountType` 枚举中添加新类型：

```python
class AccountType(Enum):
    # 现有类型...
    NEW_TOOL = "新工具名称"
```

### 自定义主题
在 `ui/styles.py` 中修改或添加新的主题样式。

### 扩展功能
- 导入/导出功能可在主窗口的相应方法中实现
- 数据库模式可在 `models/database.py` 中扩展

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查Python版本是否符合要求
   - 确认所有依赖包已正确安装

2. **数据库错误**
   - 检查文件权限
   - 删除 `accounts.db` 文件重新初始化

3. **界面显示异常**
   - 检查系统DPI设置
   - 尝试重启应用程序

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 更新日志

### v1.0.0
- 初始版本发布
- 基本的账号管理功能
- 加密存储支持
- 现代化UI界面
