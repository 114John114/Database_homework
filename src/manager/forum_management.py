from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QLineEdit, QDialog, QTextBrowser)
from PyQt5.QtCore import Qt
from database import Database

class ReplyDialog(QDialog):
    def __init__(self, post_id, parent=None):
        super().__init__(parent)
        self.post_id = post_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('回复详情')
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 帖子信息
        self.post_info = QTextBrowser()
        layout.addWidget(self.post_info)
        
        # 回复列表
        self.reply_table = QTableWidget()
        self.reply_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.reply_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.reply_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # 设置列
        self.reply_table.setColumnCount(4)
        self.reply_table.setHorizontalHeaderLabels([
            '回复内容', '作者', '时间', '操作'
        ])
        self.reply_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.reply_table)
        
        self.load_post_info()
        self.load_replies()
        
    def load_post_info(self):
        try:
            query = """
                SELECT p.title, p.content, u.username,
                       c.title as course_title, p.created_at
                FROM Forum_Posts p
                JOIN Users u ON p.user_id = u.user_id
                JOIN Courses c ON p.course_id = c.course_id
                WHERE p.post_id = %s
            """
            result = Database.execute_query(query, (self.post_id,))
            
            if result:
                title, content, author, course, created_at = result[0]
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else '-'
                
                post_info = (
                    f"标题：{title}\n"
                    f"作者：{author}\n"
                    f"课程：{course}\n"
                    f"发布时间：{created_str}\n\n"
                    f"内容：\n{content}"
                )
                
                self.post_info.setText(post_info)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载帖子信息失败：{str(e)}')
            
    def load_replies(self):
        try:
            query = """
                SELECT r.reply_id, r.content, u.username, r.created_at
                FROM Forum_Replies r
                JOIN Users u ON r.user_id = u.user_id
                WHERE r.post_id = %s
                ORDER BY r.created_at
            """
            replies = Database.execute_query(query, (self.post_id,))
            
            self.reply_table.setRowCount(len(replies))
            for i, reply in enumerate(replies):
                reply_id, content, author, created_at = reply
                
                # 回复内容
                self.reply_table.setItem(i, 0, QTableWidgetItem(content))
                
                # 作者
                self.reply_table.setItem(i, 1, QTableWidgetItem(author))
                
                # 时间
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else '-'
                self.reply_table.setItem(i, 2, QTableWidgetItem(created_str))
                
                # 删除按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                delete_btn = QPushButton('删除')
                delete_btn.setProperty('danger', True)
                delete_btn.clicked.connect(
                    lambda _, rid=reply_id: self.delete_reply(rid))
                btn_layout.addWidget(delete_btn)
                
                btn_widget.setLayout(btn_layout)
                self.reply_table.setCellWidget(i, 3, btn_widget)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载回复列表失败：{str(e)}')
            
    def delete_reply(self, reply_id):
        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这条回复吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM Forum_Replies WHERE reply_id = %s"
                Database.execute_query(query, (reply_id,))
                
                self.load_replies()
                QMessageBox.information(self, '成功', '回复已删除')
                
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除回复失败：{str(e)}')

class ForumManagementPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # 标题和工具栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel('讨论区管理')
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
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 帖子列表
        self.post_table = QTableWidget()
        self.post_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.post_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.post_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # 设置列
        self.post_table.setColumnCount(7)
        self.post_table.setHorizontalHeaderLabels([
            '帖子ID', '标题', '作者', '课程', '回复数', '发布时间', '操作'
        ])
        self.post_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.post_table)
        
        self.load_posts()
        
    def load_posts(self):
        try:
            query = """
                SELECT p.post_id, p.title, u.username, c.title as course_title,
                       p.created_at,
                       COUNT(r.reply_id) as reply_count
                FROM Forum_Posts p
                JOIN Users u ON p.user_id = u.user_id
                JOIN Courses c ON p.course_id = c.course_id
                LEFT JOIN Forum_Replies r ON p.post_id = r.post_id
                GROUP BY p.post_id, p.title, u.username, c.title, p.created_at
                ORDER BY p.created_at DESC
            """
            posts = Database.execute_query(query)
            
            self.post_table.setRowCount(len(posts))
            for i, post in enumerate(posts):
                post_id, title, author, course, created_at, reply_count = post
                
                # 帖子ID
                self.post_table.setItem(i, 0, QTableWidgetItem(str(post_id)))
                
                # 标题
                self.post_table.setItem(i, 1, QTableWidgetItem(title))
                
                # 作者
                self.post_table.setItem(i, 2, QTableWidgetItem(author))
                
                # 课程
                self.post_table.setItem(i, 3, QTableWidgetItem(course))
                
                # 回复数
                self.post_table.setItem(i, 4, QTableWidgetItem(str(reply_count)))
                
                # 发布时间
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else '-'
                self.post_table.setItem(i, 5, QTableWidgetItem(created_str))
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                view_btn = QPushButton('查看')
                view_btn.clicked.connect(
                    lambda _, pid=post_id: self.view_post(pid))
                btn_layout.addWidget(view_btn)
                
                delete_btn = QPushButton('删除')
                delete_btn.setProperty('danger', True)
                delete_btn.clicked.connect(
                    lambda _, pid=post_id: self.delete_post(pid))
                btn_layout.addWidget(delete_btn)
                
                btn_widget.setLayout(btn_layout)
                self.post_table.setCellWidget(i, 6, btn_widget)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载讨论列表失败：{str(e)}')
            
    def view_post(self, post_id):
        dialog = ReplyDialog(post_id, self)
        dialog.exec_()
            
    def delete_post(self, post_id):
        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这个帖子吗？这将同时删除所有相关回复。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除帖子（级联删除会自动删除相关回复）
                query = "DELETE FROM Forum_Posts WHERE post_id = %s"
                Database.execute_query(query, (post_id,))
                
                self.load_posts()
                QMessageBox.information(self, '成功', '帖子已删除')
                
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除帖子失败：{str(e)}')
    
    def search_posts(self, text):
        for i in range(self.post_table.rowCount()):
            match = False
            for j in range(self.post_table.columnCount() - 1):  # 不搜索操作列
                item = self.post_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.post_table.setRowHidden(i, not match) 