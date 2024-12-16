from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem,
                           QDialog, QFormLayout, QLineEdit, QTextEdit,
                           QSpinBox, QComboBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from database import Database
import os
import shutil

class CourseManagementPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 顶部按钮
        button_layout = QHBoxLayout()
        
        # 创建课程按钮
        create_course_btn = QPushButton('创建新课程')
        create_course_btn.clicked.connect(self.show_course_dialog)
        button_layout.addWidget(create_course_btn)
        
        # 添加章节按钮
        add_chapter_btn = QPushButton('添加章节')
        add_chapter_btn.clicked.connect(self.show_chapter_dialog)
        button_layout.addWidget(add_chapter_btn)
        
        layout.addLayout(button_layout)
        
        # 课程列表
        self.course_list = QListWidget()
        self.course_list.itemDoubleClicked.connect(self.edit_course)
        layout.addWidget(QLabel('我的课程:'))
        layout.addWidget(self.course_list)
        
        # 章节列表
        self.chapter_list = QListWidget()
        self.chapter_list.itemDoubleClicked.connect(self.edit_chapter)
        layout.addWidget(QLabel('章节列表:'))
        layout.addWidget(self.chapter_list)
        
        # 加载课程列表
        self.load_courses()
    
    def load_courses(self):
        try:
            query = """
                SELECT c.course_id, c.title, c.description,
                       c.difficulty_level, c.status,
                       COUNT(DISTINCT ch.chapter_id) as chapter_count,
                       COUNT(DISTINCT sc.student_id) as student_count
                FROM Courses c
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Student_Course sc ON c.course_id = sc.course_id
                LEFT JOIN Course_Progress lp ON c.course_id = lp.course_id
                WHERE c.instructor_id = %s
                GROUP BY c.course_id, c.title, c.description,
                         c.difficulty_level, c.status
                ORDER BY c.created_at DESC
            """
            courses = Database.execute_query(query, (self.user_id,))
            
            self.course_list.clear()
            for course in courses:
                course_id, title, desc, level, status, chapters, students = course
                item_text = (f"课程：{title}\n"
                           f"难度：{level}\n"
                           f"状态：{status}\n"
                           f"章节数：{chapters}\n"
                           f"学生数：{students}")
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, course_id)
                self.course_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, '错���', f'加载课程列表失败：{str(e)}')
    
    def load_chapters(self, course_id):
        try:
            query = """
                SELECT chapter_id, title, sequence_number,
                       content_type, content_url
                FROM Course_Chapters
                WHERE course_id = %s
                ORDER BY sequence_number
            """
            chapters = Database.execute_query(query, (course_id,))
            
            self.chapter_list.clear()
            for chapter in chapters:
                chapter_id, title, seq, content_type, url = chapter
                item_text = (f"第{seq}章：{title}\n"
                           f"类型：{content_type}\n"
                           f"文件：{url}")
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, chapter_id)
                self.chapter_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载章节列表失败：{str(e)}')
    
    def show_course_dialog(self):
        dialog = CourseDialog(self.user_id)
        dialog.course_updated.connect(self.load_courses)
        dialog.exec_()
    
    def show_chapter_dialog(self):
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请先选择一个课程')
            return
        
        course_id = current_item.data(Qt.UserRole)
        dialog = ChapterDialog(course_id)
        dialog.chapter_updated.connect(lambda: self.load_chapters(course_id))
        dialog.exec_()
    
    def edit_course(self, item):
        course_id = item.data(Qt.UserRole)
        dialog = CourseDialog(self.user_id, course_id)
        dialog.course_updated.connect(self.load_courses)
        dialog.exec_()
        
        # 加载该课程的章节
        self.load_chapters(course_id)
    
    def edit_chapter(self, item):
        chapter_id = item.data(Qt.UserRole)
        current_course = self.course_list.currentItem()
        if current_course:
            course_id = current_course.data(Qt.UserRole)
            dialog = ChapterDialog(course_id, chapter_id)
            dialog.chapter_updated.connect(lambda: self.load_chapters(course_id))
            dialog.exec_()

class CourseDialog(QDialog):
    course_updated = pyqtSignal()
    
    def __init__(self, user_id, course_id=None):
        super().__init__()
        self.user_id = user_id
        self.course_id = course_id
        
        self.setWindowTitle('课程信息')
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        # 课程标题
        self.title_input = QLineEdit()
        layout.addRow('课程标题:', self.title_input)
        
        # 课程描述
        self.description_input = QTextEdit()
        layout.addRow('课程描述:', self.description_input)
        
        # 难度等级
        self.level_combo = QComboBox()
        self.level_combo.addItems(['beginner', 'intermediate', 'advanced'])
        layout.addRow('难度等级:', self.level_combo)
        
        # 课程状态
        self.status_combo = QComboBox()
        self.status_combo.addItems(['active', 'inactive', 'draft'])
        layout.addRow('课程状态:', self.status_combo)
        
        # 保存按钮
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_course)
        layout.addRow(save_btn)
        
        if course_id:
            self.load_course_data()
    
    def load_course_data(self):
        try:
            query = """
                SELECT title, description, difficulty_level, status
                FROM Courses
                WHERE course_id = %s
            """
            result = Database.execute_query(query, (self.course_id,))
            
            if result:
                title, desc, level, status = result[0]
                self.title_input.setText(title)
                self.description_input.setText(desc)
                self.level_combo.setCurrentText(level)
                self.status_combo.setCurrentText(status)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程信息失败：{str(e)}')
    
    def save_course(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        level = self.level_combo.currentText()
        status = self.status_combo.currentText()
        
        if not title:
            QMessageBox.warning(self, '错误', '课程标题不能为空')
            return
        
        try:
            if self.course_id:
                query = """
                    UPDATE Courses
                    SET title = %s, description = %s,
                        difficulty_level = %s, status = %s
                    WHERE course_id = %s
                """
                params = (title, description, level, status, self.course_id)
            else:
                query = """
                    INSERT INTO Courses (title, description,
                        instructor_id, difficulty_level, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = (title, description, self.user_id, level, status)
            
            Database.execute_query(query, params)
            self.course_updated.emit()
            self.close()
            QMessageBox.information(self, '成功', '课程保存成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存失败：{str(e)}')

class ChapterDialog(QDialog):
    chapter_updated = pyqtSignal()
    
    def __init__(self, course_id, chapter_id=None):
        super().__init__()
        self.course_id = course_id
        self.chapter_id = chapter_id
        self.content_path = None  # 初始化content_path为None
        
        self.setWindowTitle('章节信息')
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        # 章节标题
        self.title_input = QLineEdit()
        layout.addRow('章节标题:', self.title_input)
        
        # 章节描述
        self.description_input = QTextEdit()
        layout.addRow('章节描述:', self.description_input)
        
        # 序号
        self.sequence_input = QSpinBox()
        self.sequence_input.setRange(1, 100)
        layout.addRow('序号:', self.sequence_input)
        
        # 内容类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(['video', 'document'])
        layout.addRow('内容类型:', self.type_combo)
        
        # 内容文件
        file_layout = QHBoxLayout()
        self.file_label = QLabel('未选择文件')
        select_file_btn = QPushButton('选择文件')
        select_file_btn.clicked.connect(self.select_content_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_file_btn)
        layout.addRow('内容文件:', file_layout)
        
        # 保存按钮
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_chapter)
        layout.addRow(save_btn)
        
        if chapter_id:
            self.load_chapter_data()
    
    def load_chapter_data(self):
        try:
            query = """
                SELECT title, description, sequence_number,
                       content_type, content_url
                FROM Course_Chapters
                WHERE chapter_id = %s
            """
            result = Database.execute_query(query, (self.chapter_id,))
            
            if result:
                title, desc, seq, content_type, url = result[0]
                self.title_input.setText(title)
                self.description_input.setText(desc or '')
                self.sequence_input.setValue(seq)
                self.type_combo.setCurrentText(content_type)
                if url:
                    self.content_path = url
                    self.file_label.setText(os.path.basename(url))
                else:
                    self.file_label.setText('未上传文件')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载章节信息失败：{str(e)}')
    
    def select_content_file(self):
        content_type = self.type_combo.currentText()
        if content_type == 'video':
            file_filter = 'Video files (*.mp4 *.avi *.mkv)'
        else:
            file_filter = 'Documents (*.pdf *.doc *.docx *.txt)'
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择文件', '', file_filter)
        
        if file_path:
            self.content_path = file_path
            self.file_label.setText(os.path.basename(file_path))
    
    def save_chapter(self):
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        sequence = self.sequence_input.value()
        content_type = self.type_combo.currentText()
        
        if not title:
            QMessageBox.warning(self, '错误', '章节标题不能为空')
            return
        
        try:
            # 如果选择了新文件，复制到课程内容目录
            new_content_path = None
            if self.content_path and not self.content_path.startswith('course_contents'):
                filename = os.path.basename(self.content_path)
                new_path = os.path.join('course_contents', filename)
                os.makedirs('course_contents', exist_ok=True)
                shutil.copy2(self.content_path, new_path)
                new_content_path = new_path
            elif self.content_path:
                new_content_path = self.content_path
            
            if self.chapter_id:
                # 更新现有章节
                if new_content_path:
                    query = """
                        UPDATE Course_Chapters
                        SET title = %s, description = %s,
                            sequence_number = %s, content_type = %s,
                            content_url = %s
                        WHERE chapter_id = %s
                    """
                    params = (title, description, sequence, content_type,
                            new_content_path, self.chapter_id)
                else:
                    query = """
                        UPDATE Course_Chapters
                        SET title = %s, description = %s,
                            sequence_number = %s, content_type = %s
                        WHERE chapter_id = %s
                    """
                    params = (title, description, sequence, content_type,
                            self.chapter_id)
            else:
                # 创建新章节
                if not new_content_path:
                    QMessageBox.warning(self, '错误', '请选择内容文件')
                    return
                    
                query = """
                    INSERT INTO Course_Chapters (course_id, title,
                        description, sequence_number, content_type,
                        content_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (self.course_id, title, description,
                         sequence, content_type, new_content_path)
            
            Database.execute_query(query, params)
            self.chapter_updated.emit()
            self.close()
            QMessageBox.information(self, '成功', '章节保存成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存失败：{str(e)}') 