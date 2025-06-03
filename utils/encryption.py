"""
加密工具模块
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, password: str = None):
        """
        初始化加密管理器
        
        Args:
            password: 主密码，如果为None则使用默认密码
        """
        if password is None:
            password = "ai_tools_manager_default_key"
        
        self.password = password.encode()
        self.salt = b'ai_tools_manager_salt_2024'  # 在实际应用中应该随机生成
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """从密码派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        加密字符串
        
        Args:
            data: 要加密的字符串
            
        Returns:
            加密后的base64编码字符串
        """
        if not data:
            return ""
        
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字符串
        
        Args:
            encrypted_data: 加密的base64编码字符串
            
        Returns:
            解密后的原始字符串
        """
        if not encrypted_data:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"解密失败: {e}")
            return ""
    
    def encrypt_sensitive_fields(self, account_dict: dict) -> dict:
        """
        加密账号敏感字段
        
        Args:
            account_dict: 账号字典
            
        Returns:
            加密敏感字段后的账号字典
        """
        sensitive_fields = ['password', 'api_key']
        encrypted_dict = account_dict.copy()
        
        for field in sensitive_fields:
            if field in encrypted_dict and encrypted_dict[field]:
                encrypted_dict[field] = self.encrypt(encrypted_dict[field])
        
        return encrypted_dict
    
    def decrypt_sensitive_fields(self, account_dict: dict) -> dict:
        """
        解密账号敏感字段
        
        Args:
            account_dict: 包含加密敏感字段的账号字典
            
        Returns:
            解密敏感字段后的账号字典
        """
        sensitive_fields = ['password', 'api_key']
        decrypted_dict = account_dict.copy()
        
        for field in sensitive_fields:
            if field in decrypted_dict and decrypted_dict[field]:
                decrypted_dict[field] = self.decrypt(decrypted_dict[field])
        
        return decrypted_dict


# 全局加密管理器实例
_encryption_manager = None


def get_encryption_manager(password: str = None) -> EncryptionManager:
    """获取全局加密管理器实例"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager(password)
    return _encryption_manager


def set_master_password(password: str):
    """设置主密码"""
    global _encryption_manager
    _encryption_manager = EncryptionManager(password)
