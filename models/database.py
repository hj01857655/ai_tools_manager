"""
数据库操作模块
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from models.account import Account, AccountType, AccountStatus
from models.user import User, UserRole


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "accounts.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'USER',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0
                )
            ''')

            # 创建账号表（添加用户ID关联）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    email TEXT,
                    username TEXT,
                    password TEXT,
                    api_key TEXT,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    subscription_type TEXT,
                    expiry_date TEXT,
                    notes TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # 检查是否需要迁移现有数据
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'user_id' not in columns:
                # 添加user_id列到现有账号表
                cursor.execute('ALTER TABLE accounts ADD COLUMN user_id INTEGER DEFAULT 1')

            conn.commit()
    
    def add_account(self, account: Account, user_id: int = 1) -> int:
        """添加账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (
                    user_id, name, account_type, email, username, password, api_key,
                    status, subscription_type, expiry_date, notes, tags,
                    created_at, updated_at, last_used, usage_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                account.name,
                account.account_type.value,
                account.email,
                account.username,
                account.password,
                account.api_key,
                account.status.value,
                account.subscription_type,
                account.expiry_date.isoformat() if account.expiry_date else None,
                account.notes,
                account.tags,
                account.created_at.isoformat(),
                account.updated_at.isoformat(),
                account.last_used.isoformat() if account.last_used else None,
                account.usage_count
            ))
            account_id = cursor.lastrowid
            conn.commit()
            return account_id
    
    def get_account(self, account_id: int) -> Optional[Account]:
        """获取单个账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_account(row)
            return None
    
    def get_all_accounts(self) -> List[Account]:
        """获取所有账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [self._row_to_account(row) for row in rows]

    def get_accounts_by_user(self, user_id: int) -> List[Account]:
        """根据用户ID获取账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            rows = cursor.fetchall()
            return [self._row_to_account(row) for row in rows]
    
    def update_account(self, account: Account) -> bool:
        """更新账号"""
        if account.id is None:
            return False
        
        account.updated_at = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET
                    name = ?, account_type = ?, email = ?, username = ?,
                    password = ?, api_key = ?, status = ?, subscription_type = ?,
                    expiry_date = ?, notes = ?, tags = ?, updated_at = ?,
                    last_used = ?, usage_count = ?
                WHERE id = ?
            ''', (
                account.name,
                account.account_type.value,
                account.email,
                account.username,
                account.password,
                account.api_key,
                account.status.value,
                account.subscription_type,
                account.expiry_date.isoformat() if account.expiry_date else None,
                account.notes,
                account.tags,
                account.updated_at.isoformat(),
                account.last_used.isoformat() if account.last_used else None,
                account.usage_count,
                account.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_account(self, account_id: int) -> bool:
        """删除账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_accounts(self, query: str) -> List[Account]:
        """搜索账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_pattern = f'%{query}%'
            cursor.execute('''
                SELECT * FROM accounts 
                WHERE name LIKE ? OR email LIKE ? OR username LIKE ? 
                   OR notes LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC
            ''', (search_pattern, search_pattern, search_pattern, 
                  search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [self._row_to_account(row) for row in rows]
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """根据类型获取账号"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE account_type = ? ORDER BY created_at DESC', 
                         (account_type.value,))
            rows = cursor.fetchall()
            return [self._row_to_account(row) for row in rows]
    
    def _row_to_account(self, row) -> Account:
        """将数据库行转换为Account对象"""
        account = Account()
        account.id = row[0]
        # row[1] 是 user_id，暂时跳过
        account.name = row[2]
        account.account_type = AccountType(row[3])
        account.email = row[4] or ""
        account.username = row[5] or ""
        account.password = row[6] or ""
        account.api_key = row[7] or ""
        account.status = AccountStatus(row[8])
        account.subscription_type = row[9] or ""

        # 处理日期字段
        if row[10]:  # expiry_date
            account.expiry_date = datetime.fromisoformat(row[10])

        account.notes = row[11] or ""
        account.tags = row[12] or ""
        account.created_at = datetime.fromisoformat(row[13])
        account.updated_at = datetime.fromisoformat(row[14])

        if row[15]:  # last_used
            account.last_used = datetime.fromisoformat(row[15])

        account.usage_count = row[16] or 0

        return account

    # 用户管理方法
    def add_user(self, user: User) -> int:
        """添加用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (
                    username, email, password_hash, salt, role, is_active,
                    created_at, updated_at, last_login, login_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.username,
                user.email,
                user.password_hash,
                user.salt,
                user.role.value,
                user.is_active,
                user.created_at.isoformat(),
                user.updated_at.isoformat(),
                user.last_login.isoformat() if user.last_login else None,
                user.login_count
            ))
            conn.commit()
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def update_user(self, user: User) -> bool:
        """更新用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET
                    username = ?, email = ?, password_hash = ?, salt = ?,
                    role = ?, is_active = ?, updated_at = ?,
                    last_login = ?, login_count = ?
                WHERE id = ?
            ''', (
                user.username,
                user.email,
                user.password_hash,
                user.salt,
                user.role.value,
                user.is_active,
                user.updated_at.isoformat(),
                user.last_login.isoformat() if user.last_login else None,
                user.login_count,
                user.id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]

    def _row_to_user(self, row) -> User:
        """将数据库行转换为User对象"""
        user = User()
        user.id = row[0]
        user.username = row[1]
        user.email = row[2]
        user.password_hash = row[3]
        user.salt = row[4]
        user.role = UserRole(row[5])
        user.is_active = bool(row[6])
        user.created_at = datetime.fromisoformat(row[7])
        user.updated_at = datetime.fromisoformat(row[8])

        if row[9]:  # last_login
            user.last_login = datetime.fromisoformat(row[9])

        user.login_count = row[10] or 0

        return user
