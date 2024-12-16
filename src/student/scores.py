from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
                           QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from database import Database
from datetime import datetime

class ScoresPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 成绩表格
        self.scores_table = QTableWidget()
        self.scores_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.scores_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.scores_table.setSelectionMode(QTableWidget.SingleSelection)
        self.scores_table.setStyleSheet("""
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
        
        # 设置列
        self.scores_table.setColumnCount(6)
        self.scores_table.setHorizontalHeaderLabels([
            '课程名称', '章节名称', '得分', '总分', '状态', '提交时间'
        ])
        self.scores_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.scores_table)
        
        self.load_scores()
    
    def load_scores(self):
        try:
            query = """
                SELECT c.title as course_name, 
                       ch.title as chapter_name,
                       ts.score,
                       (SELECT SUM(points) 
                        FROM Test_Questions 
                        WHERE chapter_id = ch.chapter_id) as total_points,
                       ts.status,
                       ts.submitted_at
                FROM Student_Course sc
                JOIN Courses c ON sc.course_id = c.course_id
                JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Test_Submissions ts ON ts.chapter_id = ch.chapter_id 
                    AND ts.student_id = sc.student_id
                WHERE sc.student_id = %s
                ORDER BY c.title, ch.sequence_number
            """
            scores = Database.execute_query(query, (self.user_id,))
            
            self.scores_table.setRowCount(len(scores))
            for i, score in enumerate(scores):
                course_name, chapter_name, score_val, total_points, status, submitted_at = score
                
                # 课程名称
                self.scores_table.setItem(i, 0, QTableWidgetItem(course_name))
                
                # 章节名称
                self.scores_table.setItem(i, 1, QTableWidgetItem(chapter_name))
                
                # 得分
                score_str = f"{score_val:.1f}" if score_val is not None else "未作答"
                score_item = QTableWidgetItem(score_str)
                if score_val is not None:
                    score_item.setForeground(
                        Qt.green if score_val >= 60 else Qt.red
                    )
                else:
                    score_item.setForeground(Qt.gray)
                self.scores_table.setItem(i, 2, score_item)
                
                # 总分
                total_str = str(total_points) if total_points else "0"
                self.scores_table.setItem(i, 3, QTableWidgetItem(total_str))
                
                # 状态
                if score_val is not None:
                    status_text = "通过" if score_val >= 60 else "未通过"
                    status_item = QTableWidgetItem(status_text)
                    status_item.setForeground(
                        Qt.green if score_val >= 60 else Qt.red
                    )
                else:
                    status_item = QTableWidgetItem("未作答")
                    status_item.setForeground(Qt.gray)
                self.scores_table.setItem(i, 4, status_item)
                
                # 提交时间
                if submitted_at:
                    submitted_str = submitted_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    submitted_str = "未提交"
                self.scores_table.setItem(i, 5, QTableWidgetItem(submitted_str))
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载成绩失败：{str(e)}')
    
    # ... ScoresPage的其他方法 ... 