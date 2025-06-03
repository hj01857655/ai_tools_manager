#!/usr/bin/env python3
"""
测试应用程序功能
"""

def test_database():
    """测试数据库功能"""
    print("🔍 测试数据库连接...")
    try:
        from models.database import DatabaseManager
        db = DatabaseManager()
        print("✅ 数据库连接成功")
        
        # 测试获取所有账号
        accounts = db.get_all_accounts()
        print(f"📊 当前账号数量: {len(accounts)}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_account_creation():
    """测试账号创建"""
    print("\n🔍 测试账号创建...")
    try:
        from models.database import DatabaseManager
        from models.account import Account, AccountType, AccountStatus
        
        db = DatabaseManager()
        
        # 创建测试账号
        test_account = Account(
            name="测试Cursor账号",
            account_type=AccountType.CURSOR,
            email="test@example.com",
            username="testuser",
            password="testpass123",
            status=AccountStatus.ACTIVE,
            subscription_type="Pro",
            tags="测试,开发"
        )
        
        account_id = db.add_account(test_account)
        print(f"✅ 账号创建成功，ID: {account_id}")
        
        # 验证账号
        accounts = db.get_all_accounts()
        cursor_accounts = [acc for acc in accounts if acc.account_type == AccountType.CURSOR]
        print(f"📊 Cursor账号数量: {len(cursor_accounts)}")
        
        return True
    except Exception as e:
        print(f"❌ 账号创建测试失败: {e}")
        return False

def test_automation_support():
    """测试自动化支持"""
    print("\n🔍 测试自动化功能...")
    try:
        from automation.automation_manager import is_automation_supported
        from models.account import AccountType
        
        # 测试支持的工具
        tools = [AccountType.CURSOR, AccountType.WINDSURF, AccountType.AUGMENT]
        
        for tool in tools:
            supported = is_automation_supported(tool)
            status = "✅ 支持" if supported else "❌ 不支持"
            print(f"  {tool.value}: {status}")
        
        return True
    except Exception as e:
        print(f"❌ 自动化测试失败: {e}")
        return False

def test_ui_components():
    """测试UI组件"""
    print("\n🔍 测试UI组件...")
    try:
        # 测试侧边导航
        from ui.sidebar_navigation import SidebarNavigation
        print("✅ 侧边导航组件正常")
        
        # 测试账号页面
        from ui.account_page import AccountPage
        print("✅ 账号页面组件正常")
        
        # 测试自动化对话框
        from ui.automation_dialog import AutomationDialog
        print("✅ 自动化对话框组件正常")
        
        return True
    except Exception as e:
        print(f"❌ UI组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 AI工具管理器功能测试")
    print("=" * 50)
    
    tests = [
        ("数据库功能", test_database),
        ("账号创建", test_account_creation),
        ("自动化支持", test_automation_support),
        ("UI组件", test_ui_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用程序功能正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return passed == total

if __name__ == "__main__":
    main()
