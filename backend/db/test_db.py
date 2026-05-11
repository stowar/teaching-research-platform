# 只导入必要的包
from backend.db.connection import get_db_connection


# 极简测试：只测能不能连上数据库
def test():
    try:
        # 尝试连接
        conn = get_db_connection()
        print("✅ 数据库连接成功！")
        # 关闭连接
        conn.close()
    except Exception as e:
        print("❌ 连接失败：", e)

if __name__ == '__main__':
    test()