#!/usr/bin/env python3
"""
清理数据库
"""
import os
import shutil

def clean_database():
    """清理数据库"""
    # 删除数据目录
    if os.path.exists("data"):
        print("删除现有数据目录...")
        shutil.rmtree("data")
        print("✅ 数据目录已删除")
    
    # 删除配置文件
    if os.path.exists("config.json"):
        print("删除配置文件...")
        os.remove("config.json")
        print("✅ 配置文件已删除")
    
    print("🎉 数据库清理完成！下次启动将创建全新的数据库。")

if __name__ == "__main__":
    clean_database()
