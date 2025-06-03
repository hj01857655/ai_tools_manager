"""
用户数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import hashlib
import secrets


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "管理员"
    USER = "普通用户"


@dataclass
class User:
    """用户数据模型"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""  # 密码哈希
    salt: str = ""  # 密码盐值
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    last_login: Optional[datetime] = None
    login_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def set_password(self, password: str):
        """设置密码"""
        self.salt = secrets.token_hex(32)
        self.password_hash = self._hash_password(password, self.salt)
        self.updated_at = datetime.now()
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == self._hash_password(password, self.salt)
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """生成密码哈希"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def update_login(self):
        """更新登录信息"""
        self.last_login = datetime.now()
        self.login_count += 1
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'salt': self.salt,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象"""
        user = cls()
        user.id = data.get('id')
        user.username = data.get('username', '')
        user.email = data.get('email', '')
        user.password_hash = data.get('password_hash', '')
        user.salt = data.get('salt', '')
        user.role = UserRole(data.get('role', UserRole.USER.value))
        user.is_active = data.get('is_active', True)
        user.login_count = data.get('login_count', 0)
        
        # 处理日期时间字段
        if data.get('created_at'):
            user.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            user.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
            
        return user


@dataclass
class UserSession:
    """用户会话模型"""
    user_id: int
    username: str
    role: UserRole
    login_time: datetime
    last_activity: datetime
    
    def __post_init__(self):
        if self.login_time is None:
            self.login_time = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """检查会话是否过期"""
        if timeout_minutes <= 0:
            return False
        
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > (timeout_minutes * 60)
