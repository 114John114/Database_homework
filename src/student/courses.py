from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem,
                           QLineEdit, QMainWindow, QMessageBox, QTextEdit,
                           QComboBox, QDialog)
from PyQt5.QtCore import Qt, QTimer
from database import Database
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import os

class CoursesPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索课程...')
        search_button = QPushButton('搜索')
        search_button.clicked.connect(self.search_courses)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # 课程列表
        self.course_list = QListWidget()
        self.course_list.itemDoubleClicked.connect(self.show_course_detail)
        layout.addWidget(self.course_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 收藏按钮
        favorite_button = QPushButton('收藏课程')
        favorite_button.clicked.connect(self.favorite_course)
        button_layout.addWidget(favorite_button)
        
        # 评分按钮
        rate_button = QPushButton('评价课程')
        rate_button.clicked.connect(self.rate_course)
        button_layout.addWidget(rate_button)
        
        layout.addLayout(button_layout)
        
        self.load_courses()
    
    def load_courses(self):
        try:
            query = """
                SELECT c.course_id, c.title, u.username, c.description,
                       c.difficulty_level, COUNT(DISTINCT ch.chapter_id) as chapter_count,
                       ROUND(AVG(cr.rating), 2) as avg_rating
                FROM Courses c
                LEFT JOIN Users u ON c.instructor_id = u.user_id
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Course_Ratings cr ON c.course_id = cr.course_id
                WHERE c.status = 'active'
                GROUP BY c.course_id, c.title, u.username, c.description, c.difficulty_level
                ORDER BY c.created_at DESC
            """
            courses = Database.execute_query(query)
            
            self.course_list.clear()
            for course in courses:
                course_id, title, instructor, desc, level, chapters, rating = course
                rating_text = f"评分：{rating}" if rating else "暂无评分"
                item_text = f"{title}\n教师：{instructor}\n难度：{level}\n章节数：{chapters}\n{rating_text}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, course_id)
                self.course_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程失败：{str(e)}')
    
    def search_courses(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_courses()
            return
            
        try:
            query = """
                SELECT c.course_id, c.title, u.username, c.description,
                       c.difficulty_level, COUNT(DISTINCT ch.chapter_id) as chapter_count,
                       ROUND(AVG(cr.rating), 2) as avg_rating
                FROM Courses c
                LEFT JOIN Users u ON c.instructor_id = u.user_id
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Course_Ratings cr ON c.course_id = cr.course_id
                WHERE c.status = 'active'
                AND (c.title ILIKE %s OR c.description ILIKE %s OR u.username ILIKE %s)
                GROUP BY c.course_id, c.title, u.username, c.description, c.difficulty_level
                ORDER BY c.created_at DESC
            """
            search_pattern = f"%{search_text}%"
            courses = Database.execute_query(query, (search_pattern, search_pattern, search_pattern))
            
            self.course_list.clear()
            for course in courses:
                course_id, title, instructor, desc, level, chapters, rating = course
                rating_text = f"评分：{rating}" if rating else "暂无评分"
                item_text = f"{title}\n教师：{instructor}\n难度：{level}\n章节数：{chapters}\n{rating_text}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, course_id)
                self.course_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, '错误', f'搜索课程失败：{str(e)}')
    
    def show_course_detail(self, item):
        try:
            course_id = item.data(Qt.UserRole)
            
            # 获取课程详细信息
            course_query = """
                SELECT c.title, c.description, u.username, c.difficulty_level,
                       COUNT(DISTINCT ch.chapter_id) as chapter_count,
                       ROUND(AVG(cr.rating), 2) as avg_rating
                FROM Courses c
                LEFT JOIN Users u ON c.instructor_id = u.user_id
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Course_Ratings cr ON c.course_id = cr.course_id
                WHERE c.course_id = %s
                GROUP BY c.course_id, c.title, c.description, u.username, c.difficulty_level
            """
            course_result = Database.execute_query(course_query, (course_id,))
            
            if course_result:
                title, desc, instructor, level, chapters, rating = course_result[0]
                
                # 获取章节列表
                chapters_query = """
                    SELECT ch.chapter_id, ch.title, ch.description,
                           COALESCE(lp.progress_percentage, 0) as progress,
                           COALESCE(lp.status, 'not_started') as status
                    FROM Course_Chapters ch
                    LEFT JOIN Learning_Progress lp ON ch.chapter_id = lp.chapter_id 
                        AND lp.user_id = %s
                    WHERE ch.course_id = %s
                    ORDER BY ch.sequence_number
                """
                chapters_result = Database.execute_query(chapters_query, (self.user_id, course_id))
                
                # 创建并显示课程详情窗口
                self.detail_window = CourseDetailWindow(self.user_id, course_id)
                self.detail_window.setWindowTitle(title)
                
                # 显示课程基本信息
                info_text = (f"课程：{title}\n"
                           f"教师：{instructor}\n"
                           f"难度：{level}\n"
                           f"评分：{rating if rating else '暂无评分'}\n"
                           f"章节数：{chapters}\n\n"
                           f"课程简介：\n{desc}\n\n"
                           f"章节列表：")
                           
                self.detail_window.info_label.setText(info_text)
                
                # 显示章节列表
                self.detail_window.chapter_list.clear()
                for chapter in chapters_result:
                    chapter_id, ch_title, ch_desc, progress, status = chapter
                    chapter_text = (f"{ch_title}\n"
                                  f"进度：{progress}%\n"
                                  f"状态：{status}")
                    chapter_item = QListWidgetItem(chapter_text)
                    chapter_item.setData(Qt.UserRole, chapter_id)
                    self.detail_window.chapter_list.addItem(chapter_item)
                
                self.detail_window.show()
            else:
                QMessageBox.warning(self, '错误', '未找到课程信息')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'显示课程详情失败：{str(e)}')
    
    def favorite_course(self):
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请先选择一个课程')
            return
            
        course_id = current_item.data(Qt.UserRole)
        try:
            # 检查是否已收藏
            check_query = """
                SELECT favorite_id FROM User_Favorites
                WHERE user_id = %s AND course_id = %s
            """
            result = Database.execute_query(check_query, (self.user_id, course_id))
            
            if result:
                QMessageBox.information(self, '提示', '该课程已在收藏列表中')
                return
            
            # 添加收藏
            insert_query = """
                INSERT INTO User_Favorites (user_id, course_id)
                VALUES (%s, %s)
            """
            Database.execute_query(insert_query, (self.user_id, course_id))
            QMessageBox.information(self, '成功', '课程已添加到收藏！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'收藏失败：{str(e)}')
    
    def rate_course(self):
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请先选择一个课程')
            return
            
        course_id = current_item.data(Qt.UserRole)
        dialog = CourseRatingDialog(self.user_id, course_id)
        dialog.exec_()
        self.load_courses()  # 刷新课程列表以显示新的评分

class CourseDetailWindow(QMainWindow):
    def __init__(self, user_id, course_id):
        super().__init__()
        self.user_id = user_id
        self.course_id = course_id
        
        self.setWindowTitle('课程详情')
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 课程信息标签
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # 章节列表
        self.chapter_list = QListWidget()
        self.chapter_list.itemDoubleClicked.connect(self.start_chapter)
        layout.addWidget(self.chapter_list)
        
        # 创建视频播放器
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        
        # 创建文档查看器
        self.doc_viewer = QTextEdit()
        self.doc_viewer.setReadOnly(True)
        
        # 添加到布局
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.video_widget)
        content_layout.addWidget(self.doc_viewer)
        
        # 播放控制按钮
        control_layout = QHBoxLayout()
        play_button = QPushButton('播放/暂停')
        play_button.clicked.connect(self.toggle_play)
        control_layout.addWidget(play_button)
        
        content_layout.addLayout(control_layout)
        
        # 更新学习进度的按钮
        complete_button = QPushButton('完成学习')
        complete_button.clicked.connect(self.complete_chapter)
        content_layout.addWidget(complete_button)
        
        layout.addLayout(content_layout)
        
        self.media_player.setVideoOutput(self.video_widget)
        
        # 添加计时器
        self.study_timer = QTimer()
        self.study_timer.setInterval(60000)  # 每分钟更新一次
        self.study_timer.timeout.connect(self.update_study_time)
        self.study_time_count = 0
        
        # 初始隐藏播放器和文档查看器
        self.video_widget.hide()
        self.doc_viewer.hide()
    
    def start_chapter(self, item):
        chapter_id = item.data(Qt.UserRole)
        try:
            # 检查是否已有学习记录
            check_query = """
                SELECT progress_id FROM Learning_Progress
                WHERE user_id = %s AND chapter_id = %s
            """
            result = Database.execute_query(check_query, (self.user_id, chapter_id))
            
            if not result:
                # 创建新的学习记录
                insert_query = """
                    INSERT INTO Learning_Progress (user_id, course_id, chapter_id, status)
                    VALUES (%s, %s, %s, 'in_progress')
                """
                Database.execute_query(insert_query, (self.user_id, self.course_id, chapter_id))
            
            # 加载章节内容
            self.load_chapter_content(chapter_id)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'开始学习失败：{str(e)}')
    
    def load_chapter_content(self, chapter_id):
        query = """
            SELECT content_url, content_type
            FROM Course_Chapters
            WHERE chapter_id = %s
        """
        result = Database.execute_query(query, (chapter_id,))
        if result:
            content_url = result[0][0]
            content_type = result[0][1]
            
            if content_type == 'video':
                media = QMediaContent(QUrl.fromLocalFile(content_url))
                self.media_player.setMedia(media)
                self.video_widget.show()
                self.doc_viewer.hide()
            elif content_type == 'document':
                with open(content_url, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.doc_viewer.setText(content)
                self.video_widget.hide()
                self.doc_viewer.show()
        self.current_chapter_id = chapter_id
        self.study_timer.start()
    
    def toggle_play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def complete_chapter(self):
        try:
            query = """
                UPDATE Learning_Progress
                SET status = 'completed', progress_percentage = 100,
                    completion_date = CURRENT_TIMESTAMP
                WHERE user_id = %s AND chapter_id = %s
            """
            Database.execute_query(query, (self.user_id, self.current_chapter_id))
            QMessageBox.information(self, '成功', '完成本章节学习！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'更新进度失败：{str(e)}')
    
    def update_study_time(self):
        self.study_time_count += 1
        try:
            query = """
                UPDATE Learning_Progress
                SET study_time = study_time + 1,
                    last_study_time = CURRENT_TIMESTAMP
                WHERE user_id = %s AND chapter_id = %s
            """
            Database.execute_query(query, (
                self.user_id, self.current_chapter_id
            ))
        except Exception as e:
            print(f"Error updating study time: {e}")
    
    def closeEvent(self, event):
        self.study_timer.stop()
        super().closeEvent(event)

class CourseRatingDialog(QDialog):
    def __init__(self, user_id, course_id):
        super().__init__()
        self.user_id = user_id
        self.course_id = course_id
        
        self.setWindowTitle('课程评价')
        self.setFixedWidth(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 评分选择
        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel('评分:'))
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(['1', '2', '3', '4', '5'])
        rating_layout.addWidget(self.rating_combo)
        layout.addLayout(rating_layout)
        
        # 评价内容
        layout.addWidget(QLabel('评价内容:'))
        self.comment_edit = QTextEdit()
        layout.addWidget(self.comment_edit)
        
        # 提交按钮
        submit_btn = QPushButton('提交评价')
        submit_btn.clicked.connect(self.submit_rating)
        layout.addWidget(submit_btn)
        
        self.load_existing_rating()
    
    def load_existing_rating(self):
        query = """
            SELECT rating, comment
            FROM Course_Ratings
            WHERE user_id = %s AND course_id = %s
        """
        result = Database.execute_query(query, (self.user_id, self.course_id))
        if result:
            self.rating_combo.setCurrentText(str(result[0][0]))
            self.comment_edit.setText(result[0][1])
    
    def submit_rating(self):
        rating = int(self.rating_combo.currentText())
        comment = self.comment_edit.toPlainText()
        
        try:
            query = """
                INSERT INTO Course_Ratings (user_id, course_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, course_id)
                DO UPDATE SET rating = %s, comment = %s
            """
            Database.execute_query(query, (
                self.user_id, self.course_id, rating, comment,
                rating, comment
            ))
            QMessageBox.information(self, '成功', '评价提交成功！')
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'提交失败：{str(e)}')

class FavoritesPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 收藏列表
        self.favorites_list = QListWidget()
        layout.addWidget(self.favorites_list)
        
        # 取消收藏按钮
        unfavorite_btn = QPushButton('取消收藏')
        unfavorite_btn.clicked.connect(self.remove_favorite)
        layout.addWidget(unfavorite_btn)
        
        self.load_favorites()
    
    def load_favorites(self):
        query = """
            SELECT c.course_id, c.title, u.username
            FROM User_Favorites f
            JOIN Courses c ON f.course_id = c.course_id
            JOIN Users u ON c.instructor_id = u.user_id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """
        favorites = Database.execute_query(query, (self.user_id,))
        
        self.favorites_list.clear()
        for fav in favorites:
            item = QListWidgetItem(f"{fav[1]} - 教师：{fav[2]}")
            item.setData(Qt.UserRole, fav[0])
            self.favorites_list.addItem(item)
    
    def remove_favorite(self):
        current_item = self.favorites_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请先选择一个课程')
            return
        
        course_id = current_item.data(Qt.UserRole)
        try:
            query = """
                DELETE FROM User_Favorites
                WHERE user_id = %s AND course_id = %s
            """
            Database.execute_query(query, (self.user_id, course_id))
            self.load_favorites()
            QMessageBox.information(self, '成功', '已取消收藏')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'操作失败：{str(e)}')