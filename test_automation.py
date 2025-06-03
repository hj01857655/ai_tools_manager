#!/usr/bin/env python3
"""
测试自动化功能
"""

def test_imports():
    """测试导入"""
    print("测试基础导入...")
    
    try:
        from models.account import AccountType
        print("✅ 账号模型导入成功")
    except ImportError as e:
        print(f"❌ 账号模型导入失败: {e}")
        return False
    
    try:
        from automation.base_automation import BaseAutomation, AutomationResult, AutomationStatus
        print("✅ 自动化基类导入成功")
    except ImportError as e:
        print(f"❌ 自动化基类导入失败: {e}")
        return False
    
    try:
        from automation.automation_manager import get_automation_manager
        print("✅ 自动化管理器导入成功")
    except ImportError as e:
        print(f"❌ 自动化管理器导入失败: {e}")
        return False
    
    return True

def test_automation_manager():
    """测试自动化管理器"""
    print("\n测试自动化管理器...")
    
    try:
        from automation.automation_manager import get_automation_manager
        from models.account import AccountType
        
        manager = get_automation_manager()
        print(f"✅ 自动化管理器创建成功")
        
        # 测试支持的类型
        supported_types = manager.get_supported_types()
        print(f"✅ 支持的AI工具类型: {[t.value for t in supported_types]}")
        
        # 测试每个支持的类型
        for account_type in supported_types:
            is_supported = manager.is_supported(account_type)
            print(f"✅ {account_type.value}: {'支持' if is_supported else '不支持'}")
            
            # 获取服务信息
            service_info = manager.get_service_info(account_type)
            if service_info:
                print(f"   - 注册URL: {service_info['registration_url']}")
                print(f"   - 登录URL: {service_info['login_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 自动化管理器测试失败: {e}")
        return False

def test_drissionpage():
    """测试DrissionPage"""
    print("\n测试DrissionPage...")
    
    try:
        import DrissionPage
        print(f"✅ DrissionPage已安装，版本: {DrissionPage.__version__}")
        return True
    except ImportError:
        print("❌ DrissionPage未安装")
        print("请运行: pip install DrissionPage")
        return False
    except Exception as e:
        print(f"❌ DrissionPage测试失败: {e}")
        return False

def test_ui_imports():
    """测试UI导入"""
    print("\n测试UI组件导入...")
    
    try:
        from ui.automation_dialog import AutomationDialog
        print("✅ 自动化对话框导入成功")
        return True
    except ImportError as e:
        print(f"❌ 自动化对话框导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🤖 AI工具自动化功能测试")
    print("=" * 50)
    
    all_passed = True
    
    # 测试基础导入
    if not test_imports():
        all_passed = False
    
    # 测试自动化管理器
    if not test_automation_manager():
        all_passed = False
    
    # 测试DrissionPage
    if not test_drissionpage():
        all_passed = False
    
    # 测试UI导入
    if not test_ui_imports():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！自动化功能可以使用。")
    else:
        print("⚠️ 部分测试失败，请检查相关依赖。")
    
    return all_passed

if __name__ == "__main__":
    main()
