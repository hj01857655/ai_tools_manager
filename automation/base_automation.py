"""
自动化基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import random


class AutomationStatus(Enum):
    """自动化状态"""
    SUCCESS = "成功"
    FAILED = "失败"
    TIMEOUT = "超时"
    CAPTCHA_REQUIRED = "需要验证码"
    EMAIL_VERIFICATION_REQUIRED = "需要邮箱验证"
    PHONE_VERIFICATION_REQUIRED = "需要手机验证"
    ACCOUNT_EXISTS = "账号已存在"
    INVALID_CREDENTIALS = "凭据无效"
    NETWORK_ERROR = "网络错误"
    UNKNOWN_ERROR = "未知错误"


@dataclass
class AutomationResult:
    """自动化结果"""
    status: AutomationStatus
    message: str = ""
    data: Dict[str, Any] = None
    screenshot_path: Optional[str] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
    
    @property
    def is_success(self) -> bool:
        return self.status == AutomationStatus.SUCCESS
    
    @property
    def needs_manual_intervention(self) -> bool:
        return self.status in [
            AutomationStatus.CAPTCHA_REQUIRED,
            AutomationStatus.EMAIL_VERIFICATION_REQUIRED,
            AutomationStatus.PHONE_VERIFICATION_REQUIRED
        ]


@dataclass
class RegistrationData:
    """注册数据"""
    email: str
    password: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'password': self.password,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'company': self.company
        }


@dataclass
class LoginData:
    """登录数据"""
    email: str
    password: str
    remember_me: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'password': self.password,
            'remember_me': self.remember_me
        }


class BaseAutomation(ABC):
    """自动化基类"""
    
    def __init__(self, headless: bool = False, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.page = None
        self.screenshots_dir = "screenshots"
        
    @abstractmethod
    def get_service_name(self) -> str:
        """获取服务名称"""
        pass
    
    @abstractmethod
    def get_registration_url(self) -> str:
        """获取注册页面URL"""
        pass
    
    @abstractmethod
    def get_login_url(self) -> str:
        """获取登录页面URL"""
        pass
    
    @abstractmethod
    def register(self, data: RegistrationData) -> AutomationResult:
        """注册账号"""
        pass
    
    @abstractmethod
    def login(self, data: LoginData) -> AutomationResult:
        """登录账号"""
        pass
    
    def init_browser(self) -> bool:
        """初始化浏览器"""
        try:
            from DrissionPage import ChromiumOptions, Chromium

            # 配置浏览器选项
            options = ChromiumOptions()
            if self.headless:
                options.headless()

            # 设置用户代理
            options.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            # 禁用图片加载以提高速度
            options.set_pref('profile.managed_default_content_settings.images', 2)

            # 创建浏览器对象
            browser = Chromium(addr_or_opts=options)
            self.page = browser.latest_tab
            self.page.set.timeouts(base=self.timeout)

            return True
        except Exception as e:
            print(f"初始化浏览器失败: {e}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        if self.page:
            try:
                # 关闭浏览器
                browser = self.page.browser
                browser.quit()
            except:
                pass
            self.page = None
    
    def take_screenshot(self, name: str = None) -> str:
        """截图"""
        if not self.page:
            return ""
        
        try:
            import os
            if not os.path.exists(self.screenshots_dir):
                os.makedirs(self.screenshots_dir)
            
            if not name:
                name = f"{self.get_service_name()}_{int(time.time())}"
            
            screenshot_path = os.path.join(self.screenshots_dir, f"{name}.png")
            self.page.get_screenshot(path=screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"截图失败: {e}")
            return ""
    
    def wait_and_click(self, selector: str, timeout: int = None) -> bool:
        """等待元素并点击"""
        if not self.page:
            return False
        
        try:
            timeout = timeout or self.timeout
            element = self.page.ele(selector, timeout=timeout)
            if element:
                element.click()
                return True
        except Exception as e:
            print(f"点击元素失败 {selector}: {e}")
        
        return False
    
    def wait_and_input(self, selector: str, text: str, timeout: int = None) -> bool:
        """等待元素并输入文本"""
        if not self.page:
            return False
        
        try:
            timeout = timeout or self.timeout
            element = self.page.ele(selector, timeout=timeout)
            if element:
                element.clear()
                element.input(text)
                return True
        except Exception as e:
            print(f"输入文本失败 {selector}: {e}")
        
        return False
    
    def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """等待元素出现"""
        if not self.page:
            return False
        
        try:
            timeout = timeout or self.timeout
            element = self.page.ele(selector, timeout=timeout)
            return element is not None
        except:
            return False
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机延迟"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def handle_common_errors(self, error: Exception) -> AutomationResult:
        """处理常见错误"""
        error_msg = str(error).lower()
        
        if "timeout" in error_msg:
            return AutomationResult(
                status=AutomationStatus.TIMEOUT,
                message=f"操作超时: {error}",
                screenshot_path=self.take_screenshot("timeout_error")
            )
        elif "network" in error_msg or "connection" in error_msg:
            return AutomationResult(
                status=AutomationStatus.NETWORK_ERROR,
                message=f"网络错误: {error}",
                screenshot_path=self.take_screenshot("network_error")
            )
        else:
            return AutomationResult(
                status=AutomationStatus.UNKNOWN_ERROR,
                message=f"未知错误: {error}",
                screenshot_path=self.take_screenshot("unknown_error")
            )
