MODERN_STYLE = """
/* 全局样式 */
QWidget {
    font-family: "Microsoft YaHei", "SimHei";
    font-size: 12px;
}

/* 主窗口样式 */
QMainWindow {
    background-color: #f5f5f5;
}

/* 按钮样式 */
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

/* 危险操作按钮 */
QPushButton[danger="true"] {
    background-color: #f44336;
}

QPushButton[danger="true"]:hover {
    background-color: #d32f2f;
}

/* 成功操作按钮 */
QPushButton[success="true"] {
    background-color: #4CAF50;
}

QPushButton[success="true"]:hover {
    background-color: #388E3C;
}

/* 表格样式 */
QTableWidget {
    background-color: white;
    alternate-background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    gridline-color: #e0e0e0;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #e3f2fd;
    color: #1976D2;
}

QHeaderView::section {
    background-color: #f5f5f5;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e0e0e0;
    font-weight: bold;
}

/* 下拉框样式 */
QComboBox {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
    min-width: 120px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(resources/down-arrow.png);
    width: 12px;
    height: 12px;
}

/* 标签样式 */
QLabel {
    color: #333333;
}

QLabel[heading="true"] {
    font-size: 18px;
    font-weight: bold;
    color: #1976D2;
    padding: 10px 0;
}

/* 文本框样式 */
QLineEdit, QTextEdit {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #2196F3;
}

/* 单选框样式 */
QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #757575;
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

/* 进度条样式 */
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #e0e0e0;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 4px;
}

/* 滚动条样式 */
QScrollBar:vertical {
    border: none;
    background-color: #f5f5f5;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #bdbdbd;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #757575;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f5f5f5;
    height: 10px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #bdbdbd;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #757575;
}

/* 对话框样式 */
QDialog {
    background-color: white;
}

/* 消息框样式 */
QMessageBox {
    background-color: white;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 6px 14px;
}

/* 工具提示样式 */
QToolTip {
    background-color: #424242;
    color: white;
    border: none;
    padding: 5px;
    border-radius: 3px;
}
""" 