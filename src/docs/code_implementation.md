# 在线教学系统代码实现说明文档

## 一、系统架构

### 1. 技术栈
- 前端：PyQt5实现桌面GUI界面
- 后端：Python实现业务逻辑
- 数据库：OpenGauss关系型数据库
- 开发模式：MVC架构设计

### 2. 目录结构
```
src/
├── main.py              # 程序入口
├── database.py          # 数据库连接管理
├── config.py            # 配置文件
├── styles.py            # 界面样式
├── student/            # 学生模块
├── teacher/            # 教师模块
└── manager/            # 管理员模块
```

## 二、核心功能实现

### 1. 数据库连接池（database.py）
```python
class Database:
    _pool = None

    @classmethod
    def initialize(cls):
        if cls._pool is None:
            cls._pool = SimpleConnectionPool(1, 20, **DB_CONFIG)

    @classmethod
    def execute_query(cls, query, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    result = cur.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        finally:
            cls.return_connection(conn)
```
- 使用连接池管理数据库连接
- 实现自动连接获取和释放
- 统一的SQL执行接口

### 2. 用户认证（login_window.py）
```python
def handle_login(self):
    username = self.username_input.text()
    password = self.password_input.text()
    
    # 密码加密
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # 验证用户
    query = """
        SELECT user_id, role 
        FROM Users 
        WHERE username = %s AND password = %s
    """
    result = Database.execute_query(query, (username, hashed_password))
```
- SHA256密码加密
- 角色基础访问控制
- 登录状态管理

### 3. 课程管理（teacher/course_management.py）
```python
def create_course(self):
    title = self.title_input.text()
    description = self.description_input.toPlainText()
    
    query = """
        INSERT INTO Courses (title, description, instructor_id)
        VALUES (%s, %s, %s)
        RETURNING course_id
    """
    result = Database.execute_query(
        query, 
        (title, description, self.user_id)
    )
```
- 课程CRUD操作
- 教师权限验���
- 课程资源管理

### 4. 学习进度跟踪（student/progress.py）
```python
def load_progress(self):
    query = """
        SELECT c.title, ch.title, cp.progress_percentage,
               cp.status, cp.last_accessed
        FROM Course_Progress cp
        JOIN Courses c ON cp.course_id = c.course_id
        JOIN Course_Chapters ch ON cp.chapter_id = ch.chapter_id
        WHERE cp.student_id = %s
    """
    progress_data = Database.execute_query(query, (self.user_id,))
```
- 实时进度更新
- 学习状态记录
- 数据可视化展示

### 5. 测试系统（student/test.py）
```python
def submit_test(self):
    answers = self.collect_answers()
    
    query = """
        INSERT INTO Test_Submissions 
        (student_id, course_id, chapter_id, answer)
        VALUES (%s, %s, %s, %s)
    """
    Database.execute_query(
        query,
        (self.user_id, self.course_id, self.chapter_id, answers)
    )
```
- 自动评分系统
- 答案验证
- 成绩统计分析

### 6. 讨论区管理（forum_management.py）
```python
def create_post(self):
    title = self.title_input.text()
    content = self.content_input.toPlainText()
    
    query = """
        INSERT INTO Forum_Posts 
        (course_id, user_id, title, content)
        VALUES (%s, %s, %s, %s)
    """
    Database.execute_query(
        query,
        (self.course_id, self.user_id, title, content)
    )
```
- 帖子管理
- 回复功能
- 内容审核

## 三、关键技术要点

### 1. 数据安全
- 密码加密存储
- SQL注入防护
- 权限访问控制

### 2. 性能优化
- 数据库连接池
- 查询语句优化
- 缓存机制

### 3. 用户界面
- 现代化界面设计
- 响应式布局
- 用户交互优化

### 4. 错误处理
```python
try:
    result = Database.execute_query(query, params)
except Exception as e:
    QMessageBox.warning(self, '错误', f'操作失败：{str(e)}')
    return
```
- 异常捕获
- 用户友好提示
- 日志记录

## 四、扩展功能

### 1. 数据统计（statistics.py）
```python
def generate_statistics(self):
    query = """
        SELECT 
            COUNT(DISTINCT student_id) as student_count,
            AVG(score) as avg_score,
            COUNT(DISTINCT course_id) as course_count
        FROM Test_Submissions
        WHERE status = 'completed'
    """
    stats = Database.execute_query(query)
```
- 成绩统计
- 学习进度分析
- 使用情况报告

### 2. 系统管理（manager_window.py）
```python
class ManagerWindow(QMainWindow):
    def __init__(self, user_id):
        self.setup_ui()
        self.load_management_tools()
```
- 用户管理
- 课程审核
- 系统监控

## 五、代码规范

### 1. 命名规范
- 类名：驼峰命名（UserManagement）
- 方法名：下划线命名（handle_login）
- 变量名：下划线命名（user_id）

### 2. 注释规范
- 类注释：说明类的功能和用途
- 方法注释：说明参数和返回值
- 关键代码注释：说明实现逻辑

### 3. 代码组织
- 模块化设计
- 功能封装
- 代码复用

## 六、部署说明

### 1. 环境要求
- Python 3.8+
- PyQt5 5.15+
- psycopg2 2.9+
- OpenGauss 3.0+

### 2. 配置说明
```python
DB_CONFIG = {
    'database': 'db_tpcc',
    'user': 'joe',
    'password': '******',
    'host': '1.94.215.59',
    'port': '26000'
}
```
- 数据库连接配置
- 系统参数设置
- 环境变量配置

### 3. 运行方式
```bash
cd src
python main.py
```
- 直接运行
- 打包发布
- 服务部署 