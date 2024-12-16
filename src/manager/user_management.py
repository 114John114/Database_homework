from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from database import Database

class UserManagementPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # 标题
        title_label = QLabel('用户管理')
        title_label.setProperty('heading', True)
        layout.addWidget(title_label)
        
        # 用户列表
        self.user_table = QTableWidget()
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # 设置列
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            '用户ID', '用户名', '角色', '注册时间', '最后登录', '详细信息'
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.user_table)
        
        self.load_users()
        
    def load_users(self):
        try:
            query = """
                SELECT u.user_id, u.username, u.role, u.created_at,
                       u.last_login,
                       COUNT(DISTINCT sc.course_id) as enrolled_courses,
                       COUNT(DISTINCT cp.chapter_id) as completed_chapters,
                       COUNT(DISTINCT ts.submission_id) as test_count,
                       AVG(ts.score) as avg_score
                FROM Users u
                LEFT JOIN Student_Course sc ON u.user_id = sc.student_id
                LEFT JOIN Course_Progress cp ON u.user_id = cp.student_id
                LEFT JOIN Test_Submissions ts ON u.user_id = ts.student_id
                GROUP BY u.user_id, u.username, u.role, u.created_at,
                         u.last_login
                ORDER BY u.user_id
            """
            users = Database.execute_query(query)
            
            self.user_table.setRowCount(len(users))
            for i, user in enumerate(users):
                (user_id, username, role, created_at, last_login,
                 enrolled_courses, completed_chapters, test_count, avg_score) = user
                
                # 用户ID
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user_id)))
                
                # 用户名
                self.user_table.setItem(i, 1, QTableWidgetItem(username))
                
                # 角色
                role_map = {
                    'admin': '管理员',
                    'teacher': '教师',
                    'student': '学生'
                }
                self.user_table.setItem(i, 2, QTableWidgetItem(role_map.get(role, role)))
                
                # 注册时间
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else '-'
                self.user_table.setItem(i, 3, QTableWidgetItem(created_str))
                
                # 最后登录
                login_str = last_login.strftime("%Y-%m-%d %H:%M:%S") if last_login else '-'
                self.user_table.setItem(i, 4, QTableWidgetItem(login_str))
                
                # 详细信息按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 2, 5, 2)
                
                detail_btn = QPushButton('查看详情')
                detail_btn.clicked.connect(
                    lambda _, uid=user_id: self.show_user_details(uid))
                btn_layout.addWidget(detail_btn)
                
                btn_widget.setLayout(btn_layout)
                self.user_table.setCellWidget(i, 5, btn_widget)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载用户列表失败：{str(e)}')
            
    def show_user_details(self, user_id):
        try:
            # 获取用户基本信息
            query = """
                SELECT u.username, u.role, u.created_at,
                       u.last_login,
                       COUNT(DISTINCT sc.course_id) as enrolled_courses,
                       COUNT(DISTINCT cp.chapter_id) as completed_chapters,
                       COUNT(DISTINCT ts.submission_id) as test_count,
                       COALESCE(AVG(ts.score), 0) as avg_score
                FROM Users u
                LEFT JOIN Student_Course sc ON u.user_id = sc.student_id
                LEFT JOIN Course_Progress cp ON u.user_id = cp.student_id
                LEFT JOIN Test_Submissions ts ON u.user_id = ts.student_id
                WHERE u.user_id = %s
                GROUP BY u.username, u.role, u.created_at,
                         u.last_login
            """
            result = Database.execute_query(query, (user_id,))
            
            if result:
                user = result[0]
                username, role, created_at, last_login, \
                enrolled_courses, completed_chapters, test_count, avg_score = user
                
                role_map = {
                    'admin': '管理员',
                    'teacher': '教师',
                    'student': '学生'
                }
                
                # 创建详情对话框
                dialog = QDialog(self)
                dialog.setWindowTitle('用户详情')
                dialog.setFixedSize(800, 600)
                
                # 创建布局
                layout = QVBoxLayout()
                layout.setSpacing(20)
                layout.setContentsMargins(40, 40, 40, 40)
                dialog.setLayout(layout)
                
                # 用户基本信息区域
                basic_info_group = QGroupBox("基本信息")
                basic_info_layout = QGridLayout()
                basic_info_group.setLayout(basic_info_layout)
                basic_info_group.setStyleSheet("""
                    QGroupBox {
                        font-size: 16px;
                        font-weight: bold;
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        margin-top: 16px;
                        padding-top: 16px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 20px;
                        padding: 0 5px;
                        color: #2196F3;
                    }
                    QLabel {
                        font-size: 14px;
                        padding: 8px;
                    }
                """)
                
                # 添加基本信息
                labels = [
                    ('用户名：', username),
                    ('角色：', role_map.get(role, role)),
                    ('注册时间：', created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else '未记录'),
                    ('最后登录：', last_login.strftime('%Y-%m-%d %H:%M:%S') if last_login else '从未登录')
                ]
                
                for i, (label, value) in enumerate(labels):
                    label_widget = QLabel(label)
                    value_widget = QLabel(str(value))
                    value_widget.setStyleSheet("color: #333333;")
                    basic_info_layout.addWidget(label_widget, i, 0)
                    basic_info_layout.addWidget(value_widget, i, 1)
                
                layout.addWidget(basic_info_group)
                
                # 如果是学生，添加学习统计信息
                if role == 'student':
                    stats_group = QGroupBox("学习统计")
                    stats_layout = QGridLayout()
                    stats_group.setLayout(stats_layout)
                    stats_group.setStyleSheet("""
                        QGroupBox {
                            font-size: 16px;
                            font-weight: bold;
                            border: 2px solid #e0e0e0;
                            border-radius: 8px;
                            margin-top: 16px;
                            padding-top: 16px;
                        }
                        QGroupBox::title {
                            subcontrol-origin: margin;
                            left: 20px;
                            padding: 0 5px;
                            color: #2196F3;
                        }
                        QLabel {
                            font-size: 14px;
                            padding: 8px;
                        }
                    """)
                    
                    stats = [
                        ('选课数量：', str(int(enrolled_courses or 0))),
                        ('已完成章节：', str(int(completed_chapters or 0))),
                        ('测试次数：', str(int(test_count or 0))),
                        ('平均分数：', f"{float(avg_score or 0):.1f}")
                    ]
                    
                    for i, (label, value) in enumerate(stats):
                        label_widget = QLabel(label)
                        value_widget = QLabel(value)
                        value_widget.setStyleSheet("color: #333333;")
                        stats_layout.addWidget(label_widget, i, 0)
                        stats_layout.addWidget(value_widget, i, 1)
                    
                    layout.addWidget(stats_group)
                
                # 如果是教师，添加教学统计信息
                elif role == 'teacher':
                    # 获取教师课程信息
                    query = """
                        SELECT COUNT(DISTINCT c.course_id) as course_count,
                               COUNT(DISTINCT ch.chapter_id) as chapter_count,
                               COUNT(DISTINCT sc.student_id) as student_count
                        FROM Courses c
                        LEFT JOIN Course_Chapters ch ON c.course_id = ch.course_id
                        LEFT JOIN Student_Course sc ON c.course_id = sc.course_id
                        WHERE c.instructor_id = %s
                    """
                    teacher_stats = Database.execute_query(query, (user_id,))
                    
                    if teacher_stats:
                        course_count, chapter_count, student_count = teacher_stats[0]
                        
                        teaching_group = QGroupBox("教学统计")
                        teaching_layout = QGridLayout()
                        teaching_group.setLayout(teaching_layout)
                        teaching_group.setStyleSheet("""
                            QGroupBox {
                                font-size: 16px;
                                font-weight: bold;
                                border: 2px solid #e0e0e0;
                                border-radius: 8px;
                                margin-top: 16px;
                                padding-top: 16px;
                            }
                            QGroupBox::title {
                                subcontrol-origin: margin;
                                left: 20px;
                                padding: 0 5px;
                                color: #2196F3;
                            }
                            QLabel {
                                font-size: 14px;
                                padding: 8px;
                            }
                        """)
                        
                        stats = [
                            ('课程数量：', str(int(course_count or 0))),
                            ('章节数量：', str(int(chapter_count or 0))),
                            ('学生数量：', str(int(student_count or 0)))
                        ]
                        
                        for i, (label, value) in enumerate(stats):
                            label_widget = QLabel(label)
                            value_widget = QLabel(value)
                            value_widget.setStyleSheet("color: #333333;")
                            teaching_layout.addWidget(label_widget, i, 0)
                            teaching_layout.addWidget(value_widget, i, 1)
                        
                        layout.addWidget(teaching_group)
                
                # 添加关闭按钮
                close_btn = QPushButton('关闭')
                close_btn.setFixedSize(120, 40)
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                close_btn.clicked.connect(dialog.close)
                
                btn_layout = QHBoxLayout()
                btn_layout.addStretch()
                btn_layout.addWidget(close_btn)
                layout.addLayout(btn_layout)
                
                dialog.exec_()
            else:
                QMessageBox.warning(self, '错误', '未找到用户信息')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'获取用户详情失败：{str(e)}') 