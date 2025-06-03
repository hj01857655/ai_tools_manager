"""
Cursor自动化注册登录
"""
import time
from .base_automation import (
    BaseAutomation, AutomationResult, AutomationStatus,
    RegistrationData, LoginData
)


class CursorAutomation(BaseAutomation):
    """Cursor自动化类"""
    
    def get_service_name(self) -> str:
        return "Cursor"
    
    def get_registration_url(self) -> str:
        return "https://cursor.sh/sign-up"
    
    def get_login_url(self) -> str:
        return "https://cursor.sh/sign-in"
    
    def register(self, data: RegistrationData) -> AutomationResult:
        """注册Cursor账号"""
        if not self.init_browser():
            return AutomationResult(
                status=AutomationStatus.FAILED,
                message="浏览器初始化失败"
            )
        
        try:
            # 访问注册页面
            self.page.get(self.get_registration_url())
            self.random_delay(2, 4)
            
            # 等待页面加载
            if not self.wait_for_element('input[type="email"]', timeout=10):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="注册页面加载失败",
                    screenshot_path=self.take_screenshot("cursor_register_page_load_failed")
                )
            
            # 输入邮箱
            if not self.wait_and_input('input[type="email"]', data.email):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="输入邮箱失败",
                    screenshot_path=self.take_screenshot("cursor_register_email_failed")
                )
            
            self.random_delay(1, 2)
            
            # 输入密码
            password_selector = 'input[type="password"]'
            if not self.wait_and_input(password_selector, data.password):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="输入密码失败",
                    screenshot_path=self.take_screenshot("cursor_register_password_failed")
                )
            
            self.random_delay(1, 2)
            
            # 如果有用户名字段，填写用户名
            if data.username:
                username_selectors = [
                    'input[name="username"]',
                    'input[placeholder*="username"]',
                    'input[placeholder*="Username"]'
                ]
                for selector in username_selectors:
                    if self.wait_for_element(selector, timeout=2):
                        self.wait_and_input(selector, data.username)
                        break
            
            # 如果有姓名字段，填写姓名
            if data.first_name:
                name_selectors = [
                    'input[name="firstName"]',
                    'input[name="first_name"]',
                    'input[placeholder*="First"]',
                    'input[placeholder*="Name"]'
                ]
                for selector in name_selectors:
                    if self.wait_for_element(selector, timeout=2):
                        self.wait_and_input(selector, data.first_name)
                        break
            
            if data.last_name:
                last_name_selectors = [
                    'input[name="lastName"]',
                    'input[name="last_name"]',
                    'input[placeholder*="Last"]'
                ]
                for selector in last_name_selectors:
                    if self.wait_for_element(selector, timeout=2):
                        self.wait_and_input(selector, data.last_name)
                        break
            
            # 处理服务条款复选框
            terms_selectors = [
                'input[type="checkbox"]',
                'input[name="terms"]',
                'input[name="agree"]',
                '[role="checkbox"]'
            ]
            for selector in terms_selectors:
                if self.wait_for_element(selector, timeout=2):
                    try:
                        element = self.page.ele(selector)
                        if element and not element.states.is_checked:
                            element.click()
                            self.random_delay(0.5, 1)
                    except:
                        pass
            
            self.random_delay(1, 2)
            
            # 点击注册按钮
            register_selectors = [
                'button[type="submit"]',
                'button:contains("Sign Up")',
                'button:contains("Register")',
                'button:contains("Create Account")',
                'input[type="submit"]'
            ]
            
            register_clicked = False
            for selector in register_selectors:
                if self.wait_for_element(selector, timeout=2):
                    if self.wait_and_click(selector):
                        register_clicked = True
                        break
            
            if not register_clicked:
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="找不到注册按钮",
                    screenshot_path=self.take_screenshot("cursor_register_button_not_found")
                )
            
            self.random_delay(3, 5)
            
            # 检查注册结果
            current_url = self.page.url
            
            # 检查是否需要邮箱验证
            verification_indicators = [
                "verify",
                "confirmation",
                "check your email",
                "验证",
                "确认"
            ]
            
            page_text = self.page.html.lower()
            for indicator in verification_indicators:
                if indicator in page_text:
                    return AutomationResult(
                        status=AutomationStatus.EMAIL_VERIFICATION_REQUIRED,
                        message="需要邮箱验证，请检查邮箱并点击验证链接",
                        screenshot_path=self.take_screenshot("cursor_register_email_verification"),
                        data={"email": data.email}
                    )
            
            # 检查是否注册成功（通常会跳转到仪表板或欢迎页面）
            if "dashboard" in current_url or "welcome" in current_url or "app" in current_url:
                return AutomationResult(
                    status=AutomationStatus.SUCCESS,
                    message="Cursor账号注册成功",
                    screenshot_path=self.take_screenshot("cursor_register_success"),
                    data=data.to_dict()
                )
            
            # 检查是否有错误信息
            error_selectors = [
                '.error',
                '.alert-danger',
                '[role="alert"]',
                '.text-red',
                '.text-danger'
            ]
            
            for selector in error_selectors:
                if self.wait_for_element(selector, timeout=2):
                    error_element = self.page.ele(selector)
                    if error_element:
                        error_text = error_element.text
                        if "already exists" in error_text.lower() or "已存在" in error_text:
                            return AutomationResult(
                                status=AutomationStatus.ACCOUNT_EXISTS,
                                message=f"账号已存在: {error_text}",
                                screenshot_path=self.take_screenshot("cursor_register_account_exists")
                            )
                        else:
                            return AutomationResult(
                                status=AutomationStatus.FAILED,
                                message=f"注册失败: {error_text}",
                                screenshot_path=self.take_screenshot("cursor_register_error")
                            )
            
            # 如果没有明确的成功或失败指示，返回需要手动检查
            return AutomationResult(
                status=AutomationStatus.UNKNOWN_ERROR,
                message="注册状态不明确，请手动检查",
                screenshot_path=self.take_screenshot("cursor_register_unclear")
            )
            
        except Exception as e:
            return self.handle_common_errors(e)
        finally:
            self.close_browser()
    
    def login(self, data: LoginData) -> AutomationResult:
        """登录Cursor账号"""
        if not self.init_browser():
            return AutomationResult(
                status=AutomationStatus.FAILED,
                message="浏览器初始化失败"
            )
        
        try:
            # 访问登录页面
            self.page.get(self.get_login_url())
            self.random_delay(2, 4)
            
            # 等待页面加载
            if not self.wait_for_element('input[type="email"]', timeout=10):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="登录页面加载失败",
                    screenshot_path=self.take_screenshot("cursor_login_page_load_failed")
                )
            
            # 输入邮箱
            if not self.wait_and_input('input[type="email"]', data.email):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="输入邮箱失败",
                    screenshot_path=self.take_screenshot("cursor_login_email_failed")
                )
            
            self.random_delay(1, 2)
            
            # 输入密码
            if not self.wait_and_input('input[type="password"]', data.password):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="输入密码失败",
                    screenshot_path=self.take_screenshot("cursor_login_password_failed")
                )
            
            self.random_delay(1, 2)
            
            # 处理"记住我"选项
            if data.remember_me:
                remember_selectors = [
                    'input[name="remember"]',
                    'input[type="checkbox"]',
                    '[role="checkbox"]'
                ]
                for selector in remember_selectors:
                    if self.wait_for_element(selector, timeout=2):
                        try:
                            element = self.page.ele(selector)
                            if element and not element.states.is_checked:
                                element.click()
                                self.random_delay(0.5, 1)
                                break
                        except:
                            pass
            
            # 点击登录按钮
            login_selectors = [
                'button[type="submit"]',
                'button:contains("Sign In")',
                'button:contains("Login")',
                'button:contains("Log In")',
                'input[type="submit"]'
            ]
            
            login_clicked = False
            for selector in login_selectors:
                if self.wait_for_element(selector, timeout=2):
                    if self.wait_and_click(selector):
                        login_clicked = True
                        break
            
            if not login_clicked:
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="找不到登录按钮",
                    screenshot_path=self.take_screenshot("cursor_login_button_not_found")
                )
            
            self.random_delay(3, 5)
            
            # 检查登录结果
            current_url = self.page.url
            
            # 检查是否登录成功
            if "dashboard" in current_url or "app" in current_url or "workspace" in current_url:
                return AutomationResult(
                    status=AutomationStatus.SUCCESS,
                    message="Cursor登录成功",
                    screenshot_path=self.take_screenshot("cursor_login_success"),
                    data=data.to_dict()
                )
            
            # 检查是否有错误信息
            error_selectors = [
                '.error',
                '.alert-danger',
                '[role="alert"]',
                '.text-red',
                '.text-danger'
            ]
            
            for selector in error_selectors:
                if self.wait_for_element(selector, timeout=2):
                    error_element = self.page.ele(selector)
                    if error_element:
                        error_text = error_element.text
                        if "invalid" in error_text.lower() or "incorrect" in error_text.lower():
                            return AutomationResult(
                                status=AutomationStatus.INVALID_CREDENTIALS,
                                message=f"登录凭据无效: {error_text}",
                                screenshot_path=self.take_screenshot("cursor_login_invalid_credentials")
                            )
                        else:
                            return AutomationResult(
                                status=AutomationStatus.FAILED,
                                message=f"登录失败: {error_text}",
                                screenshot_path=self.take_screenshot("cursor_login_error")
                            )
            
            # 检查是否需要验证码
            captcha_selectors = [
                '.captcha',
                '.recaptcha',
                '[data-sitekey]',
                'iframe[src*="recaptcha"]'
            ]
            
            for selector in captcha_selectors:
                if self.wait_for_element(selector, timeout=2):
                    return AutomationResult(
                        status=AutomationStatus.CAPTCHA_REQUIRED,
                        message="需要验证码，请手动完成验证",
                        screenshot_path=self.take_screenshot("cursor_login_captcha_required")
                    )
            
            return AutomationResult(
                status=AutomationStatus.UNKNOWN_ERROR,
                message="登录状态不明确，请手动检查",
                screenshot_path=self.take_screenshot("cursor_login_unclear")
            )
            
        except Exception as e:
            return self.handle_common_errors(e)
        finally:
            self.close_browser()
