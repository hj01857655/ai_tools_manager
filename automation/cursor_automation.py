"""
Cursor自动化注册登录
"""
from automation.base_automation import (
    BaseAutomation, AutomationResult, AutomationStatus,
    RegistrationData, LoginData
)
from utils.account_generator import get_account_generator, GeneratedAccount
from utils.logger import get_logger


class CursorAutomation(BaseAutomation):
    """Cursor自动化类"""

    def __init__(self, headless: bool = False, timeout: int = 30):
        super().__init__(headless, timeout)
        self.logger = get_logger()
    
    def get_service_name(self) -> str:
        return "Cursor"
    
    def get_registration_url(self) -> str:
        return "https://authenticator.cursor.sh/sign-up"

    def get_login_url(self) -> str:
        return "https://www.cursor.com/api/auth/login"

    def get_homepage_url(self) -> str:
        return "https://www.cursor.com/"

    def input_fields_with_validation(self, fields_dict: dict) -> bool:
        """改进的表单填充方法，参考用户提供的方法"""
        import time
        import random

        # 存储已输入的值
        input_values = {}

        try:
            for name, value in fields_dict.items():
                print(f"🔤 正在输入 {name}: {value}")

                # 获取当前输入框
                field = self.page.ele(f'@name={name}')
                if not field:
                    print(f"❌ 找不到字段: {name}")
                    return False

                # 保存当前输入的值
                input_values[name] = value

                # 再次检查之前输入的内容是否还在
                for prev_name, prev_value in input_values.items():
                    if prev_name != name:
                        prev_field = self.page.ele(f'@name={prev_name}')
                        if prev_field:
                            prev_current_value = prev_field.attr('value') or ''
                            # 如果之前的值被清空，重新输入
                            if not prev_current_value or prev_current_value != prev_value:
                                print(f"⚠️ 检测到 {prev_name} 的值被清空，正在重新输入")
                                prev_field.clear()
                                prev_field.input(prev_value)
                                time.sleep(random.uniform(0.5, 1))

                # 输入当前字段的值
                field.clear()
                field.input(value)
                time.sleep(random.uniform(1, 2))

                # 验证输入是否成功
                current_value = field.attr('value') or ''
                if current_value == value:
                    print(f"✅ 成功输入 {name}: {value}")
                else:
                    print(f"❌ 输入验证失败 {name}: 期望 '{value}', 实际 '{current_value}'")
                    # 重试一次
                    field.clear()
                    field.input(value)
                    time.sleep(1)
                    current_value = field.attr('value') or ''
                    if current_value != value:
                        return False
                    print(f"✅ 重试成功 {name}: {value}")

            # 最终验证所有字段
            print("🔍 最终验证所有字段...")
            for name, expected_value in fields_dict.items():
                field = self.page.ele(f'@name={name}')
                if field:
                    actual_value = field.attr('value') or ''
                    if actual_value != expected_value:
                        print(f"❌ 最终验证失败 {name}: 期望 '{expected_value}', 实际 '{actual_value}'")
                        return False
                    print(f"✅ 最终验证通过 {name}: {actual_value}")

            return True

        except Exception as e:
            print(f"❌ 表单填充异常: {e}")
            return False

    def generate_account(self, domain: str = None, include_pin: bool = False, pin: str = None) -> GeneratedAccount:
        """生成Cursor账号信息"""
        generator = get_account_generator()
        return generator.generate_account(
            domain=domain,  # 使用传入的域名或默认域名
            username_prefix="cursor",
            include_pin=include_pin,
            pin=pin,
            password_length=12
        )

    def register_with_generated_account(self, domain: str = None, include_pin: bool = False, pin: str = None,
                                       chrome_path: str = None, headless: bool = None) -> AutomationResult:
        """使用生成的账号信息进行注册"""
        try:
            # 生成账号信息
            generated_account = self.generate_account(domain=domain, include_pin=include_pin, pin=pin)

            # 生成随机姓名
            import random
            first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Quinn", "Blake", "Cameron"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            # 转换为注册数据
            reg_data = RegistrationData(
                email=generated_account.email,
                password=generated_account.password,
                username=generated_account.username,
                first_name=first_name,
                last_name=last_name
            )

            # 执行注册
            result = self.register(reg_data, chrome_path=chrome_path, headless=headless)

            # 添加生成的账号信息到结果
            if result.data is None:
                result.data = {}
            result.data.update({
                "generated_account": {
                    "username": generated_account.username,
                    "email": generated_account.email,
                    "password": generated_account.password,
                    "domain": generated_account.domain,
                    "pin": generated_account.pin,
                    "first_name": first_name,
                    "last_name": last_name,
                    "generated_at": generated_account.generated_at.isoformat()
                }
            })

            return result

        except Exception as e:
            return AutomationResult(
                status=AutomationStatus.FAILED,
                message=f"生成账号注册失败: {str(e)}",
                screenshot_path=self.take_screenshot("cursor_generated_register_failed")
            )
    
    def register(self, data: RegistrationData, chrome_path: str = None, headless: bool = None) -> AutomationResult:
        """注册Cursor账号"""
        if not self.init_browser(chrome_path=chrome_path, headless=headless):
            return AutomationResult(
                status=AutomationStatus.FAILED,
                message="浏览器初始化失败"
            )
        
        try:
            # 访问注册页面
            self.page.get(self.get_registration_url())
            self.random_delay(2, 4)
            
            # 等待页面加载 - 检查First name字段
            if not self.wait_for_element('input[name="first_name"]', timeout=10):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="注册页面加载失败",
                    screenshot_path=self.take_screenshot("cursor_register_page_load_failed")
                )
            
            # 使用改进的表单填充方法
            fields_dict = {
                'first_name': data.first_name,
                'last_name': data.last_name,
                'email': data.email
            }

            if not self.input_fields_with_validation(fields_dict):
                return AutomationResult(
                    status=AutomationStatus.FAILED,
                    message="表单填充失败",
                    screenshot_path=self.take_screenshot("cursor_register_form_failed")
                )
            
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
            
            # 点击Continue按钮（Cursor注册的提交按钮）
            print(f"🔘 正在查找并点击Continue按钮...")
            register_selectors = [
                'button[name="intent"][value="sign-up"]',  # Cursor特定的按钮
                'button[type="submit"]',
                'button:contains("Continue")',
                'button:contains("Sign Up")',
                'button:contains("Register")',
                'button:contains("Create Account")',
                'input[type="submit"]'
            ]

            register_clicked = False
            for i, selector in enumerate(register_selectors):
                print(f"🔍 尝试选择器 {i+1}/{len(register_selectors)}: {selector}")
                try:
                    if self.wait_for_element(selector, timeout=3):
                        print(f"✅ 找到按钮: {selector}")
                        if self.wait_and_click(selector):
                            print(f"✅ 成功点击Continue按钮")
                            register_clicked = True
                            break
                        else:
                            print(f"❌ 点击失败: {selector}")
                    else:
                        print(f"❌ 未找到: {selector}")
                except Exception as e:
                    print(f"❌ 选择器异常 {selector}: {e}")
                    continue
            
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
