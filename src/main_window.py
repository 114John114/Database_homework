from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt
from database import Database

class MainWindow(QMainWindow):
    def __init__(self, user_id, username, role):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.role = role
        
        # 设置窗口标题和大小
        self.setWindowTitle(f'在线教育系统 - {username}')
        self.setMinimumSize(1200, 800)  # 设置最小窗口大小
        
        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 创建左侧边栏
        sidebar = QWidget()
        sidebar.setMinimumWidth(200)  # 设置侧边栏最小宽度
        sidebar.setMaximumWidth(250)  # 设置侧边栏最大宽度
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        
        # 添加用户信息区域
        user_info = QLabel(f'用户名: {username}\n角色: {role}')
        user_info.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f0f0f0;
                border-radius: 5px;
                margin-bottom: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        sidebar_layout.addWidget(user_info)
        
        # 创建按钮
        self.create_sidebar_buttons(sidebar_layout)
        
        # 添加底部空白区域
        sidebar_layout.addStretch()
        
        # 添加退出按钮
        logout_btn = QPushButton('🚪 退出登录')
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)
        
        # 设置侧边栏样式
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-right: 1px solid #cccccc;
            }
            QPushButton {
                text-align: left;
                padding: 12px;
                border: none;
                border-radius: 5px;
                margin: 2px 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # 添加侧边栏到主布局
        main_layout.addWidget(sidebar)
        
        # 创建内容区域
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        main_layout.addWidget(self.content_stack)
        
        # 设置布局比例
        main_layout.setStretch(0, 1)  # 侧边栏占比
        main_layout.setStretch(1, 4)  # 内容区域占比
        
        # 初始化页面
        self.initialize_pages()
    
    def handle_logout(self):
        reply = QMessageBox.question(self, '确认', '确定要退出登录吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # 更新最后登录时间
                query = """
                    UPDATE Users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE user_id = %s
                """
                Database.execute_query(query, (self.user_id,))
                
                # 关闭当前窗口
                self.close()
                
                # 显示登录窗口
                from login_window import LoginWindow
                self.login_window = LoginWindow()
                self.login_window.show()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'退出登录失败：{str(e)}')
        
    def create_sidebar_buttons(self, layout):
        # 由子类实现
        pass
        
    def initialize_pages(self):
        # 由子类实现
        pass