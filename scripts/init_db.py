import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.connection import  execute_update
from backend.core.config import settings

def execute_sql_file(file_path):
    """执行SQL文件"""
    with open(file_path,"r",encoding="utf-8") as f:
        sql_content = f.read()
    # print(sql_content)
    # 分割SQL语句
    sql_statement = sql_content.split(";")
    for sql in sql_statement:
        sql = sql.strip()
        if sql and not sql.startswith('--'):
            try:
                execute_update(sql)
                print(f"执行成功:{sql[:50]}...")
            except Exception as e:
                print(f"执行失败:{sql[:50]}...")
                print(f"错误信息:{e}")

if __name__ == '__main__':
    print("开始初始化数据库...")
    # 执行建表SQL
    execute_sql_file(os.path.join(settings.BASE_DIR, r"docs/database/create_tables.sql"))
    print("数据库初始化完成！")
