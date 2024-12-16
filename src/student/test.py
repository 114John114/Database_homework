from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QRadioButton, QButtonGroup, QTextEdit,
                           QPushButton, QMessageBox)
from database import Database
from datetime import datetime
from PyQt5.QtCore import QTimer

class TestWindow(QMainWindow):
    def __init__(self, user_id, chapter_id):
        super().__init__()
        self.user_id = user_id
        self.chapter_id = chapter_id
        
        self.setWindowTitle('章节测试')
        self.setMinimumSize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.questions = []
        self.current_question = 0
        self.answers = {}
        
        # 加载题目
        self.load_questions()
        
        # 显示第一题
        self.question_widget = QWidget()
        layout.addWidget(self.question_widget)
        
        # 提交按钮
        submit_button = QPushButton('提交答案')
        submit_button.clicked.connect(self.submit_test)
        layout.addWidget(submit_button)
        
        self.start_time = datetime.now()
        self.test_timer = QTimer()
        self.test_timer.setInterval(1000)  # 每秒更新
        self.test_timer.timeout.connect(self.update_time_display)
        self.test_timer.start()
        
        # 添加时间显示标签
        self.time_label = QLabel('用时：0:00')
        layout.addWidget(self.time_label)
        
        self.show_question(0)
    
    def load_questions(self):
        query = """
            SELECT question_id, question_text, question_type, points
            FROM Test_Questions
            WHERE chapter_id = %s
            ORDER BY RANDOM()
        """
        self.questions = Database.execute_query(query, (self.chapter_id,))
    
    def show_question(self, index):
        if 0 <= index < len(self.questions):
            question = self.questions[index]
            
            # 清除旧的问题显示
            layout = QVBoxLayout()
            old_widget = self.question_widget
            self.question_widget = QWidget()
            self.question_widget.setLayout(layout)
            old_widget.parent().layout().replaceWidget(old_widget, self.question_widget)
            old_widget.deleteLater()
            
            # 显示问题
            layout.addWidget(QLabel(f"问题 {index + 1}/{len(self.questions)}"))
            layout.addWidget(QLabel(question[1]))
            
            if question[2] == 'multiple_choice':
                self.show_multiple_choice(question[0], layout)
            elif question[2] == 'true_false':
                self.show_true_false(question[0], layout)
            else:  # essay
                self.show_essay(question[0], layout)
            
            # 导航按钮
            nav_layout = QHBoxLayout()
            if index > 0:
                prev_button = QPushButton('上一题')
                prev_button.clicked.connect(lambda: self.show_question(index - 1))
                nav_layout.addWidget(prev_button)
            
            if index < len(self.questions) - 1:
                next_button = QPushButton('下一题')
                next_button.clicked.connect(lambda: self.show_question(index + 1))
                nav_layout.addWidget(next_button)
            
            layout.addLayout(nav_layout)
    
    def show_multiple_choice(self, question_id, layout):
        query = """
            SELECT option_id, option_text
            FROM Question_Options
            WHERE question_id = %s
            ORDER BY sequence_number
        """
        options = Database.execute_query(query, (question_id,))
        
        button_group = QButtonGroup(self)
        for option in options:
            radio = QRadioButton(option[1])
            button_group.addButton(radio, option[0])
            layout.addWidget(radio)
            
            if question_id in self.answers:
                if self.answers[question_id] == option[0]:
                    radio.setChecked(True)
        
        button_group.buttonClicked.connect(
            lambda btn: self.save_answer(question_id, button_group.id(btn))
        )
    
    def show_true_false(self, question_id, layout):
        button_group = QButtonGroup(self)
        true_radio = QRadioButton('正确')
        false_radio = QRadioButton('错误')
        button_group.addButton(true_radio, 1)
        button_group.addButton(false_radio, 0)
        layout.addWidget(true_radio)
        layout.addWidget(false_radio)
        
        if question_id in self.answers:
            if self.answers[question_id]:
                true_radio.setChecked(True)
            else:
                false_radio.setChecked(True)
        
        button_group.buttonClicked.connect(
            lambda btn: self.save_answer(question_id, button_group.id(btn))
        )
    
    def show_essay(self, question_id, layout):
        answer_edit = QTextEdit()
        layout.addWidget(answer_edit)
        
        if question_id in self.answers:
            answer_edit.setText(self.answers[question_id])
        
        answer_edit.textChanged.connect(
            lambda: self.save_answer(question_id, answer_edit.toPlainText())
        )
    
    def save_answer(self, question_id, answer):
        self.answers[question_id] = answer
    
    def submit_test(self):
        self.test_timer.stop()
        elapsed_minutes = int((datetime.now() - self.start_time).total_seconds() / 60)
        
        if len(self.answers) < len(self.questions):
            reply = QMessageBox.question(
                self, '确认提交',
                '还有题目未完成，确定要提交吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        score = self.calculate_score()
        status = 'passed' if score >= 60 else 'failed'
        
        try:
            query = """
                INSERT INTO Test_Submissions 
                (student_id, course_id, chapter_id, score, answer, status)
                VALUES (%s, %s, %s, %s, %s, 'graded')
            """
            Database.execute_query(query, (
                self.user_id, self.course_id, self.chapter_id, 
                score, str(self.answers), status
            ))
            
            QMessageBox.information(
                self, '完成',
                f'测试已完成！\n得分：{score}\n状态：{status}'
            )
            self.close()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'提交失败：{str(e)}')
    
    def calculate_score(self):
        total_points = 0
        earned_points = 0
        
        for question in self.questions:
            question_id = question[0]
            points = question[3]
            total_points += points
            
            if question_id in self.answers:
                if question[2] in ('multiple_choice', 'true_false'):
                    query = """
                        SELECT is_correct
                        FROM Question_Options
                        WHERE option_id = %s
                    """
                    result = Database.execute_query(
                        query, (self.answers[question_id],)
                    )
                    if result and result[0][0]:
                        earned_points += points
        
        return (earned_points / total_points) * 100 if total_points > 0 else 0 
    
    def update_time_display(self):
        elapsed = datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() / 60)
        seconds = int(elapsed.total_seconds() % 60)
        self.time_label.setText(f'用时：{minutes}:{seconds:02d}')