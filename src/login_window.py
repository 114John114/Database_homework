from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from database import Database
import hashlib
from student_window import StudentWindow
from teacher_window import TeacherWindow
from manager_window import ManagerWindow
from register_dialog import RegisterDialog

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('学习星球')
        self.setFixedSize(1200, 1500)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(100, 100, 100, 100)
        central_widget.setLayout(layout)
        
        # 标题
        title_label = QLabel('学习星球')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 72px;
                font-weight: bold;
                color: #2196F3;
                margin: 60px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 创建表单布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(30)
        
        # 用户名输入
        username_label = QLabel('用户名:')
        username_label.setStyleSheet('font-size: 24px;')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        self.username_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                min-height: 60px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # 密码输入
        password_label = QLabel('密码:')
        password_label.setStyleSheet('font-size: 24px;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                min-height: 60px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        layout.addLayout(form_layout)
        
        # 添加一些空间
        layout.addSpacing(60)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(50)
        
        # 登录按钮
        login_btn = QPushButton('登录')
        login_btn.setFixedSize(360, 120)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 48px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        login_btn.clicked.connect(self.login)
        button_layout.addWidget(login_btn)
        
        # 注册按钮
        register_btn = QPushButton('注册')
        register_btn.setFixedSize(360, 120)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #666;
                border: 6px solid #ddd;
                border-radius: 12px;
                font-size: 48px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        register_btn.clicked.connect(self.show_register_dialog)
        button_layout.addWidget(register_btn)
        
        layout.addLayout(button_layout)
        
        # 添加一些空间
        layout.addStretch()
        
        # 版权信息
        copyright_label = QLabel('© 2024 学习星球 版权所有')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {
                color: #666;
                margin: 60px 0;
                font-size: 24px;
            }
        """)
        layout.addWidget(copyright_label)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, '错误', '请输入用户名和密码')
            return
            
        try:
            # 对密码进行SHA256加密
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # 查询用户
            query = """
                SELECT user_id, username, role
                FROM Users
                WHERE username = %s AND password = %s
            """
            result = Database.execute_query(query, (username, password_hash))
            
            if not result:
                QMessageBox.warning(self, '错误', '用户名或密码错误')
                return
                
            user_id, username, role = result[0]
            
            # 更新最后登录时间
            update_query = """
                UPDATE Users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE user_id = %s
            """
            Database.execute_query(update_query, (user_id,))
            
            # 根据角色打开相应的窗口
            if role == 'student':
                self.window = StudentWindow(user_id, username, role)
            elif role == 'teacher':
                self.window = TeacherWindow(user_id)
            elif role == 'admin':
                self.window = ManagerWindow(user_id)
            else:
                QMessageBox.warning(self, '错误', '未知的用户角色')
                return
            
            self.window.show()
            self.close()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'登录失败：{str(e)}')
    
    def show_register_dialog(self):
        dialog = RegisterDialog()
        dialog.exec_() 