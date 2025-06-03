"""
账号数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AccountType(Enum):
    """账号类型枚举"""
    CURSOR = "Cursor"
    WINDSURF = "Windsurf"
    AUGMENT = "Augment"
    GITHUB_COPILOT = "GitHub Copilot"
    CLAUDE = "Claude"
    CHATGPT = "ChatGPT"
    OPENAI_API = "OpenAI API"
    ANTHROPIC_API = "Anthropic API"
    GOOGLE_GEMINI = "Google Gemini"
    MICROSOFT_COPILOT = "Microsoft Copilot"
    JETBRAINS_AI = "JetBrains AI"
    TABNINE = "Tabnine"
    CODEIUM = "Codeium"
    REPLIT_AI = "Replit AI"
    OTHER = "其他"


class AccountStatus(Enum):
    """账号状态枚举"""
    ACTIVE = "活跃"
    INACTIVE = "未激活"
    EXPIRED = "已过期"
    SUSPENDED = "已暂停"


@dataclass
class Account:
    """账号数据模型"""
    id: Optional[int] = None
    name: str = ""
    account_type: AccountType = AccountType.OTHER
    email: str = ""
    username: str = ""
    password: str = ""  # 加密存储
    api_key: str = ""   # 加密存储
    status: AccountStatus = AccountStatus.ACTIVE
    subscription_type: str = ""  # 订阅类型：免费版、专业版等
    expiry_date: Optional[datetime] = None
    notes: str = ""
    tags: str = ""  # 逗号分隔的标签
    created_at: datetime = None
    updated_at: datetime = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type.value,
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'api_key': self.api_key,
            'status': self.status.value,
            'subscription_type': self.subscription_type,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """从字典创建账号对象"""
        account = cls()
        account.id = data.get('id')
        account.name = data.get('name', '')
        account.account_type = AccountType(data.get('account_type', AccountType.OTHER.value))
        account.email = data.get('email', '')
        account.username = data.get('username', '')
        account.password = data.get('password', '')
        account.api_key = data.get('api_key', '')
        account.status = AccountStatus(data.get('status', AccountStatus.ACTIVE.value))
        account.subscription_type = data.get('subscription_type', '')
        
        # 处理日期字段
        if data.get('expiry_date'):
            account.expiry_date = datetime.fromisoformat(data['expiry_date'])
        if data.get('created_at'):
            account.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            account.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('last_used'):
            account.last_used = datetime.fromisoformat(data['last_used'])
            
        account.notes = data.get('notes', '')
        account.tags = data.get('tags', '')
        account.usage_count = data.get('usage_count', 0)
        
        return account
    
    def get_tags_list(self) -> list:
        """获取标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def add_tag(self, tag: str):
        """添加标签"""
        tags = self.get_tags_list()
        if tag not in tags:
            tags.append(tag)
            self.tags = ', '.join(tags)
    
    def remove_tag(self, tag: str):
        """移除标签"""
        tags = self.get_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.tags = ', '.join(tags)
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if self.expiry_date is None:
            return False
        return datetime.now() > self.expiry_date
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used = datetime.now()
        self.usage_count += 1
        self.updated_at = datetime.now()

    def get_account_type_info(self) -> Dict[str, Any]:
        """获取账号类型的详细信息"""
        type_info = {
            AccountType.CURSOR: {
                "category": "AI编程助手",
                "description": "AI驱动的代码编辑器",
                "website": "https://cursor.sh",
                "requires_api_key": False,
                "subscription_types": ["免费版", "专业版", "商业版"]
            },
            AccountType.WINDSURF: {
                "category": "AI编程助手",
                "description": "AI代码编辑器和开发环境",
                "website": "https://windsurf.ai",
                "requires_api_key": False,
                "subscription_types": ["免费版", "专业版"]
            },
            AccountType.AUGMENT: {
                "category": "AI编程助手",
                "description": "AI代码补全和开发工具",
                "website": "https://augmentcode.com",
                "requires_api_key": True,
                "subscription_types": ["免费版", "专业版", "企业版"]
            },
            AccountType.GITHUB_COPILOT: {
                "category": "AI编程助手",
                "description": "GitHub的AI代码助手",
                "website": "https://github.com/features/copilot",
                "requires_api_key": False,
                "subscription_types": ["个人版", "商业版"]
            },
            AccountType.CLAUDE: {
                "category": "AI聊天助手",
                "description": "Anthropic的AI助手",
                "website": "https://claude.ai",
                "requires_api_key": False,
                "subscription_types": ["免费版", "专业版", "团队版"]
            },
            AccountType.CHATGPT: {
                "category": "AI聊天助手",
                "description": "OpenAI的ChatGPT",
                "website": "https://chat.openai.com",
                "requires_api_key": False,
                "subscription_types": ["免费版", "Plus", "Team", "Enterprise"]
            },
            AccountType.OPENAI_API: {
                "category": "AI API服务",
                "description": "OpenAI API服务",
                "website": "https://platform.openai.com",
                "requires_api_key": True,
                "subscription_types": ["按使用付费"]
            },
            AccountType.ANTHROPIC_API: {
                "category": "AI API服务",
                "description": "Anthropic Claude API",
                "website": "https://console.anthropic.com",
                "requires_api_key": True,
                "subscription_types": ["按使用付费"]
            },
            AccountType.GOOGLE_GEMINI: {
                "category": "AI聊天助手",
                "description": "Google的Gemini AI",
                "website": "https://gemini.google.com",
                "requires_api_key": False,
                "subscription_types": ["免费版", "高级版"]
            },
            AccountType.MICROSOFT_COPILOT: {
                "category": "AI助手",
                "description": "Microsoft Copilot",
                "website": "https://copilot.microsoft.com",
                "requires_api_key": False,
                "subscription_types": ["免费版", "专业版"]
            },
            AccountType.JETBRAINS_AI: {
                "category": "AI编程助手",
                "description": "JetBrains AI Assistant",
                "website": "https://www.jetbrains.com/ai",
                "requires_api_key": False,
                "subscription_types": ["订阅制"]
            },
            AccountType.TABNINE: {
                "category": "AI编程助手",
                "description": "AI代码补全工具",
                "website": "https://www.tabnine.com",
                "requires_api_key": False,
                "subscription_types": ["免费版", "专业版", "企业版"]
            },
            AccountType.CODEIUM: {
                "category": "AI编程助手",
                "description": "免费AI代码助手",
                "website": "https://codeium.com",
                "requires_api_key": False,
                "subscription_types": ["免费版", "团队版", "企业版"]
            },
            AccountType.REPLIT_AI: {
                "category": "AI编程助手",
                "description": "Replit的AI编程助手",
                "website": "https://replit.com",
                "requires_api_key": False,
                "subscription_types": ["免费版", "核心版", "团队版"]
            },
            AccountType.OTHER: {
                "category": "其他",
                "description": "其他AI工具",
                "website": "",
                "requires_api_key": False,
                "subscription_types": ["自定义"]
            }
        }

        return type_info.get(self.account_type, type_info[AccountType.OTHER])

    def get_category(self) -> str:
        """获取账号类型分类"""
        return self.get_account_type_info()["category"]

    def requires_api_key(self) -> bool:
        """检查是否需要API密钥"""
        return self.get_account_type_info()["requires_api_key"]

    def get_available_subscription_types(self) -> list:
        """获取可用的订阅类型"""
        return self.get_account_type_info()["subscription_types"]
