"""数据库迁移脚本 - 为Essay表添加topic_analysis字段"""
import sqlite3
import os
import sys

# 获取数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'k12_platform.db')

def migrate():
    """执行迁移"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(essays)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'topic_analysis' not in columns:
            print("正在添加 topic_analysis 字段...")
            cursor.execute("ALTER TABLE essays ADD COLUMN topic_analysis TEXT")
            conn.commit()
            print("✅ 字段添加成功！")
        else:
            print("ℹ️ topic_analysis 字段已存在，无需迁移")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate()
    print("迁移完成！")
