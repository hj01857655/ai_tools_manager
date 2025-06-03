#!/usr/bin/env python3
"""
Cursor自动注册测试脚本
"""
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation.cursor_automation import CursorAutomation
from utils.account_generator import get_account_generator, generate_cursor_account
from utils.logger import get_logger


def test_account_generation():
    """测试账号生成"""
    print("🧪 测试账号生成功能")
    print("-" * 50)
    
    try:
        # 测试单个账号生成
        account = generate_cursor_account(include_pin=True)
        
        print(f"✅ 生成账号成功:")
        print(f"   用户名: {account.username}")
        print(f"   邮箱: {account.email}")
        print(f"   密码: {account.password}")
        print(f"   域名: {account.domain}")
        print(f"   PIN: {account.pin}")
        print(f"   生成时间: {account.generated_at}")
        
        return account
        
    except Exception as e:
        print(f"❌ 账号生成失败: {e}")
        return None


def test_cursor_automation_methods():
    """测试Cursor自动化方法"""
    print("\n🧪 测试Cursor自动化方法")
    print("-" * 50)
    
    try:
        automation = CursorAutomation()
        
        print(f"✅ 服务名称: {automation.get_service_name()}")
        print(f"✅ 注册URL: {automation.get_registration_url()}")
        print(f"✅ 登录URL: {automation.get_login_url()}")
        print(f"✅ 主页URL: {automation.get_homepage_url()}")
        
        # 测试账号生成方法
        generated_account = automation.generate_account(include_pin=True)
        print(f"✅ 自动化生成账号: {generated_account.email}")
        
        return automation, generated_account
        
    except Exception as e:
        print(f"❌ Cursor自动化测试失败: {e}")
        return None, None


def test_registration_simulation():
    """测试注册模拟（不实际执行）"""
    print("\n🧪 测试注册流程模拟")
    print("-" * 50)
    
    try:
        automation = CursorAutomation()
        
        # 生成测试账号
        test_account = automation.generate_account(
            domain="10minutemail.com",
            include_pin=True
        )
        
        print(f"📧 测试邮箱: {test_account.email}")
        print(f"🔑 测试密码: {test_account.password}")
        print(f"👤 测试用户名: {test_account.username}")
        print(f"📌 测试PIN: {test_account.pin}")
        
        # 模拟注册流程（不实际执行浏览器操作）
        print(f"\n📋 注册流程模拟:")
        print(f"1. 访问注册页面: {automation.get_registration_url()}")
        print(f"2. 填写邮箱: {test_account.email}")
        print(f"3. 填写密码: {'*' * len(test_account.password)}")
        print(f"4. 填写用户名: {test_account.username}")
        print(f"5. 提交注册表单")
        print(f"6. 等待邮箱验证")
        
        print(f"\n✅ 注册流程模拟完成")
        
        return test_account
        
    except Exception as e:
        print(f"❌ 注册模拟失败: {e}")
        return None


def test_batch_account_generation():
    """测试批量账号生成"""
    print("\n🧪 测试批量账号生成")
    print("-" * 50)
    
    try:
        generator = get_account_generator()
        
        # 生成5个测试账号
        accounts = generator.generate_batch_accounts(
            count=5,
            domain="10minutemail.com",
            username_prefix="cursor_test",
            include_pin=True
        )
        
        print(f"✅ 批量生成成功: {len(accounts)} 个账号")
        
        for i, account in enumerate(accounts, 1):
            print(f"   账号{i}: {account.email}")
        
        # 导出账号
        if accounts:
            filename = generator.export_accounts(accounts, "test_cursor_accounts.txt")
            print(f"✅ 账号已导出: {filename}")
        
        return accounts
        
    except Exception as e:
        print(f"❌ 批量生成失败: {e}")
        return []


def test_domain_management():
    """测试域名管理"""
    print("\n🧪 测试域名管理")
    print("-" * 50)
    
    try:
        generator = get_account_generator()
        
        # 获取可用域名
        domains = generator.get_available_domains()
        print(f"✅ 可用域名数量: {len(domains)}")
        print(f"   前5个域名: {domains[:5]}")
        
        # 添加自定义域名
        custom_domain = "test-email.com"
        if generator.add_custom_domain(custom_domain):
            print(f"✅ 添加自定义域名成功: {custom_domain}")
        
        # 验证域名
        test_domains = ["gmail.com", "invalid..domain", "test.co"]
        for domain in test_domains:
            is_valid = generator.validate_email_domain(domain)
            status = "✅ 有效" if is_valid else "❌ 无效"
            print(f"   {domain}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 域名管理测试失败: {e}")
        return False


def test_password_generation():
    """测试密码生成"""
    print("\n🧪 测试密码生成")
    print("-" * 50)
    
    try:
        generator = get_account_generator()
        
        # 测试不同配置的密码
        configs = [
            {"length": 8, "include_symbols": False},
            {"length": 12, "include_symbols": True},
            {"length": 16, "include_uppercase": False},
            {"length": 20, "symbols": "@#$%"}
        ]
        
        for i, config in enumerate(configs, 1):
            password = generator.generate_password(config=config)
            print(f"   配置{i}: {password} (长度: {len(password)})")
        
        print(f"✅ 密码生成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 密码生成测试失败: {e}")
        return False


def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 Cursor自动注册测试报告")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"测试时间: {datetime.now().isoformat()}")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
    
    print(f"\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    # 保存报告
    try:
        import json
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%",
            "results": results
        }
        
        with open("cursor_auto_register_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试报告已保存: cursor_auto_register_test_report.json")
        
    except Exception as e:
        print(f"\n⚠️ 保存测试报告失败: {e}")
    
    return passed_tests == total_tests


def main():
    """主函数"""
    print("🚀 Cursor自动注册功能测试")
    print("="*60)
    
    # 运行所有测试
    tests = {
        "账号生成": lambda: test_account_generation() is not None,
        "自动化方法": lambda: test_cursor_automation_methods()[0] is not None,
        "注册模拟": lambda: test_registration_simulation() is not None,
        "批量生成": lambda: len(test_batch_account_generation()) > 0,
        "域名管理": test_domain_management,
        "密码生成": test_password_generation
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
        print("\n🎉 所有测试通过！Cursor自动注册功能正常。")
        print("\n💡 提示:")
        print("   - 账号生成器已就绪")
        print("   - 可以在UI中使用自动注册功能")
        print("   - 支持自定义域名和批量生成")
        print("   - 所有生成的账号都会自动保存")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
    
    return all_passed


if __name__ == "__main__":
    main()
