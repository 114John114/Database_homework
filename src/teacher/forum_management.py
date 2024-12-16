from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem,
                           QComboBox, QMessageBox, QDialog, QTextEdit)
from PyQt5.QtCore import Qt
from database import Database

class ForumManagementPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 顶部布局
        top_layout = QHBoxLayout()
        
        # 课程选择
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.load_posts)
        top_layout.addWidget(QLabel('选择课程:'))
        top_layout.addWidget(self.course_combo)
        
        layout.addLayout(top_layout)
        
        # 帖子列表
        self.posts_list = QListWidget()
        self.posts_list.itemDoubleClicked.connect(self.show_post_detail)
        layout.addWidget(self.posts_list)
        
        # 管理按钮
        button_layout = QHBoxLayout()
        
        hide_btn = QPushButton('隐藏帖子')
        hide_btn.clicked.connect(lambda: self.change_post_status('hidden'))
        button_layout.addWidget(hide_btn)
        
        show_btn = QPushButton('显示帖子')
        show_btn.clicked.connect(lambda: self.change_post_status('active'))
        button_layout.addWidget(show_btn)
        
        delete_btn = QPushButton('删除帖子')
        delete_btn.clicked.connect(lambda: self.change_post_status('deleted'))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        # 加载课程列表
        self.load_courses()
    
    def load_courses(self):
        try:
            query = """
                SELECT course_id, title
                FROM Courses
                WHERE instructor_id = %s AND status = 'active'
                ORDER BY title
            """
            courses = Database.execute_query(query, (self.user_id,))
            
            self.course_combo.clear()
            self.course_combo.addItem('所有课程', None)
            for course_id, title in courses:
                self.course_combo.addItem(title, course_id)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
    
    def load_posts(self):
        try:
            course_id = self.course_combo.currentData()
            
            if course_id:
                query = """
                    SELECT fp.post_id, fp.title, u.username,
                           fp.created_at, fp.status,
                           COUNT(fr.reply_id) as reply_count
                    FROM Forum_Posts fp
                    JOIN Users u ON fp.user_id = u.user_id
                    LEFT JOIN Forum_Replies fr ON fp.post_id = fr.post_id
                    WHERE fp.course_id = %s
                    GROUP BY fp.post_id, fp.title, u.username,
                             fp.created_at, fp.status
                    ORDER BY fp.created_at DESC
                """
                posts = Database.execute_query(query, (course_id,))
            else:
                query = """
                    SELECT fp.post_id, fp.title, u.username,
                           fp.created_at, fp.status,
                           COUNT(fr.reply_id) as reply_count
                    FROM Forum_Posts fp
                    JOIN Users u ON fp.user_id = u.user_id
                    LEFT JOIN Forum_Replies fr ON fp.post_id = fr.post_id
                    JOIN Courses c ON fp.course_id = c.course_id
                    WHERE c.instructor_id = %s
                    GROUP BY fp.post_id, fp.title, u.username,
                             fp.created_at, fp.status
                    ORDER BY fp.created_at DESC
                """
                posts = Database.execute_query(query, (self.user_id,))
            
            self.posts_list.clear()
            for post in posts:
                post_id, title, username, created_at, status, reply_count = post
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                
                item_text = (f"标题：{title}\n"
                           f"作者：{username}\n"
                           f"状态：{status}\n"
                           f"回复数：{reply_count}\n"
                           f"发布时间：{created_str}")
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, post_id)
                self.posts_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载帖子列表失败：{str(e)}')
    
    def change_post_status(self, status):
        current_item = self.posts_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请先选择一个帖子')
            return
            
        post_id = current_item.data(Qt.UserRole)
        try:
            query = """
                UPDATE Forum_Posts
                SET status = %s
                WHERE post_id = %s
            """
            Database.execute_query(query, (status, post_id))
            
            self.load_posts()
            QMessageBox.information(self, '成功', '帖子状态已更新！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'更新状态失败：{str(e)}')
    
    def show_post_detail(self, item):
        post_id = item.data(Qt.UserRole)
        dialog = PostDetailDialog(post_id)
        dialog.exec_()

class PostDetailDialog(QDialog):
    def __init__(self, post_id):
        super().__init__()
        self.post_id = post_id
        
        self.setWindowTitle('帖子详情')
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 帖子内容
        self.post_content = QTextEdit()
        self.post_content.setReadOnly(True)
        layout.addWidget(self.post_content)
        
        # 回复列表
        self.replies_list = QListWidget()
        layout.addWidget(QLabel('回复列表:'))
        layout.addWidget(self.replies_list)
        
        # 加载内容
        self.load_post_content()
        self.load_replies()
    
    def load_post_content(self):
        try:
            query = """
                SELECT fp.title, fp.content, u.username,
                       fp.created_at, c.title as course_title
                FROM Forum_Posts fp
                JOIN Users u ON fp.user_id = u.user_id
                JOIN Courses c ON fp.course_id = c.course_id
                WHERE fp.post_id = %s
            """
            result = Database.execute_query(query, (self.post_id,))
            
            if result:
                title, content, username, created_at, course_title = result[0]
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                
                post_text = (f"标题：{title}\n"
                           f"作者：{username}\n"
                           f"课程：{course_title}\n"
                           f"发布时间：{created_str}\n\n"
                           f"内容：\n{content}")
                
                self.post_content.setText(post_text)
                self.setWindowTitle(f'帖子详情 - {title}')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载帖子内容失败：{str(e)}')
    
    def load_replies(self):
        try:
            query = """
                SELECT fr.content, u.username, fr.created_at,
                       fr.status
                FROM Forum_Replies fr
                JOIN Users u ON fr.user_id = u.user_id
                WHERE fr.post_id = %s
                ORDER BY fr.created_at
            """
            replies = Database.execute_query(query, (self.post_id,))
            
            self.replies_list.clear()
            for reply in replies:
                content, username, created_at, status = reply
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                
                item_text = (f"{username} 回复于 {created_str}\n"
                           f"状态：{status}\n"
                           f"{content}")
                
                self.replies_list.addItem(QListWidgetItem(item_text))
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载回复列表失败：{str(e)}')