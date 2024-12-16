from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from database import Database
import hashlib

class RegisterWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('学习星球 - 用户注册')
        self.setFixedSize(900, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 60)
        central_widget.setLayout(layout)
        
        # 添加标题标签
        title_label = QLabel('用户注册')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(160)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #2196F3;
                margin: 60px 60px;
                padding: 20px 20px;
                background-color: #f5f5f5;
                border-radius: 20px;
                border: 2px solid #e0e0e0;
                min-height: 120px;
                line-height: 80px;
            }
        """)
        layout.addSpacing(40)
        layout.addWidget(title_label)
        layout.addSpacing(40)
        
        # 创建表单布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # 用户名输入
        username_label = QLabel('用户名:')
        username_label.setStyleSheet('font-size: 24px;')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名（至少4个字符）')
        self.username_input.setMinimumWidth(600)
        self.username_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                min-height: 50px;
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
        self.password_input.setPlaceholderText('请输入密码（至少6个字符）')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                min-height: 50px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # 确认密码输入
        confirm_password_label = QLabel('确认密码:')
        confirm_password_label.setStyleSheet('font-size: 24px;')
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('请再次输入密码')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                min-height: 50px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        form_layout.addWidget(confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)
        
        # 用户角色选择
        role_label = QLabel('选择角色:')
        role_label.setStyleSheet('font-size: 24px;')
        self.role_combo = QComboBox()
        self.role_combo.addItems(['student', 'teacher'])
        self.role_combo.setStyleSheet("""
            QComboBox {
                font-size: 24px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                min-height: 50px;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
        """)
        form_layout.addWidget(role_label)
        form_layout.addWidget(self.role_combo)
        
        layout.addLayout(form_layout)
        
        # 添加一些空间
        layout.addSpacing(40)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        
        # 注册按钮
        register_button = QPushButton('注册')
        register_button.setFixedSize(240, 80)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        register_button.clicked.connect(self.handle_register)
        button_layout.addWidget(register_button)
        
        # 返回按钮
        back_button = QPushButton('返回登录')
        back_button.setFixedSize(240, 80)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #666;
                border: 4px solid #ddd;
                border-radius: 10px;
                font-size: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        back_button.clicked.connect(self.close)
        button_layout.addWidget(back_button)
        
        layout.addLayout(button_layout)
        
        # 添加一些空间
        layout.addStretch()
        
        # 版权信息
        copyright_label = QLabel('© 2024 学习星球 版权所有')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet('color: #666; margin: 20px 0; font-size: 20px;')
        layout.addWidget(copyright_label)

    def handle_register(self):
        try:
            username = self.username_input.text()
            password = self.password_input.text()
            confirm_password = self.confirm_password_input.text()
            role = self.role_combo.currentText()
            
            # 输入验证
            if not username or not password or not confirm_password:
                QMessageBox.warning(self, '错误', '所有字段都必须填写')
                return
                
            if password != confirm_password:
                QMessageBox.warning(self, '错误', '两次输入的密码不一致')
                return
                
            if len(password) < 6:
                QMessageBox.warning(self, '错误', '密码长度必须至少为6个字符')
                return
            
            # 检查用户名是否已存在
            query = "SELECT user_id FROM Users WHERE username = %s"
            result = Database.execute_query(query, (username,))
            
            if result:
                QMessageBox.warning(self, '错误', f'用户名 {username} 已存在')
                return
            
            # 对密码进行哈希处理
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # 插入新用户
            query = """
                INSERT INTO Users (username, password, role)
                VALUES (%s, %s, %s)
                RETURNING user_id
            """
            result = Database.execute_query(query, (username, hashed_password, role))
            
            if result:
                QMessageBox.information(self, '成功', '注册成功！请返回登录')
                self.close()
            else:
                QMessageBox.warning(self, '错误', '注册失败：数据库未返回用户ID')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'注册失败：\n\n{str(e)}\n\n如果问题持续存在，请联系管理员。') 