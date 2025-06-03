"""
用户会话管理模块
"""
from typing import Optional
from datetime import datetime
from models.user import UserSession, User, UserRole
from models.database import DatabaseManager


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.current_session: Optional[UserSession] = None
        self.db_manager = DatabaseManager()
        self.session_timeout_minutes = 30
    
    def login(self, username: str, password: str) -> bool:
        """用户登录"""
        user = self.db_manager.get_user_by_username(username)
        if not user:
            return False
        
        if not user.is_active:
            return False
        
        if not user.verify_password(password):
            return False
        
        # 更新用户登录信息
        user.update_login()
        self.db_manager.update_user(user)
        
        # 创建会话
        self.current_session = UserSession(
            user_id=user.id,
            username=user.username,
            role=user.role,
            login_time=datetime.now(),
            last_activity=datetime.now()
        )
        
        return True
    
    def logout(self):
        """用户登出"""
        self.current_session = None
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        if not self.current_session:
            return False
        
        # 检查会话是否过期
        if self.current_session.is_expired(self.session_timeout_minutes):
            self.logout()
            return False
        
        return True
    
    def get_current_user(self) -> Optional[User]:
        """获取当前用户"""
        if not self.is_logged_in():
            return None
        
        return self.db_manager.get_user_by_id(self.current_session.user_id)
    
    def get_current_session(self) -> Optional[UserSession]:
        """获取当前会话"""
        if not self.is_logged_in():
            return None
        
        return self.current_session
    
    def update_activity(self):
        """更新活动时间"""
        if self.current_session:
            self.current_session.update_activity()
    
    def set_session_timeout(self, minutes: int):
        """设置会话超时时间"""
        self.session_timeout_minutes = minutes
    
    def is_admin(self) -> bool:
        """检查当前用户是否为管理员"""
        if not self.is_logged_in():
            return False
        
        return self.current_session.role == UserRole.ADMIN
    
    def require_login(self) -> bool:
        """要求登录，返回是否已登录"""
        return self.is_logged_in()
    
    def create_default_admin(self) -> bool:
        """创建默认管理员账户"""
        # 检查是否已存在用户
        users = self.db_manager.get_all_users()
        if users:
            return False
        
        # 创建默认管理员
        admin_user = User()
        admin_user.username = "admin"
        admin_user.email = "admin@localhost"
        admin_user.role = UserRole.ADMIN
        admin_user.set_password("admin123")
        
        try:
            user_id = self.db_manager.add_user(admin_user)
            return user_id > 0
        except Exception:
            return False


# 全局会话管理器实例
_session_manager = None


def get_session_manager() -> SessionManager:
    """获取全局会话管理器实例"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
