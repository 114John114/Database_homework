from database import Database

def check_db():
    try:
        Database.initialize()
        
        # 检查用户表
        print("\n当前用户列表：")
        print("=" * 80)
        print(f"{'ID':<5} {'用户名':<20} {'角色':<10} {'创建时间':<20} {'最后登录':<20}")
        print("-" * 80)
        
        query = """
            SELECT user_id, username, role, created_at, last_login
            FROM Users
            ORDER BY user_id
        """
        users = Database.execute_query(query)
        
        for user in users:
            user_id, username, role, created_at, last_login = user
            created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "N/A"
            login_str = last_login.strftime("%Y-%m-%d %H:%M:%S") if last_login else "从未登录"
            print(f"{user_id:<5} {username:<20} {role:<10} {created_str:<20} {login_str:<20}")
            
        print("=" * 80)
            
    except Exception as e:
        print(f"检查数据库失败：{str(e)}")

if __name__ == "__main__":
    check_db() 