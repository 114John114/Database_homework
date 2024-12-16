from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QComboBox, QRadioButton, QButtonGroup,
                           QTextEdit, QFrame)
from PyQt5.QtCore import Qt
from database import Database

class TestCenterPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        self.load_tests()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 页面标题
        title_label = QLabel('测试中心')
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 20px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 测试列表
        self.test_table = QTableWidget()
        self.test_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.test_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.test_table.setSelectionMode(QTableWidget.SingleSelection)
        self.test_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
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
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        self.test_table.setColumnCount(6)
        self.test_table.setHorizontalHeaderLabels(
            ['课程', '章节', '题目数', '总分', '得分', '操作'])
        self.test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.test_table)
        
    def load_tests(self):
        try:
            query = """
                SELECT c.course_id, ch.chapter_id,
                       c.title, ch.title,
                       COUNT(q.question_id) as question_count,
                       SUM(q.points) as total_points,
                       ts.score,
                       ts.status
                FROM Student_Course sc
                JOIN Courses c ON sc.course_id = c.course_id
                JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Test_Questions q ON ch.chapter_id = q.chapter_id
                LEFT JOIN (
                    SELECT chapter_id, course_id, score, status
                    FROM Test_Submissions
                    WHERE student_id = %s
                ) ts ON ch.chapter_id = ts.chapter_id AND c.course_id = ts.course_id
                WHERE sc.student_id = %s
                GROUP BY c.course_id, ch.chapter_id, c.title, ch.title, ts.score, ts.status
                ORDER BY c.title, ch.title
            """
            tests = Database.execute_query(query, (self.user_id, self.user_id))
            
            self.test_table.setRowCount(len(tests))
            for i, test in enumerate(tests):
                course_id, chapter_id, course_name, chapter_name, \
                question_count, total_points, score, status = test
                
                # 课程名称
                self.test_table.setItem(i, 0, QTableWidgetItem(course_name))
                
                # 章节名称
                self.test_table.setItem(i, 1, QTableWidgetItem(chapter_name))
                
                # 题目数量
                self.test_table.setItem(i, 2, QTableWidgetItem(str(question_count)))
                
                # 总分
                self.test_table.setItem(i, 3, QTableWidgetItem(str(total_points)))
                
                # 得分
                self.test_table.setItem(i, 4, QTableWidgetItem(
                    str(score) if score is not None else '未完成'))
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                if status is None and question_count > 0:
                    # 开始测试按钮
                    start_btn = QPushButton('开始测试')
                    start_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border-radius: 3px;
                            padding: 5px 10px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
                    start_btn.clicked.connect(
                        lambda _, cid=course_id, chid=chapter_id: self.start_test(cid, chid))
                    btn_layout.addWidget(start_btn)
                else:
                    # 查看结果按钮
                    view_btn = QPushButton('查看结果')
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
                        lambda _, cid=chapter_id: self.view_result(cid))
                    btn_layout.addWidget(view_btn)
                
                btn_widget.setLayout(btn_layout)
                self.test_table.setCellWidget(i, 5, btn_widget)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载测试列表失败：{str(e)}')
    
    def start_test(self, course_id, chapter_id):
        try:
            dialog = TestDialog(self.user_id, course_id, chapter_id, self)
            dialog.exec_()
            self.load_tests()  # 刷新测试列表
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'启动测试失败：{str(e)}')
    
    def view_result(self, chapter_id):
        try:
            # 先获取测试的基本信息
            query = """
                SELECT ts.score, ts.answer,
                       c.title as course_name,
                       ch.title as chapter_name,
                       c.course_id
                FROM Test_Submissions ts
                JOIN Courses c ON ts.course_id = c.course_id
                JOIN Course_Chapters ch ON ts.chapter_id = ch.chapter_id
                WHERE ts.student_id = %s 
                AND ts.chapter_id = %s
                ORDER BY ts.submitted_at DESC
                LIMIT 1
            """
            result = Database.execute_query(query, (self.user_id, chapter_id))
            
            if not result:
                QMessageBox.warning(self, '错误', '未找到测试结果')
                return
            
            score, answer_str, course_name, chapter_name, course_id = result[0]
            try:
                answers = eval(answer_str) if answer_str else {}
            except:
                answers = {}
            
            # 获取题目和正确答案
            query = """
                SELECT q.question_id, q.question_text, q.correct_answer,
                       q.points, q.question_type, q.chapter_id
                FROM Test_Questions q
                WHERE q.chapter_id = %s
                ORDER BY q.question_id
            """
            questions = Database.execute_query(query, (chapter_id,))
            
            if not questions:
                QMessageBox.warning(self, '错误', '未找到题目信息')
                return
            
            # 显示结果对话框
            dialog = QDialog(self)
            dialog.setWindowTitle('测试结果')
            dialog.setMinimumWidth(800)
            
            layout = QVBoxLayout()
            layout.setSpacing(20)
            layout.setContentsMargins(20, 20, 20, 20)
            dialog.setLayout(layout)
            
            # 添加测试信息
            info_frame = QFrame()
            info_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            info_layout = QVBoxLayout(info_frame)
            
            info_label = QLabel(f"课程：{course_name}\n章节：{chapter_name}")
            info_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                }
            """)
            info_layout.addWidget(info_label)
            
            layout.addWidget(info_frame)
            
            # 添加结果表格
            result_table = QTableWidget()
            result_table.setEditTriggers(QTableWidget.NoEditTriggers)
            result_table.setSelectionBehavior(QTableWidget.SelectRows)
            result_table.setSelectionMode(QTableWidget.SingleSelection)
            result_table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 5px;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
            result_table.setColumnCount(5)
            result_table.setHorizontalHeaderLabels(
                ['题目', '你的答案', '正确答案', '分值', '得分'])
            result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            result_table.setRowCount(len(questions))
            total_points = 0
            earned_points = 0
            
            for i, question in enumerate(questions):
                q_id, q_text, correct_answer, points, q_type, _ = question
                
                # 题目
                result_table.setItem(i, 0, QTableWidgetItem(q_text))
                
                # 你的答案
                your_answer = answers.get(q_id, "未作答")  # 使用数字类型的键
                answer_item = QTableWidgetItem(str(your_answer))
                if your_answer != "未作答":
                    if str(your_answer) == str(correct_answer):
                        answer_item.setForeground(Qt.green)
                    else:
                        answer_item.setForeground(Qt.red)
                else:
                    answer_item.setForeground(Qt.gray)
                result_table.setItem(i, 1, answer_item)
                
                # 正确答案
                result_table.setItem(i, 2, QTableWidgetItem(str(correct_answer)))
                
                # 分值
                result_table.setItem(i, 3, QTableWidgetItem(str(points)))
                
                # 得分
                earned = points if str(your_answer) == str(correct_answer) else 0
                result_table.setItem(i, 4, QTableWidgetItem(str(earned)))
                
                total_points += points
                earned_points += earned
            
            layout.addWidget(result_table)
            
            # 添加总分信息
            score_frame = QFrame()
            score_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            score_layout = QVBoxLayout(score_frame)
            
            percentage = earned_points/total_points*100 if total_points > 0 else 0
            status = "通过" if percentage >= 60 else "未通过"
            status_color = "#4CAF50" if percentage >= 60 else "#f44336"
            
            score_label = QLabel(
                f'总分: {earned_points}/{total_points} ({percentage:.1f}%)\n'
                f'状态: {status}'
            )
            score_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: bold;
                    color: {status_color};
                }}
            """)
            score_layout.addWidget(score_label)
            
            layout.addWidget(score_frame)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'查看测试结果失败：{str(e)}')

class TestDialog(QDialog):
    def __init__(self, user_id, course_id, chapter_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.course_id = course_id
        self.chapter_id = chapter_id
        self.questions = []
        self.answers = {}
        self.current_question = 0
        
        self.load_questions()
        self.setup_ui()
        
    def load_questions(self):
        try:
            query = """
                SELECT question_id, question_text, question_type,
                       points, correct_answer
                FROM Test_Questions
                WHERE chapter_id = %s
                ORDER BY question_id
            """
            self.questions = Database.execute_query(query, (self.chapter_id,))
            
            # 加载选择题选项
            for i, question in enumerate(self.questions):
                if question[2] == 'multiple_choice':
                    option_query = """
                        SELECT option_text
                        FROM Question_Options
                        WHERE question_id = %s
                        ORDER BY sequence_number
                    """
                    options = Database.execute_query(option_query, (question[0],))
                    self.questions[i] = list(question) + [options]
                else:
                    self.questions[i] = list(question) + [None]
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载题目失败：{str(e)}')
            self.reject()
    
    def setup_ui(self):
        self.setWindowTitle('测试')
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 题目区域
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.question_label)
        
        # 答案区域
        self.answer_widget = QWidget()
        self.answer_layout = QVBoxLayout()
        self.answer_widget.setLayout(self.answer_layout)
        layout.addWidget(self.answer_widget)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton('上一题')
        self.prev_btn.clicked.connect(self.prev_question)
        btn_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton('下一题')
        self.next_btn.clicked.connect(self.next_question)
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(btn_layout)
        
        # 显示第一题
        self.show_question()
    
    def show_question(self):
        if not self.questions:
            return
        
        question = self.questions[self.current_question]
        q_id, text, q_type, points, correct, options = question
        
        # 更新题��文本
        self.question_label.setText(
            f'第 {self.current_question + 1}/{len(self.questions)} 题 '
            f'({points}分)\n\n{text}')
        
        # 清空答案区域
        for i in reversed(range(self.answer_layout.count())): 
            self.answer_layout.itemAt(i).widget().setParent(None)
        
        # 根据题目类型显示不同的答案输入控件
        if q_type == 'multiple_choice':
            # 选择题显示选项
            self.option_group = QButtonGroup()
            for i, (option,) in enumerate(options):
                radio = QRadioButton(option)
                self.option_group.addButton(radio, i)
                self.answer_layout.addWidget(radio)
                
                # 如果已经答过这题，选中之前的答案
                if q_id in self.answers and self.answers[q_id] == option:
                    radio.setChecked(True)
        else:
            # 其他题型显示文本框
            self.answer_input = QTextEdit()
            self.answer_layout.addWidget(self.answer_input)
            
            # 如果已经答过这题，显示之前的答案
            if q_id in self.answers:
                self.answer_input.setText(self.answers[q_id])
        
        # 更新按钮状态
        self.prev_btn.setEnabled(self.current_question > 0)
        if self.current_question == len(self.questions) - 1:
            self.next_btn.setText('提交')
        else:
            self.next_btn.setText('下一题')
    
    def save_current_answer(self):
        if not self.questions:
            return
            
        question = self.questions[self.current_question]
        q_id, _, q_type, _, _, _ = question
        
        if q_type == 'multiple_choice':
            selected = self.option_group.checkedButton()
            if selected:
                self.answers[q_id] = selected.text()
        else:
            answer = self.answer_input.toPlainText().strip()
            if answer:
                self.answers[q_id] = answer
    
    def prev_question(self):
        self.save_current_answer()
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()
    
    def next_question(self):
        self.save_current_answer()
        
        if self.current_question == len(self.questions) - 1:
            # 最后一题，提交答案
            self.submit_test()
        else:
            self.current_question += 1
            self.show_question()
    
    def submit_test(self):
        # 检查是否所有题目都已答
        unanswered = []
        for i, question in enumerate(self.questions):
            if question[0] not in self.answers:
                unanswered.append(i + 1)
        
        if unanswered:
            reply = QMessageBox.question(
                self, '确认提交',
                f'第 {", ".join(map(str, unanswered))} 题还没有回答，'
                f'确定要提交吗？',
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
        
        try:
            # 计算得分
            total_score = 0
            total_points = 0
            for question in self.questions:
                q_id, _, _, points, correct, _ = question
                total_points += points
                if q_id in self.answers and self.answers[q_id] == correct:
                    total_score += points
            
            # 计算百分比得分
            percentage_score = (total_score / total_points * 100) if total_points > 0 else 0
            
            # 保存答案和分数
            query = """
                INSERT INTO Test_Submissions (
                    student_id, course_id, chapter_id,
                    score, answer, status
                ) VALUES (%s, %s, %s, %s, %s, 'graded')
            """
            Database.execute_query(query, (
                self.user_id, self.course_id, self.chapter_id,
                percentage_score, str(self.answers)
            ))
            
            QMessageBox.information(
                self, '成功', 
                f'测试已完成！\n得分：{percentage_score:.1f}分\n'
                f'状态：{"通过" if percentage_score >= 60 else "未通过"}'
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'提交测试失败：{str(e)}') 