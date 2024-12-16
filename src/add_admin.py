import hashlib
from database import Database

def add_admin():
    try:
        # 管理员账号信息
        username = 'admin'
        password = 'admin123'
        role = 'admin'
        
        # 对密码进行哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 检查管理员账号是否已存在
        check_query = "SELECT user_id FROM Users WHERE username = %s"
        result = Database.execute_query(check_query, (username,))
        
        if result:
            print("管理员账号已存在！")
            return
            
        # 创建管理员账号
        query = """
            INSERT INTO Users (username, password, role)
            VALUES (%s, %s, %s)
            RETURNING user_id
        """
        result = Database.execute_query(query, (username, hashed_password, role))
        
        if result:
            print("管理员账号创建成功！")
            print("用户名：admin")
            print("密码：admin123")
        else:
            print("管理员账号创建失败！")
            
    except Exception as e:
        print(f"创建管理员账号时出错：{str(e)}")

if __name__ == "__main__":
    add_admin() 