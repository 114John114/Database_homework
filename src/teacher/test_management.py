from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem,
                           QDialog, QFormLayout, QTextEdit, QSpinBox,
                           QComboBox, QMessageBox, QInputDialog, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from database import Database

class TestManagementPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 顶部布局
        top_layout = QHBoxLayout()
        
        # 课程选择
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.on_course_selected)
        top_layout.addWidget(QLabel('选择课程:'))
        top_layout.addWidget(self.course_combo)
        
        # 章节选择
        self.chapter_combo = QComboBox()
        self.chapter_combo.currentIndexChanged.connect(self.load_questions)
        top_layout.addWidget(QLabel('选择章节:'))
        top_layout.addWidget(self.chapter_combo)
        
        layout.addLayout(top_layout)
        
        # 添加题目按钮
        add_btn = QPushButton('添加题目')
        add_btn.clicked.connect(self.show_question_dialog)
        layout.addWidget(add_btn)
        
        # 题目列表
        self.question_list = QListWidget()
        self.question_list.itemDoubleClicked.connect(self.edit_question)
        layout.addWidget(self.question_list)
        
        # 加载课程��表
        self.load_courses()
    
    def on_course_selected(self):
        """当选择课程时，加载对应的章节列表"""
        self.load_chapters()
        self.load_questions()
    
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
            self.course_combo.addItem('选择课程', None)
            for course_id, title in courses:
                self.course_combo.addItem(title, course_id)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
    
    def load_chapters(self):
        try:
            course_id = self.course_combo.currentData()
            if not course_id:
                self.chapter_combo.clear()
                self.chapter_combo.addItem('请先选择课程', None)
                return
                
            query = """
                SELECT chapter_id, title
                FROM Course_Chapters
                WHERE course_id = %s
                ORDER BY sequence_number
            """
            chapters = Database.execute_query(query, (course_id,))
            
            self.chapter_combo.clear()
            self.chapter_combo.addItem('选择章节', None)
            for chapter_id, title in chapters:
                self.chapter_combo.addItem(title, chapter_id)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载章节列表失败：{str(e)}')
    
    def load_questions(self):
        try:
            course_id = self.course_combo.currentData()
            chapter_id = self.chapter_combo.currentData()
            
            if not course_id:
                return
                
            query = """
                SELECT q.question_id, q.question_text, q.question_type,
                       q.correct_answer, q.points,
                       COUNT(o.option_id) as option_count
                FROM Test_Questions q
                LEFT JOIN Question_Options o ON q.question_id = o.question_id
                WHERE q.course_id = %s
            """
            params = [course_id]
            
            if chapter_id:
                query += " AND q.chapter_id = %s"
                params.append(chapter_id)
                
            query += """ 
                GROUP BY q.question_id, q.question_text, q.question_type,
                         q.correct_answer, q.points
                ORDER BY q.created_at DESC
            """
            
            questions = Database.execute_query(query, params)
            
            self.question_list.clear()
            for question in questions:
                q_id, text, q_type, answer, points, options = question
                
                item_text = (f"类型：{q_type}\n"
                           f"分值：{points}\n"
                           f"题目：{text}\n"
                           f"答案：{answer}")
                if q_type == 'multiple_choice':
                    item_text += f"\n选项数：{options}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, q_id)
                self.question_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载题目列表失败：{str(e)}')
    
    def show_question_dialog(self):
        course_id = self.course_combo.currentData()
        chapter_id = self.chapter_combo.currentData()
        
        if not course_id or not chapter_id:
            QMessageBox.warning(self, '提示', '请先选择课程和章节')
            return
            
        dialog = QuestionDialog(course_id, chapter_id)
        dialog.question_updated.connect(self.load_questions)
        dialog.exec_()
    
    def edit_question(self, item):
        question_id = item.data(Qt.UserRole)
        course_id = self.course_combo.currentData()
        chapter_id = self.chapter_combo.currentData()
        
        dialog = QuestionDialog(course_id, chapter_id, question_id)
        dialog.question_updated.connect(self.load_questions)
        dialog.exec_()

class QuestionDialog(QDialog):
    question_updated = pyqtSignal()
    
    def __init__(self, course_id, chapter_id, question_id=None):
        super().__init__()
        self.course_id = course_id
        self.chapter_id = chapter_id
        self.question_id = question_id
        
        self.setWindowTitle('题目信息')
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 题目类型
        type_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(['multiple_choice', 'true_false', 'essay'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(QLabel('题目类型:'))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 题目内容
        layout.addWidget(QLabel('题目内容:'))
        self.question_input = QTextEdit()
        self.question_input.setMaximumHeight(100)
        layout.addWidget(self.question_input)
        
        # 分值
        points_layout = QHBoxLayout()
        self.points_spin = QSpinBox()
        self.points_spin.setRange(1, 100)
        self.points_spin.setValue(1)
        points_layout.addWidget(QLabel('分值:'))
        points_layout.addWidget(self.points_spin)
        layout.addLayout(points_layout)
        
        # 选项区域（用于选择题）
        self.options_group = QGroupBox('选项')
        self.options_layout = QVBoxLayout()
        self.options_group.setLayout(self.options_layout)
        layout.addWidget(self.options_group)
        
        # 选项列表
        self.options_list = QListWidget()
        self.options_list.itemDoubleClicked.connect(self.edit_option)
        self.options_layout.addWidget(self.options_list)
        
        # 选项按钮
        options_btn_layout = QHBoxLayout()
        add_option_btn = QPushButton('添加选项')
        add_option_btn.clicked.connect(self.add_option)
        remove_option_btn = QPushButton('删除选项')
        remove_option_btn.clicked.connect(self.remove_option)
        set_correct_btn = QPushButton('设为正确答案')
        set_correct_btn.clicked.connect(self.set_correct_option)
        options_btn_layout.addWidget(add_option_btn)
        options_btn_layout.addWidget(remove_option_btn)
        options_btn_layout.addWidget(set_correct_btn)
        self.options_layout.addLayout(options_btn_layout)
        
        # 正确答案（用于非选择题）
        self.answer_group = QGroupBox('正确答案')
        answer_layout = QVBoxLayout()
        self.answer_input = QTextEdit()
        answer_layout.addWidget(self.answer_input)
        self.answer_group.setLayout(answer_layout)
        layout.addWidget(self.answer_group)
        
        # 保存按钮
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_question)
        layout.addWidget(save_btn)
        
        # 根据题目类型显示/隐藏相关控件
        self.on_type_changed(self.type_combo.currentText())
        
        # 如果是编辑模式，加载题目数据
        if question_id:
            self.load_question_data()
    
    def on_type_changed(self, question_type):
        """当题目类型改变时，显示/隐藏相关控件"""
        if question_type == 'multiple_choice':
            self.options_group.show()
            self.answer_group.hide()
        else:
            self.options_group.hide()
            self.answer_group.show()
    
    def load_question_data(self):
        try:
            # 加载题目基本信息
            query = """
                SELECT question_text, question_type, correct_answer, points
                FROM Test_Questions
                WHERE question_id = %s
            """
            result = Database.execute_query(query, (self.question_id,))
            
            if result:
                text, q_type, answer, points = result[0]
                self.question_input.setText(text)
                self.type_combo.setCurrentText(q_type)
                self.points_spin.setValue(points)
                
                if q_type == 'multiple_choice':
                    # 加载选项
                    options_query = """
                        SELECT option_text, is_correct
                        FROM Question_Options
                        WHERE question_id = %s
                        ORDER BY sequence_number
                    """
                    options = Database.execute_query(options_query, (self.question_id,))
                    
                    self.options_list.clear()
                    for option_text, is_correct in options:
                        item = QListWidgetItem(
                            f"{'[√]' if is_correct else '[ ]'} {option_text}")
                        self.options_list.addItem(item)
                else:
                    self.answer_input.setText(answer)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载题目信息失败：{str(e)}')
    
    def add_option(self):
        """添加新选项"""
        text, ok = QInputDialog.getText(self, '添加选项', '请输入选项内容:')
        if ok and text:
            item = QListWidgetItem(f"[ ] {text}")
            self.options_list.addItem(item)
    
    def edit_option(self, item):
        """编辑选项内容"""
        old_text = item.text()
        is_correct = old_text.startswith('[√]')
        option_text = old_text[4:]  # 去掉标记部分
        
        text, ok = QInputDialog.getText(self, '编辑选项',
                                      '请输入选项内容:', text=option_text)
        if ok and text:
            item.setText(f"{'[√]' if is_correct else '[ ]'} {text}")
    
    def remove_option(self):
        """删除选中的选项"""
        current_item = self.options_list.currentItem()
        if current_item:
            self.options_list.takeItem(self.options_list.row(current_item))
    
    def set_correct_option(self):
        """设置选中的选项为正确答案"""
        current_item = self.options_list.currentItem()
        if not current_item:
            return
            
        # 先将所有选项设为错误
        for i in range(self.options_list.count()):
            item = self.options_list.item(i)
            text = item.text()[4:]  # 去掉标记部分
            item.setText(f"[ ] {text}")
        
        # 设置当前选项为正确
        text = current_item.text()[4:]  # 去掉标记部分
        current_item.setText(f"[√] {text}")
    
    def save_question(self):
        question_text = self.question_input.toPlainText().strip()
        question_type = self.type_combo.currentText()
        points = self.points_spin.value()
        
        if not question_text:
            QMessageBox.warning(self, '错误', '请输入题目内容')
            return
        
        if question_type == 'multiple_choice':
            # 检查选项
            if self.options_list.count() < 2:
                QMessageBox.warning(self, '错误', '选择题至少需要两个选项')
                return
                
            # 检查是否有正确答案
            has_correct = False
            for i in range(self.options_list.count()):
                if self.options_list.item(i).text().startswith('[√]'):
                    has_correct = True
                    break
            
            if not has_correct:
                QMessageBox.warning(self, '错误', '请设置一个正确答案')
                return
        else:
            # 检查答案
            if not self.answer_input.toPlainText().strip():
                QMessageBox.warning(self, '错误', '请输入正确答案')
                return
        
        try:
            if self.question_id:
                # 更新题目
                query = """
                    UPDATE Test_Questions
                    SET question_text = %s, question_type = %s,
                        correct_answer = %s, points = %s
                    WHERE question_id = %s
                    RETURNING question_id
                """
                correct_answer = ''
                if question_type == 'multiple_choice':
                    for i in range(self.options_list.count()):
                        item = self.options_list.item(i)
                        if item.text().startswith('[√]'):
                            correct_answer = item.text()[4:]
                            break
                else:
                    correct_answer = self.answer_input.toPlainText().strip()
                
                result = Database.execute_query(query, (
                    question_text, question_type, correct_answer,
                    points, self.question_id
                ))
                question_id = self.question_id
            else:
                # 创建新题目
                query = """
                    INSERT INTO Test_Questions (course_id, chapter_id,
                        question_text, question_type, correct_answer, points)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING question_id
                """
                correct_answer = ''
                if question_type == 'multiple_choice':
                    for i in range(self.options_list.count()):
                        item = self.options_list.item(i)
                        if item.text().startswith('[√]'):
                            correct_answer = item.text()[4:]
                            break
                else:
                    correct_answer = self.answer_input.toPlainText().strip()
                
                result = Database.execute_query(query, (
                    self.course_id, self.chapter_id, question_text,
                    question_type, correct_answer, points
                ))
                question_id = result[0][0]
            
            # 如果是选择题，保存选项
            if question_type == 'multiple_choice':
                # 先删除旧选项
                if self.question_id:
                    delete_query = """
                        DELETE FROM Question_Options
                        WHERE question_id = %s
                    """
                    Database.execute_query(delete_query, (question_id,))
                
                # 添加新选项
                for i in range(self.options_list.count()):
                    item = self.options_list.item(i)
                    option_text = item.text()[4:]  # 去掉标记部分
                    is_correct = item.text().startswith('[√]')
                    
                    option_query = """
                        INSERT INTO Question_Options (question_id,
                            option_text, is_correct, sequence_number)
                        VALUES (%s, %s, %s, %s)
                    """
                    Database.execute_query(option_query, (
                        question_id, option_text, is_correct, i + 1
                    ))
            
            self.question_updated.emit()
            self.close()
            QMessageBox.information(self, '成功', '题目保存成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存失败：{str(e)}')