"""
Cursor自动化测试工具
"""
import time
import json
from datetime import datetime
from typing import Dict, List, Any

from automation.cursor_automation import CursorAutomation
from automation.base_automation import RegistrationData, LoginData, AutomationStatus
from utils.logger import get_logger


class CursorTester:
    """Cursor自动化测试器"""
    
    def __init__(self):
        self.automation = CursorAutomation()
        self.logger = get_logger()
        self.test_results = []
    
    def test_registration_flow(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """测试注册流程"""
        self.logger.info("开始测试Cursor注册流程")
        
        test_result = {
            "test_name": "Cursor注册流程测试",
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "steps": [],
            "errors": [],
            "screenshots": []
        }
        
        try:
            # 准备测试数据
            reg_data = RegistrationData(
                email=test_data.get("email", "test@example.com"),
                password=test_data.get("password", "TestPass123!"),
                username=test_data.get("username", "testuser"),
                first_name=test_data.get("first_name", "Test"),
                last_name=test_data.get("last_name", "User")
            )
            
            # 步骤1: 访问注册页面
            step1 = {
                "step": "访问注册页面",
                "url": self.automation.get_registration_url(),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            test_result["steps"].append(step1)
            
            # 步骤2: 执行注册
            self.logger.info("执行Cursor注册操作")
            result = self.automation.register(reg_data)
            
            step2 = {
                "step": "执行注册",
                "status": result.status.value,
                "message": result.message,
                "timestamp": datetime.now().isoformat()
            }
            
            if result.screenshot_path:
                step2["screenshot"] = result.screenshot_path
                test_result["screenshots"].append(result.screenshot_path)
            
            test_result["steps"].append(step2)
            
            # 分析结果
            if result.status == AutomationStatus.SUCCESS:
                test_result["status"] = "success"
                self.logger.info("Cursor注册测试成功")
            elif result.status == AutomationStatus.EMAIL_VERIFICATION_REQUIRED:
                test_result["status"] = "partial_success"
                test_result["note"] = "需要邮箱验证"
                self.logger.info("Cursor注册测试部分成功，需要邮箱验证")
            elif result.status == AutomationStatus.ACCOUNT_EXISTS:
                test_result["status"] = "expected_failure"
                test_result["note"] = "账号已存在（预期结果）"
                self.logger.info("Cursor注册测试：账号已存在")
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(result.message)
                self.logger.error(f"Cursor注册测试失败: {result.message}")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(str(e))
            self.logger.error(f"Cursor注册测试异常: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        self.test_results.append(test_result)
        return test_result
    
    def test_login_flow(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """测试登录流程"""
        self.logger.info("开始测试Cursor登录流程")
        
        test_result = {
            "test_name": "Cursor登录流程测试",
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "steps": [],
            "errors": [],
            "screenshots": []
        }
        
        try:
            # 准备测试数据
            login_data = LoginData(
                email=test_data.get("email", "test@example.com"),
                password=test_data.get("password", "TestPass123!"),
                remember_me=test_data.get("remember_me", False)
            )
            
            # 步骤1: 访问登录页面
            step1 = {
                "step": "访问登录页面",
                "url": self.automation.get_login_url(),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            test_result["steps"].append(step1)
            
            # 步骤2: 执行登录
            self.logger.info("执行Cursor登录操作")
            result = self.automation.login(login_data)
            
            step2 = {
                "step": "执行登录",
                "status": result.status.value,
                "message": result.message,
                "timestamp": datetime.now().isoformat()
            }
            
            if result.screenshot_path:
                step2["screenshot"] = result.screenshot_path
                test_result["screenshots"].append(result.screenshot_path)
            
            test_result["steps"].append(step2)
            
            # 分析结果
            if result.status == AutomationStatus.SUCCESS:
                test_result["status"] = "success"
                self.logger.info("Cursor登录测试成功")
            elif result.status == AutomationStatus.INVALID_CREDENTIALS:
                test_result["status"] = "expected_failure"
                test_result["note"] = "登录凭据无效（可能是预期结果）"
                self.logger.info("Cursor登录测试：凭据无效")
            elif result.status == AutomationStatus.CAPTCHA_REQUIRED:
                test_result["status"] = "partial_success"
                test_result["note"] = "需要验证码"
                self.logger.info("Cursor登录测试：需要验证码")
            else:
                test_result["status"] = "failed"
                test_result["errors"].append(result.message)
                self.logger.error(f"Cursor登录测试失败: {result.message}")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(str(e))
            self.logger.error(f"Cursor登录测试异常: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        self.test_results.append(test_result)
        return test_result
    
    def test_page_accessibility(self) -> Dict[str, Any]:
        """测试页面可访问性"""
        self.logger.info("开始测试Cursor页面可访问性")
        
        test_result = {
            "test_name": "Cursor页面可访问性测试",
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "pages": [],
            "errors": []
        }
        
        pages_to_test = [
            ("主页", "https://www.cursor.com/"),
            ("注册页", "https://authenticator.cursor.sh/sign-up"),
            ("登录页", "https://www.cursor.com/api/auth/login")
        ]
        
        try:
            if not self.automation.init_browser():
                raise Exception("浏览器初始化失败")
            
            for page_name, url in pages_to_test:
                page_result = {
                    "name": page_name,
                    "url": url,
                    "status": "testing",
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    # 访问页面
                    self.automation.page.get(url)
                    time.sleep(3)
                    
                    # 检查页面标题
                    title = self.automation.page.title
                    page_result["title"] = title
                    
                    # 检查页面是否加载成功
                    if "error" not in title.lower() and "404" not in title.lower():
                        page_result["status"] = "accessible"
                        self.logger.info(f"Cursor {page_name} 可访问")
                    else:
                        page_result["status"] = "error"
                        page_result["error"] = f"页面标题包含错误信息: {title}"
                        self.logger.warning(f"Cursor {page_name} 可能有问题: {title}")
                    
                    # 截图
                    screenshot_path = self.automation.take_screenshot(f"cursor_{page_name.lower()}_accessibility")
                    if screenshot_path:
                        page_result["screenshot"] = screenshot_path
                    
                except Exception as e:
                    page_result["status"] = "error"
                    page_result["error"] = str(e)
                    self.logger.error(f"测试Cursor {page_name} 失败: {e}")
                
                test_result["pages"].append(page_result)
            
            # 总体状态
            accessible_count = len([p for p in test_result["pages"] if p["status"] == "accessible"])
            total_count = len(test_result["pages"])
            
            if accessible_count == total_count:
                test_result["status"] = "success"
            elif accessible_count > 0:
                test_result["status"] = "partial_success"
            else:
                test_result["status"] = "failed"
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(str(e))
            self.logger.error(f"Cursor页面可访问性测试异常: {e}")
        
        finally:
            self.automation.close_browser()
        
        test_result["end_time"] = datetime.now().isoformat()
        self.test_results.append(test_result)
        return test_result
    
    def run_comprehensive_test(self, test_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行综合测试"""
        self.logger.info("开始Cursor综合测试")
        
        if test_config is None:
            test_config = {
                "email": "test@example.com",
                "password": "TestPass123!",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "remember_me": False
            }
        
        comprehensive_result = {
            "test_suite": "Cursor综合测试",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
        
        # 测试1: 页面可访问性
        accessibility_result = self.test_page_accessibility()
        comprehensive_result["tests"].append(accessibility_result)
        
        # 测试2: 注册流程
        registration_result = self.test_registration_flow(test_config)
        comprehensive_result["tests"].append(registration_result)
        
        # 测试3: 登录流程
        login_result = self.test_login_flow(test_config)
        comprehensive_result["tests"].append(login_result)
        
        # 生成摘要
        total_tests = len(comprehensive_result["tests"])
        successful_tests = len([t for t in comprehensive_result["tests"] if t["status"] == "success"])
        partial_tests = len([t for t in comprehensive_result["tests"] if t["status"] == "partial_success"])
        failed_tests = len([t for t in comprehensive_result["tests"] if t["status"] in ["failed", "error"]])
        
        comprehensive_result["summary"] = {
            "total_tests": total_tests,
            "successful": successful_tests,
            "partial_success": partial_tests,
            "failed": failed_tests,
            "success_rate": f"{(successful_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
        }
        
        comprehensive_result["end_time"] = datetime.now().isoformat()
        
        # 保存测试报告
        self.save_test_report(comprehensive_result)
        
        self.logger.info(f"Cursor综合测试完成，成功率: {comprehensive_result['summary']['success_rate']}")
        return comprehensive_result
    
    def save_test_report(self, test_result: Dict[str, Any]):
        """保存测试报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cursor_test_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(test_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Cursor测试报告已保存: {filename}")
            
        except Exception as e:
            self.logger.error(f"保存Cursor测试报告失败: {e}")
    
    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        if not self.test_results:
            return {"message": "暂无测试结果"}
        
        total_tests = len(self.test_results)
        successful_tests = len([t for t in self.test_results if t["status"] == "success"])
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{(successful_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
            "last_test_time": self.test_results[-1]["end_time"] if self.test_results else None
        }


def main():
    """主函数 - 运行Cursor测试"""
    print("🎯 Cursor自动化测试工具")
    print("=" * 50)
    
    tester = CursorTester()
    
    # 运行综合测试
    result = tester.run_comprehensive_test()
    
    # 显示结果
    print(f"\n📊 测试结果摘要:")
    print(f"总测试数: {result['summary']['total_tests']}")
    print(f"成功: {result['summary']['successful']}")
    print(f"部分成功: {result['summary']['partial_success']}")
    print(f"失败: {result['summary']['failed']}")
    print(f"成功率: {result['summary']['success_rate']}")
    
    print(f"\n📁 详细报告已保存")
    print("🎉 Cursor测试完成！")


if __name__ == "__main__":
    main()
