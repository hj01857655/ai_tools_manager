#!/usr/bin/env python3
"""
修复数据库问题
"""
import sqlite3
import os

def fix_database():
    """修复数据库"""
    db_path = "data/accounts.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，无需修复")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看当前数据
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()
        print(f"当前账号数量: {len(accounts)}")
        
        # 删除有问题的数据
        cursor.execute("DELETE FROM accounts WHERE account_type NOT IN ('CURSOR', 'WINDSURF', 'AUGMENT', 'GITHUB_COPILOT', 'CLAUDE', 'CHATGPT', 'OPENAI_API', 'ANTHROPIC_API', 'OTHER')")
        deleted = cursor.rowcount
        print(f"删除无效账号: {deleted}")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("✅ 数据库修复完成")
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")

if __name__ == "__main__":
    fix_database()
