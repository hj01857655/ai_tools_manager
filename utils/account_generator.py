"""
账号生成器 - 自动生成账号信息
"""
import random
import string
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    from utils.logger import get_logger
except ImportError:
    # 如果作为独立脚本运行，使用标准日志
    import logging
    def get_logger():
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)


@dataclass
class GeneratedAccount:
    """生成的账号信息"""
    username: str
    email: str
    password: str
    domain: str
    pin: Optional[str] = None
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


class AccountGenerator:
    """账号生成器"""
    
    def __init__(self):
        self.logger = get_logger()
        
        # 默认邮箱域名（可配置）
        self.default_domain = "hjj0185.email"

        # 支持的域名列表（用户可配置）
        self.custom_domains = [
            "hjj0185.email",
            "tempmail.plus"  # 保留作为备选
        ]
        
        # 用户名前缀
        self.username_prefixes = [
            "dev", "code", "user", "test", "demo", "temp",
            "cursor", "ai", "prog", "tech", "beta", "alpha"
        ]
        
        # 密码复杂度配置
        self.password_config = {
            "length": 12,
            "include_uppercase": True,
            "include_lowercase": True,
            "include_numbers": True,
            "include_symbols": True,
            "symbols": "!@#$%^&*"
        }
    
    def generate_username(self, prefix: str = None, length: int = 8) -> str:
        """生成用户名"""
        try:
            if not prefix:
                prefix = random.choice(self.username_prefixes)
            
            # 生成随机数字后缀
            suffix_length = max(3, length - len(prefix))
            suffix = ''.join(random.choices(string.digits, k=suffix_length))
            
            username = f"{prefix}{suffix}"
            
            self.logger.debug(f"生成用户名: {username}")
            return username
            
        except Exception as e:
            self.logger.error(f"生成用户名失败: {e}")
            # 备用方案
            return f"user{int(time.time())}"
    
    def generate_email(self, domain: str = None, username: str = None) -> str:
        """生成邮箱"""
        try:
            if not domain:
                domain = self.default_domain

            if not username:
                username = self.generate_username(length=10)

            # 添加时间戳确保唯一性
            timestamp = str(int(time.time()))[-4:]
            email = f"{username}{timestamp}@{domain}"

            self.logger.debug(f"生成邮箱: {email}")
            return email

        except Exception as e:
            self.logger.error(f"生成邮箱失败: {e}")
            # 备用方案
            return f"temp{int(time.time())}@{self.default_domain}"
    
    def generate_password(self, length: int = None, config: Dict = None) -> str:
        """生成强密码"""
        try:
            if config is None:
                config = self.password_config
            
            if length is None:
                length = config.get("length", 12)
            
            # 构建字符集
            chars = ""
            
            if config.get("include_lowercase", True):
                chars += string.ascii_lowercase
            
            if config.get("include_uppercase", True):
                chars += string.ascii_uppercase
            
            if config.get("include_numbers", True):
                chars += string.digits
            
            if config.get("include_symbols", True):
                chars += config.get("symbols", "!@#$%^&*")
            
            if not chars:
                chars = string.ascii_letters + string.digits
            
            # 生成密码
            password = ''.join(random.choices(chars, k=length))
            
            # 确保密码包含各种字符类型
            if config.get("include_uppercase", True) and not any(c.isupper() for c in password):
                password = password[:-1] + random.choice(string.ascii_uppercase)
            
            if config.get("include_numbers", True) and not any(c.isdigit() for c in password):
                password = password[:-1] + random.choice(string.digits)
            
            if config.get("include_symbols", True) and not any(c in config.get("symbols", "!@#$%^&*") for c in password):
                password = password[:-1] + random.choice(config.get("symbols", "!@#$%^&*"))
            
            self.logger.debug(f"生成密码: {'*' * len(password)} (长度: {len(password)})")
            return password
            
        except Exception as e:
            self.logger.error(f"生成密码失败: {e}")
            # 备用方案
            return f"TempPass{random.randint(1000, 9999)}!"
    
    def generate_pin(self, length: int = 4) -> str:
        """生成PIN码"""
        try:
            pin = ''.join(random.choices(string.digits, k=length))
            self.logger.debug(f"生成PIN: {pin}")
            return pin
            
        except Exception as e:
            self.logger.error(f"生成PIN失败: {e}")
            return str(random.randint(1000, 9999))
    
    def generate_account(self,
                        domain: str = None,
                        username_prefix: str = None,
                        include_pin: bool = False,
                        pin: str = None,
                        password_length: int = None) -> GeneratedAccount:
        """生成完整账号信息"""
        try:
            self.logger.info("开始生成账号信息")
            
            # 生成用户名
            username = self.generate_username(prefix=username_prefix)
            
            # 生成邮箱
            email = self.generate_email(domain=domain, username=username)
            
            # 生成密码
            password = self.generate_password(length=password_length)

            # 处理PIN（优先使用传入的PIN，否则根据include_pin决定是否生成）
            if pin:
                # 使用传入的PIN
                final_pin = pin
            elif include_pin:
                # 自动生成PIN
                final_pin = self.generate_pin()
            else:
                # 不使用PIN
                final_pin = None
            
            # 确定使用的域名
            used_domain = domain if domain else email.split('@')[1]
            
            account = GeneratedAccount(
                username=username,
                email=email,
                password=password,
                domain=used_domain,
                pin=final_pin
            )
            
            self.logger.info(f"账号生成成功: {email}")
            return account
            
        except Exception as e:
            self.logger.error(f"生成账号失败: {e}")
            raise
    
    def generate_batch_accounts(self, 
                               count: int,
                               domain: str = None,
                               username_prefix: str = None,
                               include_pin: bool = False) -> List[GeneratedAccount]:
        """批量生成账号"""
        try:
            self.logger.info(f"开始批量生成 {count} 个账号")
            
            accounts = []
            for i in range(count):
                try:
                    # 为每个账号添加序号
                    prefix = f"{username_prefix or 'user'}{i+1:03d}" if username_prefix else None
                    
                    account = self.generate_account(
                        domain=domain,
                        username_prefix=prefix,
                        include_pin=include_pin
                    )
                    
                    accounts.append(account)
                    
                    # 添加小延迟避免重复
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"生成第 {i+1} 个账号失败: {e}")
                    continue
            
            self.logger.info(f"批量生成完成: {len(accounts)}/{count}")
            return accounts
            
        except Exception as e:
            self.logger.error(f"批量生成账号失败: {e}")
            return []
    
    def validate_email_domain(self, domain: str) -> bool:
        """验证邮箱域名"""
        try:
            # 基本格式检查
            if not domain or '.' not in domain:
                return False
            
            # 检查是否包含非法字符
            allowed_chars = string.ascii_letters + string.digits + '.-'
            if not all(c in allowed_chars for c in domain):
                return False
            
            # 检查长度
            if len(domain) < 4 or len(domain) > 253:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证域名失败: {e}")
            return False
    
    def get_available_domains(self) -> List[str]:
        """获取可用的邮箱域名"""
        return self.custom_domains.copy()

    def set_default_domain(self, domain: str) -> bool:
        """设置默认域名"""
        try:
            if self.validate_email_domain(domain):
                self.default_domain = domain
                if domain not in self.custom_domains:
                    self.custom_domains.append(domain)
                self.logger.info(f"设置默认域名: {domain}")
                return True
            else:
                self.logger.error(f"无效的域名: {domain}")
                return False
        except Exception as e:
            self.logger.error(f"设置默认域名失败: {e}")
            return False

    def get_default_domain(self) -> str:
        """获取默认域名"""
        return self.default_domain
    
    def add_custom_domain(self, domain: str) -> bool:
        """添加自定义域名"""
        try:
            if self.validate_email_domain(domain):
                if domain not in self.custom_domains:
                    self.custom_domains.append(domain)
                    self.logger.info(f"添加自定义域名: {domain}")
                    return True
                else:
                    self.logger.warning(f"域名已存在: {domain}")
                    return True
            else:
                self.logger.error(f"无效的域名: {domain}")
                return False

        except Exception as e:
            self.logger.error(f"添加自定义域名失败: {e}")
            return False
    
    def export_accounts(self, accounts: List[GeneratedAccount], filename: str = None) -> str:
        """导出账号信息"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_accounts_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 生成的账号信息\n")
                f.write(f"# 生成时间: {datetime.now().isoformat()}\n")
                f.write(f"# 账号数量: {len(accounts)}\n\n")
                
                for i, account in enumerate(accounts, 1):
                    f.write(f"账号 {i}:\n")
                    f.write(f"  用户名: {account.username}\n")
                    f.write(f"  邮箱: {account.email}\n")
                    f.write(f"  密码: {account.password}\n")
                    f.write(f"  域名: {account.domain}\n")
                    if account.pin:
                        f.write(f"  PIN: {account.pin}\n")
                    f.write(f"  生成时间: {account.generated_at.isoformat()}\n")
                    f.write("\n")
            
            self.logger.info(f"账号信息已导出: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"导出账号信息失败: {e}")
            return ""


# 全局生成器实例
_generator_instance = None


def get_account_generator() -> AccountGenerator:
    """获取账号生成器实例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = AccountGenerator()
    return _generator_instance


# 便捷函数
def generate_cursor_account(domain: str = None, include_pin: bool = False, pin: str = None) -> GeneratedAccount:
    """生成Cursor账号"""
    generator = get_account_generator()
    return generator.generate_account(
        domain=domain,  # 使用传入的域名或默认域名
        username_prefix="cursor",
        include_pin=include_pin,
        pin=pin,
        password_length=12
    )


def generate_email_with_domain(domain: str = None) -> str:
    """生成指定域名的邮箱"""
    generator = get_account_generator()
    return generator.generate_email(domain=domain)


def generate_strong_password(length: int = 12) -> str:
    """生成强密码"""
    generator = get_account_generator()
    return generator.generate_password(length=length)


def get_available_domains() -> List[str]:
    """获取可用邮箱域名列表"""
    generator = get_account_generator()
    return generator.get_available_domains()


def set_default_domain(domain: str) -> bool:
    """设置默认域名"""
    generator = get_account_generator()
    return generator.set_default_domain(domain)


def get_default_domain() -> str:
    """获取默认域名"""
    generator = get_account_generator()
    return generator.get_default_domain()


if __name__ == "__main__":
    # 测试代码
    generator = AccountGenerator()
    
    print("🧪 测试账号生成器")
    print("=" * 50)
    
    # 测试单个账号生成
    account = generator.generate_account(include_pin=True)
    print(f"生成账号:")
    print(f"  用户名: {account.username}")
    print(f"  邮箱: {account.email}")
    print(f"  密码: {account.password}")
    print(f"  域名: {account.domain}")
    print(f"  PIN: {account.pin}")
    
    # 测试批量生成
    print(f"\n批量生成3个账号:")
    accounts = generator.generate_batch_accounts(3, username_prefix="test")
    for i, acc in enumerate(accounts, 1):
        print(f"  账号{i}: {acc.email}")
    
    # 导出账号
    if accounts:
        filename = generator.export_accounts(accounts)
        print(f"\n账号已导出到: {filename}")
    
    print("\n✅ 测试完成")
