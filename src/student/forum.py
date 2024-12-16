from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QLineEdit, QTextEdit, QComboBox)
from PyQt5.QtCore import Qt
from database import Database
from datetime import datetime

class ForumPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        self.load_posts()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # 标题和搜索栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel('讨论区')
        title_label.setProperty('heading', True)
        header_layout.addWidget(title_label)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索讨论...')
        self.search_input.textChanged.connect(self.search_posts)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                min-width: 200px;
            }
        """)
        header_layout.addWidget(self.search_input)
        
        # 发帖按钮
        post_btn = QPushButton('发布讨论')
        post_btn.setProperty('success', True)
        post_btn.clicked.connect(self.show_post_dialog)
        header_layout.addWidget(post_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 讨论列表
        self.post_table = QTableWidget()
        self.post_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.post_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.post_table.setSelectionMode(QTableWidget.SingleSelection)
        self.post_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        
        # 设置列
        self.post_table.setColumnCount(6)
        self.post_table.setHorizontalHeaderLabels([
            '标题', '作者', '课程', '回复数', '发布时间', '操作'
        ])
        self.post_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.post_table)
        
        self.load_posts()
    
    def load_posts(self):
        try:
            query = """
                SELECT p.post_id, p.title, c.title,
                       u.username, p.created_at,
                       COUNT(r.reply_id) as reply_count
                FROM Forum_Posts p
                JOIN Courses c ON p.course_id = c.course_id
                JOIN Users u ON p.user_id = u.user_id
                LEFT JOIN Forum_Replies r ON p.post_id = r.post_id
                GROUP BY p.post_id, p.title, c.title,
                         u.username, p.created_at
                ORDER BY p.created_at DESC
            """
            posts = Database.execute_query(query)
            
            self.post_table.setRowCount(len(posts))
            for i, post in enumerate(posts):
                post_id, title, course, author, created_at, replies = post
                
                # 标题
                self.post_table.setItem(i, 0, QTableWidgetItem(title))
                
                # 课程
                self.post_table.setItem(i, 1, QTableWidgetItem(course))
                
                # 作者
                self.post_table.setItem(i, 2, QTableWidgetItem(author))
                
                # 回复数
                self.post_table.setItem(i, 3, QTableWidgetItem(str(replies)))
                
                # 发布时间
                created_at_str = created_at.strftime('%Y-%m-%d %H:%M')
                self.post_table.setItem(i, 4, QTableWidgetItem(created_at_str))
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                view_btn = QPushButton('查看')
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                view_btn.clicked.connect(
                    lambda _, pid=post_id: self.view_post(pid))
                btn_layout.addWidget(view_btn)
                
                btn_widget.setLayout(btn_layout)
                self.post_table.setCellWidget(i, 5, btn_widget)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载帖子列表失败：{str(e)}')
    
    def show_post_dialog(self):
        dialog = PostDialog(self.user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_posts()
    
    def view_post(self, post_id):
        dialog = PostViewDialog(self.user_id, post_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_posts()
    
    def search_posts(self, text):
        for i in range(self.post_table.rowCount()):
            match = False
            for j in range(self.post_table.columnCount() - 1):  # 不搜索操作列
                item = self.post_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.post_table.setRowHidden(i, not match)

class PostDialog(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('发帖')
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 选择课程
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel('选择课程:'))
        self.course_combo = QComboBox()
        self.load_courses()
        course_layout.addWidget(self.course_combo)
        layout.addLayout(course_layout)
        
        # 帖子标题
        layout.addWidget(QLabel('标题:'))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)
        
        # 帖子内容
        layout.addWidget(QLabel('内容:'))
        self.content_input = QTextEdit()
        layout.addWidget(self.content_input)
        
        # 发布按钮
        post_btn = QPushButton('发布')
        post_btn.clicked.connect(self.post)
        layout.addWidget(post_btn)
    
    def load_courses(self):
        try:
            query = """
                SELECT c.course_id, c.title as course_name
                FROM Student_Course sc
                JOIN Courses c ON sc.course_id = c.course_id
                WHERE sc.student_id = %s
                ORDER BY c.title
            """
            courses = Database.execute_query(query, (self.user_id,))
            
            self.course_combo.clear()
            for course_id, name in courses:
                self.course_combo.addItem(name, course_id)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
    
    def post(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        course_id = self.course_combo.currentData()
        
        if not all([title, content, course_id]):
            QMessageBox.warning(self, '错误', '请填写所有必要信息')
            return
        
        try:
            query = """
                INSERT INTO Forum_Posts (course_id, user_id, title, content)
                VALUES (%s, %s, %s, %s)
            """
            Database.execute_query(query, (course_id, self.user_id, title, content))
            
            self.accept()
            QMessageBox.information(self, '成功', '发布成功！')
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'发布失败：{str(e)}')

class PostViewDialog(QDialog):
    def __init__(self, user_id, post_id):
        super().__init__()
        self.user_id = user_id
        self.post_id = post_id
        self.setup_ui()
        self.load_post()
        self.load_replies()
        
    def setup_ui(self):
        self.setWindowTitle('查看帖子')
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 帖子标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 10px 0;
            }
        """)
        layout.addWidget(self.title_label)
        
        # 帖子信息
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
        """)
        layout.addWidget(self.info_label)
        
        # 帖子内容
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("""
            QLabel {
                padding: 10px 0;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.content_label)
        
        # 回复列表
        layout.addWidget(QLabel('回复:'))
        self.reply_table = QTableWidget()
        self.reply_table.setColumnCount(4)
        self.reply_table.setHorizontalHeaderLabels(
            ['回复内容', '作者', '时间', '操作'])
        self.reply_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.reply_table)
        
        # 添加回复
        layout.addWidget(QLabel('添加回复:'))
        self.reply_input = QTextEdit()
        self.reply_input.setMaximumHeight(100)
        layout.addWidget(self.reply_input)
        
        reply_btn = QPushButton('回复')
        reply_btn.clicked.connect(self.add_reply)
        layout.addWidget(reply_btn)
    
    def load_post(self):
        try:
            query = """
                SELECT p.title, p.content, u.username,
                       c.title, p.created_at
                FROM Forum_Posts p
                JOIN Users u ON p.user_id = u.user_id
                JOIN Courses c ON p.course_id = c.course_id
                WHERE p.post_id = %s
            """
            result = Database.execute_query(query, (self.post_id,))
            
            if result:
                title, content, author, course, created_at = result[0]
                
                self.title_label.setText(title)
                self.info_label.setText(
                    f'作者: {author} | 课程: {course} | '
                    f'发布时间: {created_at.strftime("%Y-%m-%d %H:%M")}')
                self.content_label.setText(content)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载帖子失败：{str(e)}')
    
    def load_replies(self):
        try:
            query = """
                SELECT r.reply_id, r.content, u.username,
                       r.created_at, r.user_id
                FROM Forum_Replies r
                JOIN Users u ON r.user_id = u.user_id
                WHERE r.post_id = %s
                ORDER BY r.created_at
            """
            replies = Database.execute_query(query, (self.post_id,))
            
            self.reply_table.setRowCount(len(replies))
            for i, reply in enumerate(replies):
                reply_id, content, author, created_at, user_id = reply
                
                # 回复内容
                self.reply_table.setItem(i, 0, QTableWidgetItem(content))
                
                # 作者
                self.reply_table.setItem(i, 1, QTableWidgetItem(author))
                
                # 时间
                created_at_str = created_at.strftime('%Y-%m-%d %H:%M')
                self.reply_table.setItem(i, 2, QTableWidgetItem(created_at_str))
                
                # 操作按钮
                if user_id == self.user_id:
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout()
                    btn_layout.setContentsMargins(5, 2, 5, 2)
                    
                    delete_btn = QPushButton('删除')
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border-radius: 3px;
                            padding: 5px 10px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """)
                    delete_btn.clicked.connect(
                        lambda _, rid=reply_id: self.delete_reply(rid))
                    btn_layout.addWidget(delete_btn)
                    
                    btn_widget.setLayout(btn_layout)
                    self.reply_table.setCellWidget(i, 3, btn_widget)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载回复列表失败：{str(e)}')
    
    def add_reply(self):
        content = self.reply_input.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, '错误', '请输入回复内容')
            return
        
        try:
            query = """
                INSERT INTO Forum_Replies (post_id, user_id, content)
                VALUES (%s, %s, %s)
            """
            Database.execute_query(query, (self.post_id, self.user_id, content))
            
            self.reply_input.clear()
            self.load_replies()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'回复失败：{str(e)}')
    
    def delete_reply(self, reply_id):
        reply = QMessageBox.question(self, '确认删除',
                                   '确定要删除这条回复吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM Forum_Replies WHERE reply_id = %s"
                Database.execute_query(query, (reply_id,))
                
                self.load_replies()
                
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除回复失败：{str(e)}')