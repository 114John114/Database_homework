from database import Database

def init_db():
    try:
        # 清空现有表
        drop_tables_query = """
            DROP TABLE IF EXISTS 
                User_Favorites, Course_Ratings, Forum_Replies, Forum_Posts,
                Test_Submissions, Question_Options, Test_Questions, Course_Progress,
                Course_Chapters, Student_Course, Courses, Users
            CASCADE;
        """
        Database.execute_query(drop_tables_query)
        print("数据库表已清空！")
        
        # 创建Users表
        create_users_table = """
        CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        """
        
        # 创建Courses表
        create_courses_table = """
        CREATE TABLE IF NOT EXISTS Courses (
            course_id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            instructor_id INTEGER REFERENCES Users(user_id),
            duration INTEGER,
            difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft', 'deleted'))
        );
        """
        
        # 创建Course_Chapters表
        create_chapters_table = """
        CREATE TABLE IF NOT EXISTS Course_Chapters (
            chapter_id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES Courses(course_id) ON DELETE CASCADE,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            sequence_number INTEGER NOT NULL,
            content_url VARCHAR(255),
            content_type VARCHAR(20) CHECK (content_type IN ('video', 'document')),
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 创建Student_Course表
        create_student_course_table = """
        CREATE TABLE IF NOT EXISTS Student_Course (
            enrollment_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES Users(user_id),
            course_id INTEGER REFERENCES Courses(course_id),
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
            UNIQUE(student_id, course_id)
        );
        """
        
        # 创建Course_Progress表
        create_course_progress_table = """
        CREATE TABLE IF NOT EXISTS Course_Progress (
            progress_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES Users(user_id),
            course_id INTEGER REFERENCES Courses(course_id),
            chapter_id INTEGER REFERENCES Course_Chapters(chapter_id),
            status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('not_started', 'in_progress', 'completed')),
            progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_id, chapter_id)
        );
        """
        
        # 创建Forum_Posts表
        create_forum_posts_table = """
        CREATE TABLE IF NOT EXISTS Forum_Posts (
            post_id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES Courses(course_id),
            user_id INTEGER REFERENCES Users(user_id),
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'hidden', 'deleted'))
        );
        """
        
        # 创建Forum_Replies表
        create_forum_replies_table = """
        CREATE TABLE IF NOT EXISTS Forum_Replies (
            reply_id SERIAL PRIMARY KEY,
            post_id INTEGER REFERENCES Forum_Posts(post_id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES Users(user_id),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'hidden', 'deleted'))
        );
        """
        
        # 创建Test_Questions表
        create_test_questions_table = """
        CREATE TABLE IF NOT EXISTS Test_Questions (
            question_id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES Courses(course_id),
            chapter_id INTEGER REFERENCES Course_Chapters(chapter_id),
            question_text TEXT NOT NULL,
            question_type VARCHAR(20) CHECK (question_type IN ('multiple_choice', 'true_false', 'essay')),
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 创建Question_Options表
        create_question_options_table = """
        CREATE TABLE IF NOT EXISTS Question_Options (
            option_id SERIAL PRIMARY KEY,
            question_id INTEGER REFERENCES Test_Questions(question_id) ON DELETE CASCADE,
            option_text TEXT NOT NULL,
            is_correct BOOLEAN DEFAULT FALSE,
            sequence_number INTEGER NOT NULL,
            UNIQUE(question_id, sequence_number)
        );
        """
        
        # 创建Test_Submissions表
        create_test_submissions_table = """
        CREATE TABLE IF NOT EXISTS Test_Submissions (
            submission_id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            chapter_id INTEGER NOT NULL,
            score REAL NOT NULL,
            answer TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'graded',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Users(user_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id),
            FOREIGN KEY (chapter_id) REFERENCES Course_Chapters(chapter_id)
        );
        """
        
        # 创建Course_Ratings表
        create_course_ratings_table = """
        CREATE TABLE IF NOT EXISTS Course_Ratings (
            rating_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES Users(user_id),
            course_id INTEGER REFERENCES Courses(course_id),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, course_id)
        );
        """
        
        # 创建User_Favorites表
        create_user_favorites_table = """
        CREATE TABLE IF NOT EXISTS User_Favorites (
            favorite_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES Users(user_id),
            course_id INTEGER REFERENCES Courses(course_id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, course_id)
        );
        """

        # 执行创建表的SQL语句
        Database.execute_query(create_users_table)
        Database.execute_query(create_courses_table)
        Database.execute_query(create_chapters_table)
        Database.execute_query(create_student_course_table)
        Database.execute_query(create_course_progress_table)
        Database.execute_query(create_forum_posts_table)
        Database.execute_query(create_forum_replies_table)
        Database.execute_query(create_test_questions_table)
        Database.execute_query(create_question_options_table)
        Database.execute_query(create_test_submissions_table)
        Database.execute_query(create_course_ratings_table)
        Database.execute_query(create_user_favorites_table)
        
        print("数据库表创建成功！")
        
    except Exception as e:
        print(f"创建数据库表时出错：{str(e)}")

if __name__ == "__main__":
    init_db() 