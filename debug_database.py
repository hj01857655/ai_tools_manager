#!/usr/bin/env python3
"""
调试数据库问题
"""
import sqlite3
import os

def debug_database():
    """调试数据库"""
    db_path = "data/accounts.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看表结构
        cursor.execute("PRAGMA table_info(accounts)")
        columns = cursor.fetchall()
        print("表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 查看数据
        cursor.execute("SELECT id, name, account_type, email FROM accounts LIMIT 5")
        accounts = cursor.fetchall()
        print(f"\n前5条数据:")
        for acc in accounts:
            print(f"  ID: {acc[0]}, Name: {acc[1]}, Type: {acc[2]}, Email: {acc[3]}")
        
        # 查看所有不同的account_type值
        cursor.execute("SELECT DISTINCT account_type FROM accounts")
        types = cursor.fetchall()
        print(f"\n所有account_type值:")
        for t in types:
            print(f"  '{t[0]}'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")

if __name__ == "__main__":
    debug_database()
