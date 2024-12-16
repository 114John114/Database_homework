from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QTabWidget, QPushButton, QMessageBox)
from manager.user_management import UserManagementPage
from manager.course_management import CourseManagementPage
from manager.statistics import StatisticsPage
from manager.forum_management import ForumManagementPage

class ManagerWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('管理员系统')
        self.setMinimumSize(1800, 600)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建顶部工具栏
        toolbar = QHBoxLayout()
        
        # 添加标题
        title_label = QWidget()
        title_label.setFixedWidth(800)
        toolbar.addWidget(title_label)
        
        # 添加登出按钮
        logout_btn = QPushButton('退出登录')
        logout_btn.setFixedWidth(100)
        logout_btn.clicked.connect(self.logout)
        toolbar.addWidget(logout_btn)
        
        layout.addLayout(toolbar)
        
        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin: 2px;
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #e3f2fd;
            }
        """)
        
        # 添加各个功能页面
        tab_widget.addTab(UserManagementPage(self.user_id), '用户管理')
        tab_widget.addTab(CourseManagementPage(self.user_id), '课程管理')
        tab_widget.addTab(StatisticsPage(self.user_id), '统计信息')
        tab_widget.addTab(ForumManagementPage(self.user_id), '讨论区管理')
        
        layout.addWidget(tab_widget)
        
    def logout(self):
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出登录吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 导入登录窗口类
            from login_window import LoginWindow
            # 关闭当前窗口
            self.close()
            # 打开登录窗口
            self.login_window = LoginWindow()
            self.login_window.show() 