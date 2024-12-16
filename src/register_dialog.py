from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QComboBox, QMessageBox,
                           QFrame)
from PyQt5.QtCore import Qt
from database import Database
import hashlib

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('注册')
        self.setFixedSize(600, 450)  # 增加窗口大小
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)  # 增加垂直间距
        layout.setContentsMargins(50, 40, 50, 40)  # 增加边距
        self.setLayout(layout)
        
        # 标题
        title_label = QLabel('用户注册')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName('title')
        layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName('line')
        layout.addWidget(line)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        username_label.setFixedWidth(120)  # 增加标签宽度
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(45)  # 增加输入框高度
        self.username_input.setPlaceholderText('请输入用户名')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        password_label.setFixedWidth(120)
        self.password_input = QLineEdit()
        self.password_input.setFixedHeight(45)
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel('确认密码:')
        confirm_label.setFixedWidth(120)
        self.confirm_input = QLineEdit()
        self.confirm_input.setFixedHeight(45)
        self.confirm_input.setPlaceholderText('请再次输入密码')
        self.confirm_input.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # 角色选择
        role_layout = QHBoxLayout()
        role_label = QLabel('角色:')
        role_label.setFixedWidth(120)
        self.role_combo = QComboBox()
        self.role_combo.setFixedHeight(45)
        self.role_combo.addItems(['学生', '教师'])
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # 添加一个弹性空间
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # 增加按钮间距
        register_btn = QPushButton('注册')
        register_btn.setObjectName('register-btn')
        register_btn.setFixedSize(180, 50)  # 增加按钮大小
        register_btn.clicked.connect(self.register)
        cancel_btn = QPushButton('取消')
        cancel_btn.setObjectName('cancel-btn')
        cancel_btn.setFixedSize(180, 50)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(register_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
    def setup_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 18px;
                color: #333;
            }
            #title {
                font-size: 32px;
                font-weight: bold;
                color: #2196F3;
                margin: 10px 0;
            }
            #line {
                color: #ddd;
                margin: 10px 0;
            }
            QLineEdit {
                padding: 8px 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QComboBox {
                padding: 8px 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                font-size: 16px;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 10px;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            #register-btn {
                background-color: #2196F3;
                color: white;
            }
            #register-btn:hover {
                background-color: #1976D2;
            }
            #cancel-btn {
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                color: #666;
            }
            #cancel-btn:hover {
                background-color: #e0e0e0;
            }
        """)
        
    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        role = 'student' if self.role_combo.currentText() == '学生' else 'teacher'
        
        # 验证输入
        if not username:
            QMessageBox.warning(self, '错误', '请输入用户名')
            return
            
        if not password:
            QMessageBox.warning(self, '错误', '请输入密码')
            return
            
        if password != confirm:
            QMessageBox.warning(self, '错误', '两次输入的密码不一致')
            return
            
        try:
            # 检查用户名是否已存在
            query = """
                SELECT user_id FROM Users WHERE username = %s
            """
            result = Database.execute_query(query, (username,))
            
            if result:
                QMessageBox.warning(self, '错误', '用户名已存在')
                return
            
            # 对密码进行SHA256��密
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # 插入新用户
            query = """
                INSERT INTO Users (username, password, role)
                VALUES (%s, %s, %s)
            """
            Database.execute_query(query, (username, password_hash, role))
            
            QMessageBox.information(self, '成功', '注册成功！')
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'注册失败：{str(e)}') 