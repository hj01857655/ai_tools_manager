"""
自动化管理器
统一管理AI工具的自动化注册和登录
"""
from typing import Dict, Type, Optional
from models.account import AccountType
from automation.base_automation import BaseAutomation, AutomationResult, AutomationStatus, RegistrationData, LoginData
from automation.cursor_automation import CursorAutomation
from automation.windsurf_automation import WindsurfAutomation
from automation.augment_automation import AugmentAutomation


class AutomationManager:
    """自动化管理器"""
    
    def __init__(self):
        # 注册自动化类映射
        self._automation_classes: Dict[AccountType, Type[BaseAutomation]] = {
            AccountType.CURSOR: CursorAutomation,
            AccountType.WINDSURF: WindsurfAutomation,
            AccountType.AUGMENT: AugmentAutomation,
        }
        
        # 支持的账号类型
        self._supported_types = set(self._automation_classes.keys())
    
    def is_supported(self, account_type: AccountType) -> bool:
        """检查是否支持自动化"""
        return account_type in self._supported_types
    
    def get_supported_types(self) -> list:
        """获取支持的账号类型列表"""
        return list(self._supported_types)
    
    def create_automation(self, account_type: AccountType, headless: bool = False, timeout: int = 30) -> Optional[BaseAutomation]:
        """创建自动化实例"""
        if not self.is_supported(account_type):
            return None
        
        automation_class = self._automation_classes[account_type]
        return automation_class(headless=headless, timeout=timeout)
    
    def register_account(
        self, 
        account_type: AccountType, 
        registration_data: RegistrationData,
        headless: bool = False,
        timeout: int = 30
    ) -> AutomationResult:
        """自动注册账号"""
        automation = self.create_automation(account_type, headless, timeout)
        if not automation:
            return AutomationResult(
                status=AutomationStatus.FAILED,
                message=f"不支持 {account_type.value} 的自动注册"
            )
        
        try:
            return automation.register(registration_data)
        except Exception as e:
            return AutomationResult(
                status=AutomationStatus.UNKNOWN_ERROR,
                message=f"自动注册过程中发生错误: {str(e)}"
            )
    
    def login_account(
        self, 
        account_type: AccountType, 
        login_data: LoginData,
        headless: bool = False,
        timeout: int = 30
    ) -> AutomationResult:
        """自动登录账号"""
        automation = self.create_automation(account_type, headless, timeout)
        if not automation:
            return AutomationResult(
                status=AutomationStatus.FAILED,
                message=f"不支持 {account_type.value} 的自动登录"
            )
        
        try:
            return automation.login(login_data)
        except Exception as e:
            return AutomationResult(
                status=AutomationStatus.UNKNOWN_ERROR,
                message=f"自动登录过程中发生错误: {str(e)}"
            )
    
    def get_service_info(self, account_type: AccountType) -> Optional[Dict[str, str]]:
        """获取服务信息"""
        automation = self.create_automation(account_type)
        if not automation:
            return None
        
        return {
            "service_name": automation.get_service_name(),
            "registration_url": automation.get_registration_url(),
            "login_url": automation.get_login_url()
        }
    
    def batch_register(
        self, 
        registrations: list,
        headless: bool = True,
        timeout: int = 30
    ) -> Dict[str, AutomationResult]:
        """批量注册账号"""
        results = {}
        
        for i, (account_type, registration_data) in enumerate(registrations):
            try:
                result = self.register_account(
                    account_type, 
                    registration_data, 
                    headless, 
                    timeout
                )
                results[f"{account_type.value}_{i}"] = result
                
                # 如果需要手动干预，暂停批量操作
                if result.needs_manual_intervention:
                    break
                    
            except Exception as e:
                results[f"{account_type.value}_{i}"] = AutomationResult(
                    status=AutomationStatus.UNKNOWN_ERROR,
                    message=f"批量注册错误: {str(e)}"
                )
        
        return results
    
    def batch_login(
        self, 
        logins: list,
        headless: bool = True,
        timeout: int = 30
    ) -> Dict[str, AutomationResult]:
        """批量登录账号"""
        results = {}
        
        for i, (account_type, login_data) in enumerate(logins):
            try:
                result = self.login_account(
                    account_type, 
                    login_data, 
                    headless, 
                    timeout
                )
                results[f"{account_type.value}_{i}"] = result
                
                # 如果需要手动干预，暂停批量操作
                if result.needs_manual_intervention:
                    break
                    
            except Exception as e:
                results[f"{account_type.value}_{i}"] = AutomationResult(
                    status=AutomationStatus.UNKNOWN_ERROR,
                    message=f"批量登录错误: {str(e)}"
                )
        
        return results


# 全局自动化管理器实例
_automation_manager = None


def get_automation_manager() -> AutomationManager:
    """获取全局自动化管理器实例"""
    global _automation_manager
    if _automation_manager is None:
        _automation_manager = AutomationManager()
    return _automation_manager


# 便捷函数
def is_automation_supported(account_type: AccountType) -> bool:
    """检查是否支持自动化"""
    return get_automation_manager().is_supported(account_type)


def get_supported_automation_types() -> list:
    """获取支持自动化的账号类型"""
    return get_automation_manager().get_supported_types()


def auto_register(account_type: AccountType, email: str, password: str, **kwargs) -> AutomationResult:
    """快速自动注册"""
    registration_data = RegistrationData(
        email=email,
        password=password,
        username=kwargs.get('username'),
        first_name=kwargs.get('first_name'),
        last_name=kwargs.get('last_name'),
        phone=kwargs.get('phone'),
        company=kwargs.get('company')
    )
    
    return get_automation_manager().register_account(
        account_type, 
        registration_data,
        headless=kwargs.get('headless', False),
        timeout=kwargs.get('timeout', 30)
    )


def auto_login(account_type: AccountType, email: str, password: str, **kwargs) -> AutomationResult:
    """快速自动登录"""
    login_data = LoginData(
        email=email,
        password=password,
        remember_me=kwargs.get('remember_me', False)
    )
    
    return get_automation_manager().login_account(
        account_type, 
        login_data,
        headless=kwargs.get('headless', False),
        timeout=kwargs.get('timeout', 30)
    )
