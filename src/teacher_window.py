from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QTabWidget, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from teacher.course_management import CourseManagementPage
from teacher.student_progress import StudentProgressPage
from teacher.test_management import TestManagementPage
from teacher.forum_management import ForumManagementPage
from teacher.statistics import StatisticsPage

class TeacherWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('教师界面')
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 添加刷新按钮
        refresh_btn = QPushButton('刷新')
        refresh_btn.setFixedSize(100, 35)
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.refresh_current_page)
        toolbar.addWidget(refresh_btn)
        
        # 添加弹性空间
        toolbar.addStretch()
        
        # 添加欢迎信息
        welcome_label = QLabel('欢迎使用教师管理系统')
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        toolbar.addWidget(welcome_label)
        
        # 添加退出登录按钮
        logout_btn = QPushButton('退出登录')
        logout_btn.setFixedSize(100, 35)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        toolbar.addWidget(logout_btn)
        
        layout.addLayout(toolbar)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            QTabBar::tab {
                background: #f5f5f5;
                border: 1px solid #ddd;
                padding: 10px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #e0e0e0;
            }
        """)
        
        # 添加各个功能页面
        self.course_page = CourseManagementPage(self.user_id)
        self.progress_page = StudentProgressPage(self.user_id)
        self.test_page = TestManagementPage(self.user_id)
        self.forum_page = ForumManagementPage(self.user_id)
        self.statistics_page = StatisticsPage(self.user_id)
        
        self.tab_widget.addTab(self.course_page, '课程管理')
        self.tab_widget.addTab(self.progress_page, '学习进度')
        self.tab_widget.addTab(self.test_page, '测试管理')
        self.tab_widget.addTab(self.forum_page, '讨论管理')
        self.tab_widget.addTab(self.statistics_page, '统计分析')
        
        layout.addWidget(self.tab_widget)
        
    def refresh_current_page(self):
        try:
            # 获取当前页面
            current_index = self.tab_widget.currentIndex()
            current_page = self.tab_widget.widget(current_index)
            
            # 调用页面的刷新方法
            if hasattr(current_page, 'load_courses'):
                current_page.load_courses()
            if hasattr(current_page, 'load_progress'):
                current_page.load_progress()
            if hasattr(current_page, 'load_tests'):
                current_page.load_tests()
            if hasattr(current_page, 'load_posts'):
                current_page.load_posts()
            if hasattr(current_page, 'load_statistics'):
                current_page.load_statistics()
                
            QMessageBox.information(self, '成功', '页面已刷新')
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'刷新失败：{str(e)}')
            
    def logout(self):
        try:
            # 动态导入以避免循环导入
            from login_window import LoginWindow
            # 创建并显示登录窗口
            self.login_window = LoginWindow()
            self.login_window.show()
            # 关闭当前窗口
            self.close()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'退出登录失败：{str(e)}')