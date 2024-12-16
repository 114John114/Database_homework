# 在线教学系统说明文档

## 一、系统概述

本系统是一个基于Python和OpenGauss数据库开发的在线教学平台，支持学生在线学习、教师教学管理和管理员系统管理等功能。

## 二、数据关系设计

### 1. 核心实体关系
1. Users（用户）与 Courses（课程）
   - 教师用户通过instructor_id与课程形成一对多关系（一个教师可以创建多个课程）
   - 学生用户通过Student_Course表与课程形成多对多关系（学生可以选修多门课程，课程可以被多个学生选修）

2. Courses（课程）与 Course_Chapters（章节）
   - 一对多关系：一个课程包含多个章节
   - 通过course_id关联
   - 级联删除：删除课程时相关章节一并删除

3. Users（用户）与学习记录
   - 通过Course_Progress表记录学生的学习进度
   - 通过Test_Submissions表记录学生的测试提交
   - 通过Course_Ratings表记录学生对课程的评分

### 2. 测试系统关系
1. Test_Questions（题目）与 Question_Options（选项）
   - 一对多关系：一个题目包含多个选项
   - 通过question_id关联
   - 级联删除：删除题目时相关选项一并删除

2. 测试题目与课程章节
   - Test_Questions通过course_id和chapter_id与具体课程章节关联
   - 可以针对整个课程或具体章节设置测试题目

### 3. 讨论区关系
1. Forum_Posts（帖子）与 Forum_Replies（回复）
   - 一对多关系：一个帖子可以有多个回复
   - 通过post_id关联
   - 级联删除：删除帖子时相关回复一并删除

2. 帖子与课程
   - Forum_Posts通过course_id与具体课程关联
   - 每个课程都有独立的讨论区

### 4. 关键外键约束
1. Student_Course表
   - student_id -> Users(user_id)
   - course_id -> Courses(course_id)
   - 唯一约束：(student_id, course_id)，确保学生不会重复选修同一课程

2. Course_Progress表
   - student_id -> Users(user_id)
   - course_id -> Courses(course_id)
   - chapter_id -> Course_Chapters(chapter_id)
   - 唯一约束：(student_id, course_id, chapter_id)，确保每个学生在每个章节只有一条进度记录

3. Course_Ratings表
   - user_id -> Users(user_id)
   - course_id -> Courses(course_id)
   - 唯一约束：(user_id, course_id)，确保每个学生只能对同一课程评分一次

### 5. 数据完整性保证
1. 实体完整性
   - 所有表都使用SERIAL类型的主键
   - 主键自动递增，确保唯一性

2. 参照完整性
   - 使用外键约束确保关联数据的有效性
   - 适当使用级联删除（ON DELETE CASCADE）

3. 域完整性
   - 使用CHECK约束限制数据范围（如评分1-5分）
   - 使用DEFAULT值设置默认数据
   - 使用NOT NULL约束确保必要数据存在

## 二、数据库表结构

### 1. Users（用户表）
```sql
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| user_id | 用户ID | SERIAL | - | 主键，自增 |
| username | 用户名 | VARCHAR | 50 | 唯一，非空 |
| password | 密码 | VARCHAR | 255 | 非空，SHA256加密 |
| role | 角色 | VARCHAR | 20 | 非空，student/teacher/admin |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |
| last_login | 最后登录时间 | TIMESTAMP | - | 可空 |

### 2. Courses（课程表）
```sql
CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    instructor_id INTEGER REFERENCES Users(user_id),
    duration INTEGER,
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| course_id | 课程ID | SERIAL | - | 主键，自增 |
| title | 课程名称 | VARCHAR | 100 | 非空 |
| description | 课程描述 | TEXT | - | 可空 |
| instructor_id | 教师ID | INTEGER | - | 外键，关联Users表 |
| duration | 课程时长 | INTEGER | - | 分钟数，可空 |
| difficulty_level | 难度等级 | VARCHAR | 20 | 初级/中级/高级 |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |
| updated_at | 更新时间 | TIMESTAMP | - | 可空 |

### 3. Course_Chapters（课程章节表）
```sql
CREATE TABLE Course_Chapters (
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
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| chapter_id | 章节ID | SERIAL | - | 主键，自增 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| title | 章节标题 | VARCHAR | 100 | 非空 |
| description | 章节描述 | TEXT | - | 可空 |
| sequence_number | 序号 | INTEGER | - | 非空，章节顺序 |
| content_url | 内容链接 | VARCHAR | 255 | 可空，资源链接 |
| content_type | 内容类型 | VARCHAR | 20 | 视频/文档 |
| duration | 时长 | INTEGER | - | 分钟数，可空 |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |

### 4. Student_Course（学生选课表）
```sql
CREATE TABLE Student_Course (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES Users(user_id),
    course_id INTEGER REFERENCES Courses(course_id),
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
    UNIQUE(student_id, course_id)
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| enrollment_id | 选课ID | SERIAL | - | 主键，自增 |
| student_id | 学生ID | INTEGER | - | 外键，关联Users表 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| enrollment_date | 选课时间 | TIMESTAMP | - | 默认当前时间 |
| status | 状态 | VARCHAR | 20 | 进行中/已完成/已退课 |

### 5. Course_Progress（学习进度表）
```sql
CREATE TABLE Course_Progress (
    progress_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES Users(user_id),
    course_id INTEGER REFERENCES Courses(course_id),
    chapter_id INTEGER REFERENCES Course_Chapters(chapter_id),
    status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id, chapter_id)
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| progress_id | 进度ID | SERIAL | - | 主键，自增 |
| student_id | 学生ID | INTEGER | - | 外键，关联Users表 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| chapter_id | 章节ID | INTEGER | - | 外键，关联Course_Chapters表 |
| status | 状态 | VARCHAR | 20 | 未开始/进行中/已完成 |
| progress_percentage | 进度百分比 | INTEGER | - | 0-100 |
| last_accessed | 最后访问时间 | TIMESTAMP | - | 默认当前时间 |

### 6. Test_Questions（测试题目表）
```sql
CREATE TABLE Test_Questions (
    question_id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES Courses(course_id),
    chapter_id INTEGER REFERENCES Course_Chapters(chapter_id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) CHECK (question_type IN ('multiple_choice', 'true_false', 'essay')),
    correct_answer TEXT NOT NULL,
    points INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| question_id | 题目ID | SERIAL | - | 主键，自增 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| chapter_id | 章节ID | INTEGER | - | 外键，关联Course_Chapters表 |
| question_text | 题目内容 | TEXT | - | 非空 |
| question_type | 题目类型 | VARCHAR | 20 | 选择/判断/问答 |
| correct_answer | 正确答案 | TEXT | - | 非空 |
| points | 分值 | INTEGER | - | 默认1分 |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |

### 7. Question_Options（选项表）
```sql
CREATE TABLE Question_Options (
    option_id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES Test_Questions(question_id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    sequence_number INTEGER NOT NULL,
    UNIQUE(question_id, sequence_number)
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| option_id | 选项ID | SERIAL | - | 主键，自增 |
| question_id | 题目ID | INTEGER | - | 外键，关联Test_Questions表 |
| option_text | 选项内容 | TEXT | - | 非空 |
| is_correct | 是否正确 | BOOLEAN | - | 默认false |
| sequence_number | 序号 | INTEGER | - | 非空，选项顺序 |

### 8. Test_Submissions（测试提交表）
```sql
CREATE TABLE Test_Submissions (
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
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| submission_id | 提交ID | SERIAL | - | 主键，自增 |
| student_id | 学生ID | INTEGER | - | 外键，关联Users表 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| chapter_id | 章节ID | INTEGER | - | 外键，关联Course_Chapters表 |
| score | 得分 | REAL | - | 非空 |
| answer | 答案 | TEXT | - | 非空 |
| status | 状态 | TEXT | - | 默认'graded' |
| submitted_at | 提交时间 | TIMESTAMP | - | 默认当前时间 |

### 9. Forum_Posts（讨论帖子表）
```sql
CREATE TABLE Forum_Posts (
    post_id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES Courses(course_id),
    user_id INTEGER REFERENCES Users(user_id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| post_id | 帖子ID | SERIAL | - | 主键，自增 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| user_id | 用户ID | INTEGER | - | 外键，关联Users表 |
| title | 标题 | VARCHAR | 200 | 非空 |
| content | 内容 | TEXT | - | 非空 |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |
| updated_at | 更新时间 | TIMESTAMP | - | 可空 |

### 10. Forum_Replies（回复表）
```sql
CREATE TABLE Forum_Replies (
    reply_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES Forum_Posts(post_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES Users(user_id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| reply_id | 回复ID | SERIAL | - | 主键，自增 |
| post_id | 帖子ID | INTEGER | - | 外键，关联Forum_Posts表 |
| user_id | 用户ID | INTEGER | - | 外键，关联Users表 |
| content | 内容 | TEXT | - | 非空 |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |
| updated_at | 更新时间 | TIMESTAMP | - | 可空 |

### 11. Course_Ratings（课程评分表）
```sql
CREATE TABLE Course_Ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id),
    course_id INTEGER REFERENCES Courses(course_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);
```

| 属性名 | 别名 | 数据类型 | 长度 | 备注 |
|--------|------|----------|------|------|
| rating_id | 评分ID | SERIAL | - | 主键，自增 |
| user_id | 用户ID | INTEGER | - | 外键，关联Users表 |
| course_id | 课程ID | INTEGER | - | 外键，关联Courses表 |
| rating | 评分 | INTEGER | - | 1-5分 |
| comment | 评论 | TEXT | - | 可空 |
| created_at | 创建时间 | TIMESTAMP | - | 默认当前时间 |

## 三、用户角色及功能

### 1. 学生功能
- 浏览和��修课程
- 学习课程内容
- 参加章节测试
- 查看学习进度
- 参与课程讨论
- 课程评分

### 2. 教师功能
- 创建和管理课程
- 上传课程内容
- 创建测试题目
- 查看学生进度
- 管理课程讨论
- 查看教学统计

### 3. 管理员功能
- 用户管理
  * 查看所有用户信息
  * 查看用户详细信息
- 课程管理
  * 查看所有课程
  * 管理课程状态
- 讨论区管理
  * 查看所有讨论
  * 管理帖子和回复
- 系统统计
  * 查看成绩分布
  * 查看学习进度
  * 查看系统使用情况

## 四、系统特点

1. 数据完整性
   - 使用外键约束确保数据关联
   - 使用CHECK约束确保数据有效性
   - 使用UNIQUE约束避免重复数据

2. 安全性
   - 密码加密存储
   - 角色权限控制
   - 数据访问控制

3. 可扩展性
   - 模块化设计
   - 清晰的表结构
   - 完善的关联关系

4. 用户体验
   - 现代化界面
   - 实时搜索功能
   - 直观的数据展示

## 五、使用说明

### 1. 系统登录
- 管理员账号：admin / admin123
- 教师账号：张教授_计算机科学 / 123456
- 学生账号：张三 / 123456

### 2. 基本操作
- 登录后根据角色进入相应界面
- 使用顶部导航栏切换功能
- 使用搜索框快速查找内容
- ���用右上角按钮退出登录

### 3. 注意事项
- 定期更改密码
- 及时保存更改
- 正确退出系统 

## 六、数据库触发器设计

### 1. 用户相关触发器

1. 用户最后登录时间更新
```sql
CREATE OR REPLACE FUNCTION update_last_login()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Users SET last_login = CURRENT_TIMESTAMP 
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_last_login
AFTER INSERT ON login_history
FOR EACH ROW
EXECUTE FUNCTION update_last_login();
```

2. 用户角色变更日志
```sql
CREATE OR REPLACE FUNCTION log_role_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.role <> NEW.role THEN
        INSERT INTO user_role_history(user_id, old_role, new_role, change_time)
        VALUES(NEW.user_id, OLD.role, NEW.role, CURRENT_TIMESTAMP);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_log_role_changes
AFTER UPDATE ON Users
FOR EACH ROW
WHEN (OLD.role IS DISTINCT FROM NEW.role)
EXECUTE FUNCTION log_role_changes();
```

### 2. 课程相关触发器

1. 课程更新时间自动更新
```sql
CREATE OR REPLACE FUNCTION update_course_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_course_timestamp
BEFORE UPDATE ON Courses
FOR EACH ROW
EXECUTE FUNCTION update_course_timestamp();
```

2. 课程章节序号自动分配
```sql
CREATE OR REPLACE FUNCTION auto_chapter_sequence()
RETURNS TRIGGER AS $$
BEGIN
    SELECT COALESCE(MAX(sequence_number), 0) + 1 
    INTO NEW.sequence_number
    FROM Course_Chapters 
    WHERE course_id = NEW.course_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_auto_chapter_sequence
BEFORE INSERT ON Course_Chapters
FOR EACH ROW
WHEN (NEW.sequence_number IS NULL)
EXECUTE FUNCTION auto_chapter_sequence();
```

### 3. 学习进度相关触发器

1. 课程总进度自动更新
```sql
CREATE OR REPLACE FUNCTION update_course_progress()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Student_Course
    SET status = CASE 
        WHEN (SELECT AVG(progress_percentage) 
              FROM Course_Progress 
              WHERE student_id = NEW.student_id 
              AND course_id = NEW.course_id) = 100 
        THEN 'completed'
        ELSE 'active'
    END
    WHERE student_id = NEW.student_id 
    AND course_id = NEW.course_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_course_progress
AFTER UPDATE ON Course_Progress
FOR EACH ROW
EXECUTE FUNCTION update_course_progress();
```

2. 新章节进度记录自动创建
```sql
CREATE OR REPLACE FUNCTION create_chapter_progress()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Course_Progress(student_id, course_id, chapter_id, status)
    SELECT sc.student_id, NEW.course_id, NEW.chapter_id, 'not_started'
    FROM Student_Course sc
    WHERE sc.course_id = NEW.course_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_create_chapter_progress
AFTER INSERT ON Course_Chapters
FOR EACH ROW
EXECUTE FUNCTION create_chapter_progress();
```

### 4. 测试相关触发器

1. 测试分数自动计算
```sql
CREATE OR REPLACE FUNCTION calculate_test_score()
RETURNS TRIGGER AS $$
DECLARE
    total_points INTEGER;
    earned_points INTEGER;
BEGIN
    -- 计算总分
    SELECT SUM(points) INTO total_points
    FROM Test_Questions
    WHERE course_id = NEW.course_id 
    AND chapter_id = NEW.chapter_id;
    
    -- 计算得分
    SELECT SUM(points) INTO earned_points
    FROM Test_Questions tq
    WHERE tq.course_id = NEW.course_id 
    AND tq.chapter_id = NEW.chapter_id
    AND tq.correct_answer = NEW.answer;
    
    NEW.score = (earned_points::FLOAT / total_points::FLOAT) * 100;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_calculate_test_score
BEFORE INSERT ON Test_Submissions
FOR EACH ROW
EXECUTE FUNCTION calculate_test_score();
```

### 5. 讨论区相关触发器

1. 帖子更新时间自动更新
```sql
CREATE OR REPLACE FUNCTION update_post_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_post_timestamp
BEFORE UPDATE ON Forum_Posts
FOR EACH ROW
WHEN (OLD.* IS DISTINCT FROM NEW.*)
EXECUTE FUNCTION update_post_timestamp();
```

2. 回复更新时间自动更新
```sql
CREATE OR REPLACE FUNCTION update_reply_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_reply_timestamp
BEFORE UPDATE ON Forum_Replies
FOR EACH ROW
WHEN (OLD.* IS DISTINCT FROM NEW.*)
EXECUTE FUNCTION update_reply_timestamp();
``` 