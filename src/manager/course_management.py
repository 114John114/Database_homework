from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QLineEdit, QDialog, QComboBox, QTextEdit)
from PyQt5.QtCore import Qt
from database import Database

class CourseDialog(QDialog):
    def __init__(self, course_id=None, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.setup_ui()
        if course_id:
            self.load_course_data()
        
    def setup_ui(self):
        self.setWindowTitle('课程信息')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # 课程名称
        layout.addWidget(QLabel('课程名称:'))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)
        
        # 教师选择
        layout.addWidget(QLabel('授课教师:'))
        self.teacher_combo = QComboBox()
        self.load_teachers()
        layout.addWidget(self.teacher_combo)
        
        # 难度选择
        layout.addWidget(QLabel('难度等级:'))
        self.difficulty_combo = QComboBox()
        self.difficulty_map = {
            '初级': 'beginner',
            '中级': 'intermediate',
            '高级': 'advanced'
        }
        self.difficulty_reverse_map = {v: k for k, v in self.difficulty_map.items()}
        self.difficulty_combo.addItems(list(self.difficulty_map.keys()))
        layout.addWidget(self.difficulty_combo)
        
        # 课程描述
        layout.addWidget(QLabel('课程描述:'))
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(100)
        layout.addWidget(self.description_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.setProperty('success', True)
        save_btn.clicked.connect(self.save_course)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def load_teachers(self):
        try:
            query = """
                SELECT user_id, username
                FROM Users
                WHERE role = 'teacher'
                ORDER BY username
            """
            teachers = Database.execute_query(query)
            
            self.teacher_combo.clear()
            for teacher_id, username in teachers:
                self.teacher_combo.addItem(username, teacher_id)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载教师列表失败：{str(e)}')
            
    def load_course_data(self):
        try:
            query = """
                SELECT c.title, c.instructor_id, c.difficulty_level,
                       c.description
                FROM Courses c
                WHERE c.course_id = %s
            """
            result = Database.execute_query(query, (self.course_id,))
            
            if result:
                title, instructor_id, difficulty, description = result[0]
                
                self.title_input.setText(title)
                
                # 设置教师
                index = self.teacher_combo.findData(instructor_id)
                if index >= 0:
                    self.teacher_combo.setCurrentIndex(index)
                
                # 设置难度
                difficulty_text = self.difficulty_reverse_map.get(difficulty, '初级')
                index = self.difficulty_combo.findText(difficulty_text)
                if index >= 0:
                    self.difficulty_combo.setCurrentIndex(index)
                
                self.description_input.setText(description or '')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程信息失败：{str(e)}')
            
    def save_course(self):
        try:
            title = self.title_input.text().strip()
            instructor_id = self.teacher_combo.currentData()
            difficulty_text = self.difficulty_combo.currentText()
            difficulty = self.difficulty_map.get(difficulty_text, 'beginner')
            description = self.description_input.toPlainText().strip()
            
            if not title:
                QMessageBox.warning(self, '错误', '请输入课程名称')
                return
                
            if not instructor_id:
                QMessageBox.warning(self, '错误', '请选择授课教师')
                return
            
            if self.course_id:
                # 更新课程
                query = """
                    UPDATE Courses
                    SET title = %s,
                        instructor_id = %s,
                        difficulty_level = %s,
                        description = %s
                    WHERE course_id = %s
                """
                Database.execute_query(query, (
                    title, instructor_id, difficulty,
                    description, self.course_id
                ))
            else:
                # 创建新课程
                query = """
                    INSERT INTO Courses (
                        title, instructor_id, difficulty_level,
                        description, status
                    ) VALUES (%s, %s, %s, %s, 'active')
                """
                Database.execute_query(query, (
                    title, instructor_id, difficulty, description
                ))
            
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存课程失败：{str(e)}')

class CourseManagementPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.difficulty_map = {
            '初级': 'beginner',
            '中级': 'intermediate',
            '高级': 'advanced'
        }
        self.difficulty_reverse_map = {v: k for k, v in self.difficulty_map.items()}
        self.setup_ui()
        self.load_courses()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # 标题和工具栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel('课程管理')
        title_label.setProperty('heading', True)
        header_layout.addWidget(title_label)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索课程...')
        self.search_input.textChanged.connect(self.search_courses)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                min-width: 200px;
            }
        """)
        header_layout.addWidget(self.search_input)
        
        # 添加课程按钮
        add_btn = QPushButton('添加课程')
        add_btn.setProperty('success', True)
        add_btn.clicked.connect(self.add_course)
        header_layout.addWidget(add_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 课程列表
        self.course_table = QTableWidget()
        self.course_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.course_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.course_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # 设置列
        self.course_table.setColumnCount(7)
        self.course_table.setHorizontalHeaderLabels([
            '课程ID', '课程名称', '教师', '难度', '章节数', '学生数', '操作'
        ])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.course_table)
        
    def load_courses(self):
        try:
            query = """
                SELECT c.course_id, c.title, u.username,
                       c.difficulty_level,
                       COUNT(DISTINCT ch.chapter_id) as chapter_count,
                       COUNT(DISTINCT sc.student_id) as student_count
                FROM Courses c
                JOIN Users u ON c.instructor_id = u.user_id
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Student_Course sc ON c.course_id = sc.course_id
                GROUP BY c.course_id, c.title, u.username,
                         c.difficulty_level
                ORDER BY c.course_id
            """
            courses = Database.execute_query(query)
            
            self.course_table.setRowCount(len(courses))
            for i, course in enumerate(courses):
                course_id, title, teacher, difficulty, chapter_count, student_count = course
                
                # 课程ID
                self.course_table.setItem(i, 0, QTableWidgetItem(str(course_id)))
                
                # 课程名称
                self.course_table.setItem(i, 1, QTableWidgetItem(title))
                
                # 教师
                self.course_table.setItem(i, 2, QTableWidgetItem(teacher))
                
                # 难度
                difficulty_text = self.difficulty_reverse_map.get(difficulty, '初级')
                self.course_table.setItem(i, 3, QTableWidgetItem(difficulty_text))
                
                # 章节数
                self.course_table.setItem(i, 4, QTableWidgetItem(str(chapter_count)))
                
                # 学生数
                self.course_table.setItem(i, 5, QTableWidgetItem(str(student_count)))
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = QPushButton('编辑')
                edit_btn.clicked.connect(
                    lambda _, cid=course_id: self.edit_course(cid))
                btn_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('删除')
                delete_btn.setProperty('danger', True)
                delete_btn.clicked.connect(
                    lambda _, cid=course_id: self.delete_course(cid))
                btn_layout.addWidget(delete_btn)
                
                btn_widget.setLayout(btn_layout)
                self.course_table.setCellWidget(i, 6, btn_widget)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
            
    def search_courses(self, text):
        for i in range(self.course_table.rowCount()):
            match = False
            for j in range(self.course_table.columnCount() - 1):  # 不搜索操作列
                item = self.course_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.course_table.setRowHidden(i, not match)
            
    def add_course(self):
        dialog = CourseDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_courses()
        
    def edit_course(self, course_id):
        dialog = CourseDialog(course_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_courses()
        
    def delete_course(self, course_id):
        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这门课程吗？\n删除后将无法恢复！',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除相关数据
                queries = [
                    "DELETE FROM Test_Submissions WHERE course_id = %s",
                    "DELETE FROM Course_Progress WHERE course_id = %s",
                    "DELETE FROM Student_Course WHERE course_id = %s",
                    "DELETE FROM Course_Chapters WHERE course_id = %s",
                    "DELETE FROM Courses WHERE course_id = %s"
                ]
                
                for query in queries:
                    Database.execute_query(query, (course_id,))
                
                self.load_courses()
                QMessageBox.information(self, '成功', '课程已删除！')
                
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除课程失败：{str(e)}') 