from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                           QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from database import Database

class ProgressPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 进度列表
        self.progress_list = QListWidget()
        layout.addWidget(self.progress_list)
        
        self.load_progress()
    
    def load_progress(self):
        try:
            query = """
                SELECT c.title, ch.title, lp.progress_percentage,
                       lp.status, lp.study_time, lp.last_study_time
                FROM Learning_Progress lp
                JOIN Courses c ON lp.course_id = c.course_id
                JOIN Course_Chapters ch ON lp.chapter_id = ch.chapter_id
                WHERE lp.user_id = %s
                ORDER BY c.title, ch.sequence_number
            """
            progress_data = Database.execute_query(query, (self.user_id,))
            
            self.progress_list.clear()
            for data in progress_data:
                course_title, chapter_title, progress, status, study_time, last_study = data
                
                # 格式化学习时间
                hours = study_time // 60
                minutes = study_time % 60
                time_str = f"{hours}小时{minutes}分钟" if hours > 0 else f"{minutes}分钟"
                
                # 格式化最后学习时间
                last_study_str = last_study.strftime("%Y-%m-%d %H:%M:%S") if last_study else "未开始学习"
                
                item_text = (f"课程：{course_title}\n"
                           f"章节：{chapter_title}\n"
                           f"进度：{progress}%\n"
                           f"状态：{status}\n"
                           f"学习时长：{time_str}\n"
                           f"最后学习：{last_study_str}")
                
                item = QListWidgetItem(item_text)
                self.progress_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载学习进度失败：{str(e)}')
    
    # ... ProgressPage的其他方法 ... 