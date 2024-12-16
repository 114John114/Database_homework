# 数据库应用实践实验三报告：在线教学系统的开发与实现

**学号**：×××  
**姓名**：××× (组长)  
**专业**：×××  
**班级**：×××

## 实验环境

1. 硬件环境
   - CPU：Intel Core i5 及以上
   - 内存：8GB 及以上
   - 硬盘：128GB 及以上
   - 网络：支持互联网连接

2. 软件环境
   - 操作系统：Windows 10/11
   - 数据库：华为OpenGauss 3.0
   - 开发语言：Python 3.8+
   - 开发工具：
     * PyCharm 2023.1
     * DBeaver 数据库管理工具
     * Git 版本控制
   - 其他工具：
     * PyQt5 5.15 (GUI开发)
     * psycopg2 2.9 (数据库连接)

## 一、系统选题需求及任务分工

### 1.1 系统需求

1. 背景需求
   - 在线教育快速发展
   - 教学管理数字化需求
   - 师生互动需求增加
   - 学习过程数据化需求

2. 功能需求
   - 用户管理与认证
   - 课程内容管理
   - 学习进度跟踪
   - 在线测试系统
   - 互动讨论功能
   - 数据统计分析

### 1.2 任务分工

| 角色 | 负责模块 | 工作内容 | 工作量占比 |
|------|----------|----------|------------|
| 组长 | 核心功能模块 | - 系统架构设计<br>- 数据库设计<br>- 用户认证模块<br>- 课程管理模块<br>- 系统集成与测试 | 40% |
| 组员A | 教学相关模块 | - 学习进度跟踪<br>- 在线测试系统<br>- 成绩管理模块<br>- 教师统计功能<br>- 相关文档编写 | 30% |
| 组员B | 用户交互模块 | - 用户界面设计<br>- 讨论区功能<br>- 个人中心模块<br>- 系统管理功能<br>- 用户使用文档 | 30% |

## 二、系统概念数据模型（E-R图）设计

[此处插入E-R图]

主要实体关系说明：
1. 用户-课程关系
   - 教师与课程：一对多
   - 学生与课程：多对多（通过选课表）

2. 课程-章节关系
   - 一对多关系
   - 包含序号、内容等属性

3. 用户-测试关系
   - 教师出题：一对多
   - 学生答题：多对多

4. 讨论区关系
   - 用户与帖子：一对多
   - 帖子与回复：一对多

## 三、系统数据表说明

### 3.1 用户相关表
1. Users（用户表）
   - 主键：user_id
   - 用户名、密码、角色等基本信息
   - 包含创建时间、最后登录时间

### 3.2 触发器设计

1. 用户相关触发器
   ```sql
   -- 更新用户最后登录时间
   CREATE OR REPLACE FUNCTION update_last_login()
   RETURNS TRIGGER AS $$
   BEGIN
       UPDATE Users 
       SET last_login = CURRENT_TIMESTAMP 
       WHERE user_id = NEW.user_id;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER tr_update_last_login
   AFTER INSERT ON Login_History
   FOR EACH ROW
   EXECUTE FUNCTION update_last_login();
   ```

2. 课程进度触发器
   ```sql
   -- 自动更新课程总进度
   CREATE OR REPLACE FUNCTION update_course_progress()
   RETURNS TRIGGER AS $$
   BEGIN
       UPDATE Course_Progress cp
       SET progress_percentage = (
           SELECT AVG(progress_percentage)
           FROM Chapter_Progress
           WHERE student_id = NEW.student_id
           AND course_id = NEW.course_id
       )
       WHERE student_id = NEW.student_id
       AND course_id = NEW.course_id;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER tr_update_course_progress
   AFTER UPDATE ON Chapter_Progress
   FOR EACH ROW
   EXECUTE FUNCTION update_course_progress();
   ```

3. 测试成绩触发器
   ```sql
   -- 自动计算测试得分
   CREATE OR REPLACE FUNCTION calculate_test_score()
   RETURNS TRIGGER AS $$
   BEGIN
       UPDATE Test_Submissions
       SET score = (
           SELECT COUNT(*) * 100.0 / (
               SELECT COUNT(*) 
               FROM Test_Questions 
               WHERE test_id = NEW.test_id
           )
           FROM Test_Answers ta
           JOIN Test_Questions tq ON ta.question_id = tq.question_id
           WHERE ta.submission_id = NEW.submission_id
           AND ta.answer = tq.correct_answer
       )
       WHERE submission_id = NEW.submission_id;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER tr_calculate_test_score
   AFTER INSERT ON Test_Answers
   FOR EACH ROW
   EXECUTE FUNCTION calculate_test_score();
   ```

4. 讨论区触发器
   ```sql
   -- 更新帖子回复数和最后回复时间
   CREATE OR REPLACE FUNCTION update_post_stats()
   RETURNS TRIGGER AS $$
   BEGIN
       UPDATE Forum_Posts
       SET reply_count = reply_count + 1,
           last_reply_time = CURRENT_TIMESTAMP
       WHERE post_id = NEW.post_id;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER tr_update_post_stats
   AFTER INSERT ON Post_Replies
   FOR EACH ROW
   EXECUTE FUNCTION update_post_stats();
   ```

[其他表格说明...]

## 四、系统运行环境配置

### 4.1 开发环境配置

1. Python环境配置
   ```bash
   # 安装Python 3.8+
   python -m pip install --upgrade pip
   
   # 安装依赖包
   pip install PyQt5==5.15.9
   pip install psycopg2-binary==2.9.6
   pip install pandas==1.5.3
   pip install matplotlib==3.7.1
   pip install seaborn==0.12.2
   ```

2. OpenGauss数据库配置
   ```sql
   -- 创建数据库
   CREATE DATABASE online_education;
   
   -- 创建表空间
   CREATE TABLESPACE tbs_online_edu 
   RELATIVE LOCATION 'tablespace/tbs_online_edu';
   
   -- 创建模式
   CREATE SCHEMA edu_schema;
   ```

3. 数据库连接配置
   ```python
   # config.py
   DB_CONFIG = {
       'database': 'db_tpcc',
       'user': 'joe',
       'password': '******',
       'host': '1.94.215.59',
       'port': '26000',
       'options': '-c search_path=edu_schema'
   }
   ```

### 4.2 运行环境要求

1. 硬件要求
   - CPU：Intel Core i5 及以上
   - 内存：8GB 及以上
   - 硬盘：128GB 及以上
   - 显示器：分辨率 1920×1080 及以上
   - 网络：支持互联网连接

2. 软件要求
   - 操作系统：Windows 10/11
   - Python：3.8 及以上版本
   - OpenGauss：3.0.0 及以上版本
   - PyQt5：5.15.9
   - psycopg2：2.9.6

### 4.3 关键代码实现

1. 数据库连接池实现
   ```python
   # database.py
   from psycopg2.pool import SimpleConnectionPool
   from config import DB_CONFIG
   
   class Database:
       _pool = None
       
       @classmethod
       def initialize(cls):
           if cls._pool is None:
               try:
                   cls._pool = SimpleConnectionPool(
                       minconn=1,
                       maxconn=20,
                       **DB_CONFIG
                   )
               except Exception as e:
                   print(f"数据库连接失败: {e}")
                   raise
   
       @classmethod
       def get_connection(cls):
           if cls._pool is None:
               cls.initialize()
           return cls._pool.getconn()
   
       @classmethod
       def return_connection(cls, conn):
           if cls._pool is not None:
               cls._pool.putconn(conn)
   ```

2. 异常处理机制
   ```python
   # database.py
   class DatabaseError(Exception):
       """数据库操作异常基类"""
       pass
   
   class ConnectionError(DatabaseError):
       """数据库连接异常"""
       pass
   
   class QueryError(DatabaseError):
       """数据库查询异常"""
       pass
   
   def execute_query(cls, query, params=None):
       conn = None
       try:
           conn = cls.get_connection()
           with conn.cursor() as cur:
               cur.execute(query, params)
               if query.strip().upper().startswith(('SELECT', 'RETURNING')):
                   result = cur.fetchall()
               else:
                   result = None
               conn.commit()
               return result
       except Exception as e:
           if conn:
               conn.rollback()
           raise QueryError(f"查询执行失败: {str(e)}")
       finally:
           if conn:
               cls.return_connection(conn)
   ```

3. 日志记录实现
   ```python
   # logger.py
   import logging
   from datetime import datetime
   
   def setup_logger():
       logger = logging.getLogger('online_education')
       logger.setLevel(logging.INFO)
       
       # 文件处理器
       fh = logging.FileHandler(
           f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
           encoding='utf-8'
       )
       fh.setLevel(logging.INFO)
       
       # 控制台处理器
       ch = logging.StreamHandler()
       ch.setLevel(logging.INFO)
       
       # 格式化器
       formatter = logging.Formatter(
           '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
       )
       fh.setFormatter(formatter)
       ch.setFormatter(formatter)
       
       logger.addHandler(fh)
       logger.addHandler(ch)
       
       return logger
   ```

### 4.4 部署说明

1. 安装步骤
   ```bash
   # 1. 克隆代码仓库
   git clone https://github.com/your-repo/online-education.git
   cd online-education
   
   # 2. 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # 3. 安装依赖
   pip install -r requirements.txt
   
   # 4. 初始化数据库
   python src/init_db.py
   python src/add_admin.py
   python src/generate_sample_data.py
   
   # 5. 启动应用
   python src/main.py
   ```

2. 目录结构
   ```
   online-education/
   ├── src/
   │   ├── main.py
   │   ├── config.py
   │   ├── database.py
   │   ├── logger.py
   │   ├── student/
   │   ├── teacher/
   │   └── manager/
   ├── docs/
   │   └── *.md
   ├── tests/
   │   └── *.py
   ├── logs/
   │   └── *.log
   ├── requirements.txt
   └── README.md
   ```

## 五、系统主要功能界面

### 5.1 登录与注册界面

1. 登录界面
   - 采用简洁现代的设计风格
   - 支持用户名和密码登录
   - 提供角色选择（学生/教师/管理员）
   - 包含注册入口和密码找回功能
   - 登录验证提示清晰明确
   [图5-1 系统登录界面]

2. 注册界面
   - 分步骤引导用户填写信息
   - 实时验证用户输入合法性
   - 提供用户协议和隐私政策
   - 支持上传头像和个人信息
   [图5-2 用户注册界面]

### 5.2 学生功能界面

1. 学生主界面
   - 显示个人信息和学习概况
   - 课程列表和学习进度展示
   - 最近学习记录和待办事项
   - 快速导航到各功能模块
   [图5-3 学生主界面]

2. 课程学习界面
   - 章节内容清晰展示
   - 进度条显示学习状态
   - 支持视频播放和文档阅读
   - 提供笔记和标记功能
   [图5-4 课程学习界面]

3. 测试考试界面
   - 倒计时显示考试时间
   - 题目导航和答题卡
   - 自动保存答题进度
   - 提交后即时查看成绩
   [图5-5 在线测试界面]

### 5.3 教师功能界面

1. 教师主界面
   - 课程管理概览
   - 学生学习数据统计
   - 待批改作业提醒
   - 教学日程安排
   [图5-6 教师主界面]

2. 课程管理界面
   - 课程内容编辑器
   - 章节结构管理
   - 资源文件上传
   - 发布课程和更新管理
   [图5-7 课程管理界面]

3. 学生管理界面
   - 学生名单和基本信息
   - 学习进度跟踪
   - 成绩统计分析
   - 学习报告生成
   [图5-8 学生管理界面]

### 5.4 管理员功能界面

1. 管理员主界面
   - 系统运行状态监控
   - 用户活动统计
   - 系统公告管理
   - 数据备份提示
   [图5-9 管理员主界面]

2. 用户管理界面
   - 用户信息列表
   - 角色权限管理
   - 账号状态控制
   - 批量操作功能
   [图5-10 用户管理界面]

3. 系统管理界面
   - 系统参数配置
   - 日志查看和导出
   - 数据库维护
   - 系统备份还原
   [图5-11 系统管理界面]

### 5.5 公共功能界面

1. 讨论区界面
   - 话题分类导航
   - 发帖和回复功能
   - 搜索和筛选工具
   - 用户互动功能
   [图5-12 讨论区界面]

2. 消息中心界面
   - 系统通知
   - 私信功能
   - 消息提醒设置
   - 消息归档管理
   [图5-13 消息中心界面]

3. 个人中心界面
   - 个人信息管理
   - 学习数据统计
   - 收藏和历史记录
   - 账号安全设置
   [图5-14 个人中心界面]

[此处插入对应的界面截图]

## 六、实验结果总结

### 6.1 系统优点
1. 功能完整性
   - 覆盖教学全过程
   - 角色权限分明
   - 操作流程清晰

2. 技术先进性
   - 采用现代化架构
   - 性能优化合理
   - 安全机制完善

### 6.2 系统不足
1. 功能局限性
   - 缺乏移动端支持
   - 实时通讯功能有限
   - 数据分析深度不够

2. 改进方向
   - 开发移动端应用
   - 增强实时互动功能
   - 深化数据分析能力
   - 优化用户体验

## 七、编程工作总结

在本次项目开发中，作为组长，我主要负责系统的整体架构设计和核心功能模块的实现。在开发过程中，遇到以下主要挑战：

1. 技术难点突破
   - 数据库连接池的实现和优化
   - 事务处理机制的设计
   - 并发访问的处理
   - 性能瓶颈的解决

2. 知识储备提升
   - 深入学习了OpenGauss数据库
   - 掌握了PyQt5界面开发
   - 提升了Python编程技能
   - 增强了项目管理能力

3. 创新设计
   - 设计了灵活的权限管理机制
   - 实现了高效的数据缓存系统
   - 开发了直观的数据可视化功能
   - 创新了用户交互方式

4. 开发体会
   - 团队协作的重要性
   - 技术选型的关键性
   - 代码质量的必要性
   - 文档管理的规范性

通过这次项目开发，不仅提升了技术能力，也学会了如何更好地进行团队协作和项目管理。在解决各种技术难题的过程中，养成了良好的编程习惯和问题解决思维。这些经验对未来的学习和工作都有很大帮助。 