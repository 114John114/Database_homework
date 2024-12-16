from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QComboBox, QFileDialog, QFrame,
                           QLineEdit)
from PyQt5.QtCore import Qt
from database import Database
from datetime import datetime
import os
import shutil

class ChapterStudyDialog(QDialog):
    def __init__(self, user_id, course_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.course_id = course_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('章节学习')
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 章节选择区域
        chapter_frame = QFrame()
        chapter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        chapter_layout = QVBoxLayout(chapter_frame)
        
        # 章节选择标题
        chapter_title = QLabel('选择学习章节')
        chapter_title.setProperty('heading', True)
        chapter_layout.addWidget(chapter_title)
        
        # 章节下拉框
        self.chapter_combo = QComboBox()
        self.chapter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.chapter_combo.currentIndexChanged.connect(self.load_chapter_content)
        chapter_layout.addWidget(self.chapter_combo)
        
        layout.addWidget(chapter_frame)
        
        # 内容显示区域
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        
        # 内容标题
        content_title = QLabel('章节内容')
        content_title.setProperty('heading', True)
        content_layout.addWidget(content_title)
        
        # 内容显示
        self.content_label = QLabel('章节内容将在这里显示')
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 20px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        content_layout.addWidget(self.content_label)
        
        # 下载按钮
        download_btn = QPushButton('下载课程文件')
        download_btn.setProperty('success', True)
        download_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
            }
        """)
        download_btn.clicked.connect(self.download_content)
        content_layout.addWidget(download_btn)
        
        layout.addWidget(content_frame)
        
        # 进度区域
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        progress_layout = QHBoxLayout(progress_frame)
        
        self.progress_label = QLabel('学习进度: 0%')
        self.progress_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        progress_layout.addWidget(self.progress_label)
        
        self.complete_btn = QPushButton('完成学习')
        self.complete_btn.setProperty('success', True)
        self.complete_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
            }
        """)
        self.complete_btn.clicked.connect(self.complete_chapter)
        progress_layout.addWidget(self.complete_btn)
        
        layout.addWidget(progress_frame)
        
        # 加载章节列表
        self.load_chapters()
        
    def load_chapters(self):
        try:
            query = """
                SELECT ch.chapter_id, ch.title,
                       COALESCE(cp.progress_percentage, 0) as progress,
                       COALESCE(cp.status, 'not_started') as status
                FROM Course_Chapters ch
                LEFT JOIN Course_Progress cp ON ch.chapter_id = cp.chapter_id
                    AND cp.student_id = %s
                WHERE ch.course_id = %s
                ORDER BY ch.sequence_number
            """
            chapters = Database.execute_query(query, (self.user_id, self.course_id))
            
            self.chapter_combo.clear()
            for chapter_id, title, progress, status in chapters:
                self.chapter_combo.addItem(
                    f"{title} ({progress}% - {status})", 
                    userData=chapter_id
                )
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载章节列表失败：{str(e)}')
            
    def load_chapter_content(self):
        try:
            chapter_id = self.chapter_combo.currentData()
            if not chapter_id:
                return
                
            query = """
                SELECT content_url, content_type, description
                FROM Course_Chapters
                WHERE chapter_id = %s
            """
            result = Database.execute_query(query, (chapter_id,))
            
            if result:
                content_url, content_type, description = result[0]
                content = f"内容类型: {content_type}\n\n"
                content += f"内容地址: {content_url}\n\n"
                content += f"章节描述:\n{description}"
                self.content_label.setText(content)
                
                # 先检查是否存在学习记录
                check_query = """
                    SELECT progress_percentage
                    FROM Course_Progress
                    WHERE student_id = %s 
                        AND course_id = %s 
                        AND chapter_id = %s
                """
                progress = Database.execute_query(
                    check_query,
                    (self.user_id, self.course_id, chapter_id)
                )
                
                if progress:
                    # 如果存在，更新最后访问时间
                    update_query = """
                        UPDATE Course_Progress
                        SET last_accessed = CURRENT_TIMESTAMP
                        WHERE student_id = %s 
                            AND course_id = %s 
                            AND chapter_id = %s
                        RETURNING progress_percentage
                    """
                    progress = Database.execute_query(
                        update_query,
                        (self.user_id, self.course_id, chapter_id)
                    )
                else:
                    # 如果不存在，创建新记录
                    insert_query = """
                        INSERT INTO Course_Progress 
                        (student_id, course_id, chapter_id, status, 
                         progress_percentage, last_accessed)
                        VALUES (%s, %s, %s, 'in_progress', 0, CURRENT_TIMESTAMP)
                        RETURNING progress_percentage
                    """
                    progress = Database.execute_query(
                        insert_query,
                        (self.user_id, self.course_id, chapter_id)
                    )
                
                if progress:
                    self.progress_label.setText(f'学习进度: {progress[0][0]}%')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载章节内容失败：{str(e)}')
            
    def complete_chapter(self):
        try:
            chapter_id = self.chapter_combo.currentData()
            if not chapter_id:
                return
                
            # 更新学习进度
            query = """
                UPDATE Course_Progress
                SET status = 'completed',
                    progress_percentage = 100,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE student_id = %s
                    AND course_id = %s
                    AND chapter_id = %s
            """
            Database.execute_query(query, (self.user_id, self.course_id, chapter_id))
            
            # 刷新章节列表
            self.load_chapters()
            self.progress_label.setText('学习进度: 100%')
            QMessageBox.information(self, '成功', '恭喜你完成本章节的学习！')
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'更新学习进度失败：{str(e)}')
            
    def download_content(self):
        try:
            chapter_id = self.chapter_combo.currentData()
            if not chapter_id:
                return
                
            # 获取文件信息
            query = """
                SELECT content_url, content_type, title
                FROM Course_Chapters
                WHERE chapter_id = %s
            """
            result = Database.execute_query(query, (chapter_id,))
            
            if not result or not result[0][0]:
                QMessageBox.warning(self, '错误', '该章节没有可下载的文件')
                return
                
            content_url, content_type, title = result[0]
            
            # 确定文件扩展名
            ext = '.mp4' if content_type == 'video' else '.docx'
            
            # 让用户选择保存位置
            file_name = f"{title}{ext}"
            save_path, _ = QFileDialog.getSaveFileName(
                self, '保存文件', file_name, 
                'Video Files (*.mp4)' if content_type == 'video' else 'Word Files (*.docx)'
            )
            
            if save_path:
                # 复制文件到用户选择的位置
                shutil.copy2(content_url, save_path)
                QMessageBox.information(self, '成功', '文件下载完成！')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'下载文件失败：{str(e)}')

class CourseListPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # 标题和搜索栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel('课程列表')
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
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 课程表格
        self.course_table = QTableWidget()
        self.course_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.course_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.course_table.setSelectionMode(QTableWidget.SingleSelection)
        self.course_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
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
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        
        # 设置列
        self.course_table.setColumnCount(7)
        self.course_table.setHorizontalHeaderLabels([
            '课程名称', '教师', '难度', '进度', '状态', '选课状态', '操作'
        ])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.course_table)
        
        self.load_courses()
        
    def load_courses(self):
        try:
            query = """
                SELECT c.course_id, c.title, u.username as teacher,
                       c.difficulty_level,
                       COUNT(DISTINCT ch.chapter_id) as total_chapters,
                       COUNT(DISTINCT CASE WHEN cp.status = 'completed' 
                           THEN cp.chapter_id END) as completed_chapters,
                       CASE WHEN sc.student_id IS NOT NULL THEN true
                           ELSE false END as is_enrolled
                FROM Courses c
                JOIN Users u ON c.instructor_id = u.user_id
                LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                LEFT JOIN Student_Course sc ON c.course_id = sc.course_id 
                    AND sc.student_id = %s
                LEFT JOIN Course_Progress cp ON c.course_id = cp.course_id
                    AND cp.student_id = sc.student_id
                WHERE c.status = 'active'
                GROUP BY c.course_id, c.title, u.username, c.difficulty_level,
                         sc.student_id
                ORDER BY is_enrolled DESC, c.title
            """
            courses = Database.execute_query(query, (self.user_id,))
            
            self.course_table.setRowCount(len(courses))
            for i, course in enumerate(courses):
                course_id, title, teacher, difficulty, total, completed, enrolled = course
                
                # 课程名称
                self.course_table.setItem(i, 0, QTableWidgetItem(title))
                
                # 教师名称
                self.course_table.setItem(i, 1, QTableWidgetItem(teacher))
                
                # 难度
                self.course_table.setItem(i, 2, QTableWidgetItem(difficulty))
                
                # 进度
                progress = (completed / total * 100) if total > 0 and enrolled else 0
                self.course_table.setItem(i, 3, 
                    QTableWidgetItem(f"{progress:.1f}% ({completed}/{total})"))
                
                # 状态
                status = "已完成" if completed == total and total > 0 and enrolled \
                        else "学习中" if enrolled else "-"
                self.course_table.setItem(i, 4, QTableWidgetItem(status))
                
                # 选课状态
                self.course_table.setItem(i, 5, 
                    QTableWidgetItem("已选" if enrolled else "未选"))
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setSpacing(10)
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                if enrolled:
                    # 继续学习按钮
                    study_btn = QPushButton('继续学习')
                    study_btn.setProperty('success', True)
                    study_btn.setStyleSheet("""
                        QPushButton {
                            font-size: 12px;
                            padding: 5px 10px;
                            min-width: 60px;
                        }
                    """)
                    study_btn.clicked.connect(
                        lambda _, cid=course_id: self.start_study(cid))
                    btn_layout.addWidget(study_btn)
                    
                    # 退课按钮
                    drop_btn = QPushButton('退课')
                    drop_btn.setProperty('danger', True)
                    drop_btn.setStyleSheet("""
                        QPushButton {
                            font-size: 12px;
                            padding: 5px 10px;
                            min-width: 60px;
                        }
                    """)
                    drop_btn.clicked.connect(
                        lambda _, cid=course_id: self.drop_course(cid))
                    btn_layout.addWidget(drop_btn)
                else:
                    # 选课按钮
                    enroll_btn = QPushButton('选课')
                    enroll_btn.setStyleSheet("""
                        QPushButton {
                            font-size: 12px;
                            padding: 5px 10px;
                            min-width: 60px;
                        }
                    """)
                    enroll_btn.clicked.connect(
                        lambda _, cid=course_id: self.enroll_course(cid))
                    btn_layout.addWidget(enroll_btn)
                
                btn_widget.setLayout(btn_layout)
                self.course_table.setCellWidget(i, 6, btn_widget)
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
            
    def start_study(self, course_id):
        try:
            dialog = ChapterStudyDialog(self.user_id, course_id, self)
            dialog.exec_()
            # 刷新课程列表以更新进度
            self.load_courses()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开学习界面失败：{str(e)}')
            
    def enroll_course(self, course_id):
        try:
            # 添加选课记录
            query = """
                INSERT INTO Student_Course (student_id, course_id)
                VALUES (%s, %s)
            """
            Database.execute_query(query, (self.user_id, course_id))
            
            self.load_courses()
            QMessageBox.information(self, '成功', '选课成功！')
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'选课失败：{str(e)}')
            
    def drop_course(self, course_id):
        reply = QMessageBox.question(
            self, '确认退课',
            '确定要退出这门课程吗？\n退课后学习进度将被清空！',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除学习进度和选课记录
                queries = [
                    "DELETE FROM Course_Progress WHERE student_id = %s AND course_id = %s",
                    "DELETE FROM Student_Course WHERE student_id = %s AND course_id = %s"
                ]
                
                for query in queries:
                    Database.execute_query(query, (self.user_id, course_id))
                
                self.load_courses()
                QMessageBox.information(self, '成功', '已退出课程！')
                
            except Exception as e:
                QMessageBox.warning(self, '错误', f'退课失败：{str(e)}')
            
    def search_courses(self, text):
        for i in range(self.course_table.rowCount()):
            match = False
            for j in range(self.course_table.columnCount() - 1):  # 不搜索操作列
                item = self.course_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.course_table.setRowHidden(i, not match) 