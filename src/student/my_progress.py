from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                           QTableWidgetItem, QHeaderView, QProgressBar,
                           QMessageBox)
from database import Database

class MyProgressPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        self.load_progress()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 页面标题
        title_label = QLabel('学习进度')
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 20px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 进度列表
        self.progress_list = QTableWidget()
        self.progress_list.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为只读
        self.progress_list.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.progress_list.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择
        self.progress_list.setStyleSheet("""
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
        self.progress_list.setColumnCount(5)
        self.progress_list.setHorizontalHeaderLabels(
            ['课程名称', '教师', '总章节', '已完成', '进度'])
        self.progress_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.progress_list)
        
    def load_progress(self):
        try:
            query = """
                SELECT c.title, u.username as teacher_name,
                       COUNT(DISTINCT ch.chapter_id) as total_chapters,
                       COUNT(DISTINCT cp.chapter_id) as completed_chapters
                FROM Student_Course sc
                JOIN Courses c ON sc.course_id = c.course_id
                JOIN Users u ON c.instructor_id = u.user_id
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Course_Progress cp ON c.course_id = cp.course_id 
                    AND cp.student_id = sc.student_id 
                    AND cp.status = 'completed'
                WHERE sc.student_id = %s
                GROUP BY c.title, u.username
                ORDER BY c.title
            """
            progress = Database.execute_query(query, (self.user_id,))
            
            self.progress_list.setRowCount(len(progress))
            for i, course in enumerate(progress):
                name, teacher, total, completed = course
                
                # 课程名称
                self.progress_list.setItem(i, 0, QTableWidgetItem(name))
                
                # 教师名称
                self.progress_list.setItem(i, 1, QTableWidgetItem(teacher))
                
                # 总章节数
                self.progress_list.setItem(i, 2, QTableWidgetItem(str(total)))
                
                # 已完成章节
                self.progress_list.setItem(i, 3, QTableWidgetItem(str(completed)))
                
                # 进度条
                progress = 0 if not total else (completed / total * 100)
                progress_bar = QProgressBar()
                progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #ddd;
                        border-radius: 3px;
                        text-align: center;
                        background-color: #f5f5f5;
                    }
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                    }
                """)
                progress_bar.setMinimum(0)
                progress_bar.setMaximum(100)
                progress_bar.setValue(int(progress))
                progress_bar.setFormat(f"{progress:.1f}%")
                self.progress_list.setCellWidget(i, 4, progress_bar)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载学习进度失败：{str(e)}') 