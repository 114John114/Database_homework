from database import Database

def add_test_course():
    try:
        Database.initialize()
        
        # 添加测试课程
        course_query = """
            INSERT INTO Courses (title, description, instructor_id, difficulty_level, status)
            VALUES ('Python编程基础', '学习Python编程的基础知识', 1, 'beginner', 'active')
            RETURNING course_id
        """
        result = Database.execute_query(course_query)
        
        if result:
            course_id = result[0][0]
            
            # 添加课程章节
            chapters = [
                ('第一章：Python简介', '了解Python的基本概念', 1),
                ('第二章：基础语法', 'Python的基本语法规则', 2),
                ('第三章：数据类型', 'Python的主要数据类型', 3)
            ]
            
            for title, desc, seq in chapters:
                chapter_query = """
                    INSERT INTO Course_Chapters (course_id, title, description, sequence_number)
                    VALUES (%s, %s, %s, %s)
                """
                Database.execute_query(chapter_query, (course_id, title, desc, seq))
            
            print("测试课程添加成功！")
        else:
            print("添加课程失败")
            
    except Exception as e:
        print(f"添加测试课程失败: {e}")

if __name__ == '__main__':
    add_test_course() 