#!/usr/bin/env python3
"""
DrissionPage使用测试脚本
验证正确的导入和使用方式
"""
import time
import os
from datetime import datetime


def test_drissionpage_import():
    """测试DrissionPage导入"""
    print("🔍 测试DrissionPage导入...")
    
    try:
        from DrissionPage import ChromiumOptions, Chromium
        print("✅ DrissionPage导入成功")
        print(f"   ChromiumOptions: {ChromiumOptions}")
        print(f"   Chromium: {Chromium}")
        return True
    except ImportError as e:
        print(f"❌ DrissionPage导入失败: {e}")
        print("💡 请安装DrissionPage: pip install DrissionPage>=4.0.0")
        return False
    except Exception as e:
        print(f"❌ DrissionPage导入异常: {e}")
        return False


def test_browser_creation():
    """测试浏览器创建"""
    print("\n🔍 测试浏览器创建...")
    
    try:
        from DrissionPage import ChromiumOptions, Chromium
        
        # 配置浏览器选项
        options = ChromiumOptions()
        options.headless()  # 无头模式
        
        # 设置用户代理
        options.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 禁用图片加载
        options.set_pref('profile.managed_default_content_settings.images', 2)
        
        print("✅ 浏览器选项配置成功")
        
        # 创建浏览器
        browser = Chromium(addr_or_opts=options)
        page = browser.latest_tab
        
        print("✅ 浏览器创建成功")
        print(f"   浏览器对象: {browser}")
        print(f"   页面对象: {page}")
        
        # 关闭浏览器
        browser.quit()
        print("✅ 浏览器关闭成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 浏览器创建失败: {e}")
        return False


def test_page_navigation():
    """测试页面导航"""
    print("\n🔍 测试页面导航...")
    
    try:
        from DrissionPage import ChromiumOptions, Chromium
        
        # 配置浏览器
        options = ChromiumOptions()
        options.headless()
        
        browser = Chromium(addr_or_opts=options)
        page = browser.latest_tab
        
        # 设置超时
        page.set.timeouts(base=10)
        
        # 访问测试页面
        test_url = "https://www.cursor.com/"
        print(f"📍 访问页面: {test_url}")
        
        page.get(test_url)
        time.sleep(3)
        
        # 获取页面信息
        title = page.title
        url = page.url
        
        print(f"✅ 页面访问成功")
        print(f"   标题: {title}")
        print(f"   URL: {url}")
        
        # 截图测试
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        screenshot_path = os.path.join(screenshots_dir, f"test_{int(time.time())}.png")
        page.get_screenshot(path=screenshot_path)
        
        if os.path.exists(screenshot_path):
            print(f"✅ 截图保存成功: {screenshot_path}")
        else:
            print("⚠️ 截图保存失败")
        
        # 关闭浏览器
        browser.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ 页面导航测试失败: {e}")
        return False


def test_element_interaction():
    """测试元素交互"""
    print("\n🔍 测试元素交互...")
    
    try:
        from DrissionPage import ChromiumOptions, Chromium
        
        # 配置浏览器
        options = ChromiumOptions()
        options.headless()
        
        browser = Chromium(addr_or_opts=options)
        page = browser.latest_tab
        
        # 访问测试页面
        page.get("https://www.cursor.com/")
        time.sleep(3)
        
        # 测试元素查找
        selectors_to_test = [
            'title',
            'body',
            'header',
            'nav',
            'a',
            'button'
        ]
        
        found_elements = 0
        for selector in selectors_to_test:
            try:
                element = page.ele(selector, timeout=2)
                if element:
                    found_elements += 1
                    print(f"✅ 找到元素: {selector}")
                else:
                    print(f"⚠️ 未找到元素: {selector}")
            except Exception as e:
                print(f"❌ 查找元素失败 {selector}: {e}")
        
        print(f"📊 元素查找结果: {found_elements}/{len(selectors_to_test)}")
        
        # 关闭浏览器
        browser.quit()
        
        return found_elements > 0
        
    except Exception as e:
        print(f"❌ 元素交互测试失败: {e}")
        return False


def test_automation_base_class():
    """测试自动化基类"""
    print("\n🔍 测试自动化基类...")
    
    try:
        from automation.base_automation import BaseAutomation, AutomationResult, AutomationStatus
        
        # 创建测试类
        class TestAutomation(BaseAutomation):
            def get_service_name(self) -> str:
                return "Test"
            
            def get_registration_url(self) -> str:
                return "https://www.cursor.com/"
            
            def get_login_url(self) -> str:
                return "https://www.cursor.com/"
            
            def register(self, data) -> AutomationResult:
                return AutomationResult(
                    status=AutomationStatus.SUCCESS,
                    message="测试注册成功"
                )
            
            def login(self, data) -> AutomationResult:
                return AutomationResult(
                    status=AutomationStatus.SUCCESS,
                    message="测试登录成功"
                )
        
        # 测试基类功能
        automation = TestAutomation(headless=True, timeout=10)
        
        print("✅ 自动化基类创建成功")
        
        # 测试浏览器初始化
        if automation.init_browser():
            print("✅ 浏览器初始化成功")
            
            # 测试页面访问
            automation.page.get("https://www.cursor.com/")
            time.sleep(2)
            
            # 测试截图
            screenshot_path = automation.take_screenshot("test_base_class")
            if screenshot_path and os.path.exists(screenshot_path):
                print(f"✅ 截图功能正常: {screenshot_path}")
            else:
                print("⚠️ 截图功能异常")
            
            # 测试元素等待
            if automation.wait_for_element('body', timeout=5):
                print("✅ 元素等待功能正常")
            else:
                print("⚠️ 元素等待功能异常")
            
            # 关闭浏览器
            automation.close_browser()
            print("✅ 浏览器关闭成功")
            
        else:
            print("❌ 浏览器初始化失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 自动化基类测试失败: {e}")
        return False


def test_cursor_automation():
    """测试Cursor自动化"""
    print("\n🔍 测试Cursor自动化...")
    
    try:
        from automation.cursor_automation import CursorAutomation
        
        automation = CursorAutomation()
        
        print("✅ Cursor自动化类创建成功")
        print(f"   服务名称: {automation.get_service_name()}")
        print(f"   注册URL: {automation.get_registration_url()}")
        print(f"   登录URL: {automation.get_login_url()}")
        
        # 测试URL有效性
        expected_urls = {
            'registration': 'https://authenticator.cursor.sh/sign-up',
            'login': 'https://www.cursor.com/api/auth/login'
        }
        
        if automation.get_registration_url() == expected_urls['registration']:
            print("✅ 注册URL正确")
        else:
            print(f"⚠️ 注册URL不匹配: {automation.get_registration_url()}")
        
        if automation.get_login_url() == expected_urls['login']:
            print("✅ 登录URL正确")
        else:
            print(f"⚠️ 登录URL不匹配: {automation.get_login_url()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cursor自动化测试失败: {e}")
        return False


def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 DrissionPage测试报告")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%",
        "results": results
    }
    
    try:
        import json
        with open("drissionpage_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 测试报告已保存: drissionpage_test_report.json")
    except Exception as e:
        print(f"\n⚠️ 保存测试报告失败: {e}")
    
    return passed_tests == total_tests


def main():
    """主函数"""
    print("🚀 DrissionPage使用测试")
    print("="*60)
    
    # 运行所有测试
    tests = {
        "DrissionPage导入": test_drissionpage_import,
        "浏览器创建": test_browser_creation,
        "页面导航": test_page_navigation,
        "元素交互": test_element_interaction,
        "自动化基类": test_automation_base_class,
        "Cursor自动化": test_cursor_automation
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        print(f"\n🧪 运行测试: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results[test_name] = False
    
    # 生成报告
    all_passed = generate_test_report(results)
    
    if all_passed:
        print("\n🎉 所有测试通过！DrissionPage配置正确。")
    else:
        print("\n⚠️ 部分测试失败，请检查DrissionPage配置。")
    
    return all_passed


if __name__ == "__main__":
    main()
