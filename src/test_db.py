from database import Database

def test_db():
    try:
        # 测试连接
        Database.initialize()
        
        # 测试查询
        result = Database.execute_query("SELECT version()")
        print("数据库连接成功！")
        print(f"数据库版本: {result[0][0]}")
        
        # 测试表是否存在
        tables = ['Users', 'Courses', 'Course_Chapters', 'Learning_Progress', 
                 'Test_Questions', 'Question_Options', 'Test_Scores', 
                 'Forum_Posts', 'Post_Replies', 'User_Favorites', 'Course_Ratings']
        
        for table in tables:
            try:
                result = Database.execute_query(f"SELECT COUNT(*) FROM {table}")
                print(f"表 {table} 存在，当前有 {result[0][0]} 条记录")
            except Exception as e:
                print(f"表 {table} 检查失败: {e}")
                
    except Exception as e:
        print(f"数据库测试失败: {e}")

if __name__ == '__main__':
    test_db() 