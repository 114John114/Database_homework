from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem,
                           QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from database import Database

class StudentProgressPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 顶部布局
        top_layout = QHBoxLayout()
        
        # 课程选择
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.load_progress)
        top_layout.addWidget(QLabel('选择课程:'))
        top_layout.addWidget(self.course_combo)
        
        layout.addLayout(top_layout)
        
        # 进度列表
        self.progress_list = QListWidget()
        layout.addWidget(self.progress_list)
        
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
            for course_id, title in courses:
                self.course_combo.addItem(title, course_id)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
    
    def load_progress(self):
        try:
            course_id = self.course_combo.currentData()
            if not course_id:
                return
                
            query = """
                SELECT u.user_id, u.username,
                       COUNT(DISTINCT ch.chapter_id) as total_chapters,
                       COUNT(DISTINCT CASE WHEN lp.status = 'completed' 
                           THEN ch.chapter_id END) as completed_chapters,
                       AVG(lp.progress_percentage) as avg_progress,
                       COUNT(DISTINCT ts.submission_id) as test_count,
                       AVG(CASE WHEN ts.status = 'graded' 
                           THEN ts.score END) as avg_score
                FROM Users u
                JOIN Student_Course sc ON sc.course_id = %s
                JOIN Course_Progress lp ON u.user_id = lp.student_id
                    AND sc.course_id = lp.course_id
                JOIN Course_Chapters ch ON lp.course_id = ch.course_id
                LEFT JOIN Test_Submissions ts ON u.user_id = ts.student_id 
                    AND lp.course_id = ts.course_id
                WHERE sc.course_id = %s
                GROUP BY u.user_id, u.username
                ORDER BY u.username
            """
            progress_data = Database.execute_query(query, (course_id, course_id))
            
            self.progress_list.clear()
            for data in progress_data:
                user_id, username, total, completed, avg_progress, test_count, avg_score = data
                
                # 计算完成百分比
                completion = avg_progress if avg_progress else 0
                
                # 格式化平均分
                score_str = f"{avg_score:.1f}" if avg_score else "暂无成绩"
                
                item_text = (f"学生：{username}\n"
                           f"进度：{completion:.1f}% ({completed}/{total}章)\n"
                           f"已完成测试：{test_count}个\n"
                           f"平均测试分数：{score_str}")
                
                self.progress_list.addItem(QListWidgetItem(item_text))
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载学习进度失败：{str(e)}')