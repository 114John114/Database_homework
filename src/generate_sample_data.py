from database import Database
import hashlib
import random
from datetime import datetime, timedelta

def generate_sample_data():
    try:
        # 生成教师用户
        teachers = [
            ('张教授', '计算机科学'),
            ('李博士', '数据科学'),
            ('王老师', '软件工程'),
            ('刘教授', '人工智能'),
            ('陈博士', '网络安全')
        ]
        
        teacher_ids = []
        for name, field in teachers:
            password = hashlib.sha256('123456'.encode()).hexdigest()
            query = """
                INSERT INTO Users (username, password, role)
                VALUES (%s, %s, 'teacher')
                RETURNING user_id
            """
            result = Database.execute_query(query, (f"{name}_{field}", password))
            teacher_ids.append(result[0][0])
            print(f"创建教师用户: {name}_{field}")
        
        # 生成学生用户
        students = [
            '张三', '李四', '王五', '赵六', '钱七',
            '孙八', '周九', '吴十', '郑十一', '王十二'
        ]
        
        student_ids = []
        for name in students:
            password = hashlib.sha256('123456'.encode()).hexdigest()
            query = """
                INSERT INTO Users (username, password, role)
                VALUES (%s, %s, 'student')
                RETURNING user_id
            """
            result = Database.execute_query(query, (name, password))
            student_ids.append(result[0][0])
            print(f"创建学生用户: {name}")
        
        # 生成课程
        courses = [
            ('Python编程基础', '学习Python编程的基本概念和语法', 'beginner'),
            ('数据结构与算法', '掌握基本的数据结构和算法设计', 'intermediate'),
            ('数据库系统原理', '学习数据库设计和SQL语言', 'intermediate'),
            ('机器学习入门', '了解机器学习的基本概念和应用', 'advanced'),
            ('Web开发基础', '学习HTML、CSS和JavaScript', 'beginner'),
            ('网络安全基础', '了解基本的网络安全概念和防护措施', 'intermediate'),
            ('人工智能导论', '人工智能基础理论和应用', 'advanced'),
            ('操作系统原理', '学习操作系统的基本概念和原理', 'intermediate'),
            ('软件工程实践', '软件开发流程和项目管理', 'intermediate'),
            ('云计算技术', '云计算平台和服务的使用', 'advanced')
        ]
        
        course_ids = []
        for i, (title, desc, level) in enumerate(courses):
            teacher_id = teacher_ids[i % len(teacher_ids)]
            query = """
                INSERT INTO Courses (title, description, instructor_id, difficulty_level, status)
                VALUES (%s, %s, %s, %s, 'active')
                RETURNING course_id
            """
            result = Database.execute_query(query, (title, desc, teacher_id, level))
            course_ids.append(result[0][0])
            print(f"创建课程: {title}")
        
        # 生成课程章节
        chapter_ids = {}  # course_id -> [chapter_ids]
        for course_id in course_ids:
            chapter_ids[course_id] = []
            for i in range(1, 6):  # 每个课程5个章节
                query = """
                    INSERT INTO Course_Chapters (course_id, title, description, sequence_number)
                    VALUES (%s, %s, %s, %s)
                    RETURNING chapter_id
                """
                title = f"第{i}章：示例章节"
                desc = f"这是第{i}章的详细描述"
                result = Database.execute_query(query, (course_id, title, desc, i))
                chapter_ids[course_id].append(result[0][0])
            print(f"为课程ID {course_id} 创建章节")
        
        # 生成学生选课记录
        for student_id in student_ids:
            for course_id in random.sample(course_ids, 3):  # 每个学生随机选3门课
                query = """
                    INSERT INTO Student_Course 
                    (student_id, course_id)
                    VALUES (%s, %s)
                """
                Database.execute_query(query, (student_id, course_id))
                print(f"为学生ID {student_id} 创建选课记录")
                
                # 为该学生的每个章节生成学习进度
                for chapter_id in chapter_ids[course_id]:
                    progress = random.randint(0, 100)
                    status = 'completed' if progress == 100 else 'in_progress'
                    
                    query = """
                        INSERT INTO Course_Progress 
                        (student_id, course_id, chapter_id, progress_percentage, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    Database.execute_query(query, (
                        student_id, course_id, chapter_id, progress, status
                    ))
                print(f"为学生ID {student_id} 创建学习进度")
        
        # 生成测试题目
        for course_id in course_ids:
            for chapter_id in chapter_ids[course_id]:
                create_test_questions(course_id, chapter_id)
        
        # 生成测试提交记录
        for student_id in student_ids:
            # 获取学生已选课程的已完成章节
            progress_query = """
                SELECT DISTINCT cp.course_id, cp.chapter_id 
                FROM Course_Progress cp
                JOIN Student_Course sc ON cp.course_id = sc.course_id 
                    AND cp.student_id = sc.student_id
                WHERE cp.student_id = %s AND cp.status = 'completed'
            """
            completed = Database.execute_query(progress_query, (student_id,))
            
            for course_id, chapter_id in completed:
                score = random.randint(60, 100)
                answers = {'1': 'A', '2': 'B', '3': 'C'}  # 示例答案
                
                query = """
                    INSERT INTO Test_Submissions 
                    (student_id, course_id, chapter_id, score, answer, status)
                    VALUES (%s, %s, %s, %s, %s, 'graded')
                """
                Database.execute_query(query, (
                    student_id, course_id, chapter_id, score, str(answers)
                ))
            print(f"为学生ID {student_id} 创建测试成绩")
        
        # 生成讨论帖子
        topics = [
            '求助：遇到一个问题',
            '分享：学习心得',
            '讨论：关于课程内容',
            '建议：课程改进',
            '交流：学习方法'
        ]
        
        for course_id in course_ids:
            # 获取选修该课��的学生
            student_query = """
                SELECT student_id FROM Student_Course WHERE course_id = %s
            """
            enrolled_students = Database.execute_query(student_query, (course_id,))
            enrolled_student_ids = [s[0] for s in enrolled_students]
            
            if not enrolled_student_ids:
                continue
                
            for i in range(3):  # 每个课程3个帖子
                student_id = random.choice(enrolled_student_ids)
                title = random.choice(topics)
                content = f"这是一个讨论帖子的内容示例{i+1}"
                
                post_query = """
                    INSERT INTO Forum_Posts 
                    (course_id, user_id, title, content)
                    VALUES (%s, %s, %s, %s)
                    RETURNING post_id
                """
                result = Database.execute_query(post_query, (
                    course_id, student_id, title, content
                ))
                
                post_id = result[0][0]
                # 添加回复
                for j in range(2):  # 每个帖子2个回复
                    reply_user = random.choice(enrolled_student_ids + teacher_ids)
                    reply_query = """
                        INSERT INTO Forum_Replies 
                        (post_id, user_id, content)
                        VALUES (%s, %s, %s)
                    """
                    Database.execute_query(reply_query, (
                        post_id, reply_user, f"这是回复内容{j+1}"
                    ))
            print(f"为课程ID {course_id} 创建讨论帖子")
        
        # 生成课程评分
        for student_id in student_ids:
            # 获取学生已选课程
            course_query = """
                SELECT course_id FROM Student_Course WHERE student_id = %s
            """
            enrolled_courses = Database.execute_query(course_query, (student_id,))
            enrolled_course_ids = [c[0] for c in enrolled_courses]
            
            if not enrolled_course_ids:
                continue
                
            for course_id in random.sample(enrolled_course_ids, min(2, len(enrolled_course_ids))):
                rating = random.randint(3, 5)
                comment = f"这是一条评价内容，评分为{rating}星"
                
                query = """
                    INSERT INTO Course_Ratings 
                    (user_id, course_id, rating, comment)
                    VALUES (%s, %s, %s, %s)
                """
                Database.execute_query(query, (student_id, course_id, rating, comment))
            print(f"为学生ID {student_id} 创建课程评分")
        
        # 生成收藏记录
        for student_id in student_ids:
            # 获取学生已选课程
            course_query = """
                SELECT course_id FROM Student_Course WHERE student_id = %s
            """
            enrolled_courses = Database.execute_query(course_query, (student_id,))
            enrolled_course_ids = [c[0] for c in enrolled_courses]
            
            if not enrolled_course_ids:
                continue
                
            for course_id in random.sample(enrolled_course_ids, min(2, len(enrolled_course_ids))):
                query = """
                    INSERT INTO User_Favorites 
                    (user_id, course_id)
                    VALUES (%s, %s)
                """
                Database.execute_query(query, (student_id, course_id))
            print(f"为学生ID {student_id} 创建收藏记录")
        
        print("\n样例数据生成完成！")
        
    except Exception as e:
        print(f"生成样例数据失败: {e}")

def create_test_questions(course_id, chapter_id):
    try:
        # 创建选择题
        query = """
            INSERT INTO Test_Questions (
                course_id, chapter_id, question_text,
                question_type, correct_answer, points
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING question_id
        """
        
        # 选择题示例
        question_data = (
            course_id, chapter_id,
            '以下哪个是Python的基本数据类型？',
            'multiple_choice',
            'A',  # 正确答案是A选项
            10  # 10分
        )
        result = Database.execute_query(query, question_data)
        
        if result:
            question_id = result[0][0]
            
            # 添加选项
            option_query = """
                INSERT INTO Question_Options (
                    question_id, option_text,
                    is_correct, sequence_number
                ) VALUES (%s, %s, %s, %s)
            """
            
            # 选项数据
            options = [
                ('整数 (int)', True, 1),  # A选项，正确答案
                ('循环 (loop)', False, 2),  # B选项
                ('打印 (print)', False, 3),  # C选项
                ('注释 (comment)', False, 4)  # D选项
            ]
            
            for option_text, is_correct, seq in options:
                Database.execute_query(option_query, (
                    question_id, option_text, is_correct, seq
                ))
        
        print(f"为课程ID {course_id} 章节ID {chapter_id} 创建测试题目")
        
    except Exception as e:
        print(f"创建测试题目失败：{str(e)}")

if __name__ == '__main__':
    generate_sample_data() 