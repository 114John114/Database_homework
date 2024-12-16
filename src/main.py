import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
from database import Database
from styles import MODERN_STYLE

def main():
    try:
        # 初始化数据库连接
        Database.initialize()
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 应用现代化样式
        app.setStyleSheet(MODERN_STYLE)
        
        # 显示登录窗口
        login_window = LoginWindow()
        login_window.show()
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程序启动失败: {e}") 

if __name__ == '__main__':
    main() 