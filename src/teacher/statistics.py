from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from database import Database
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'SimSun', 'Arial Unicode MS']  # 按优先级尝试字体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class StatisticsPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        # 设置matplotlib的字体
        matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'SimSun']
        matplotlib.rcParams['font.size'] = 10
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 顶部控制区
        control_layout = QHBoxLayout()
        
        # 课程选择
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.update_statistics)
        control_layout.addWidget(QLabel('选择课程:'))
        control_layout.addWidget(self.course_combo)
        
        # 统计类型选择
        self.stat_type_combo = QComboBox()
        self.stat_type_combo.addItems(['成绩分布', '学习时间', '测试用时'])
        self.stat_type_combo.currentIndexChanged.connect(self.update_statistics)
        control_layout.addWidget(QLabel('统计类型:'))
        control_layout.addWidget(self.stat_type_combo)
        
        layout.addLayout(control_layout)
        
        # 图表区域
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # 加载课程列表
        self.load_courses()
        
    def load_courses(self):
        try:
            query = """
                SELECT course_id, title
                FROM Courses
                WHERE instructor_id = %s AND status = 'active'
                ORDER BY title
            """
            courses = Database.execute_query(query, (self.user_id,))
            
            self.course_combo.clear()
            for course_id, title in courses:
                self.course_combo.addItem(title, course_id)
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载课程列表失败：{str(e)}')
            
    def update_statistics(self):
        stat_type = self.stat_type_combo.currentText()
        course_id = self.course_combo.currentData()
        
        if stat_type == '成绩分布':
            self.show_score_distribution(course_id)
        elif stat_type == '学习时间':
            self.show_study_time_statistics(course_id)
        else:
            self.show_test_time_statistics(course_id)
            
    def show_score_distribution(self, course_id):
        try:
            # 获取所有测试成绩
            query = """
                SELECT ts.score
                FROM Test_Submissions ts
                JOIN Course_Chapters ch ON ts.chapter_id = ch.chapter_id
                WHERE ch.course_id = %s
                AND ts.status = 'graded'
            """
            results = Database.execute_query(query, (course_id,))
            
            if not results:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, '暂无成绩数据', 
                       horizontalalignment='center',
                       verticalalignment='center')
                self.canvas.draw()
                return
            
            scores = [r[0] for r in results]
            
            # 清除旧图
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # 设置分数区间
            bins = [0, 60, 70, 80, 90, 100]
            labels = ['不及格', '及格', '良好', '优秀', '满分']
            
            # 统计各分数段的人数
            hist, _ = np.histogram(scores, bins=bins)
            
            # 绘制柱状图
            bars = ax.bar(range(len(hist)), hist)
            
            # 设置标签
            ax.set_xticks(range(len(hist)))
            ax.set_xticklabels(labels)
            
            # 在柱子上显示具体数值
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}人',
                       ha='center', va='bottom')
            
            # 设置标题和标签
            ax.set_title('成绩分布')
            ax.set_xlabel('分数段')
            ax.set_ylabel('人数')
            
            # 添加及格率信息
            pass_count = sum(1 for s in scores if s >= 60)
            pass_rate = pass_count / len(scores) * 100
            ax.text(0.95, 0.95, f'及格率: {pass_rate:.1f}%',
                   transform=ax.transAxes,
                   horizontalalignment='right',
                   verticalalignment='top',
                   bbox=dict(facecolor='white', alpha=0.8))
            
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'生成成绩分布统计失败：{str(e)}')
    
    def show_study_time_statistics(self, course_id):
        try:
            query = """
                SELECT u.username, 
                       COUNT(DISTINCT cp.chapter_id) as completed_chapters,
                       COUNT(DISTINCT ch.chapter_id) as total_chapters
                FROM Student_Course sc
                JOIN Users u ON sc.student_id = u.user_id
                JOIN Course_Chapters ch ON sc.course_id = ch.course_id
                LEFT JOIN Course_Progress cp ON sc.student_id = cp.student_id 
                    AND ch.chapter_id = cp.chapter_id
                    AND cp.status = 'completed'
                WHERE sc.course_id = %s
                GROUP BY u.username
                ORDER BY completed_chapters DESC
            """
            results = Database.execute_query(query, (course_id,))
            
            if not results:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, '暂无学习数据', 
                       horizontalalignment='center',
                       verticalalignment='center')
                self.canvas.draw()
                return
            
            # 清除旧图
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            names = [r[0] for r in results]
            completed = [r[1] for r in results]
            total = [r[2] for r in results]
            
            x = range(len(names))
            width = 0.35
            
            # 绘制已完成和总章节数的对比柱状图
            bars1 = ax.bar([i - width/2 for i in x], completed, width, 
                          label='已完成章节')
            bars2 = ax.bar([i + width/2 for i in x], total, width,
                          label='总章节数')
            
            # 设置标签
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45)
            
            # 在柱子上显示具体数值
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom')
            
            # 设置标题和标签
            ax.set_title('学习进度统计')
            ax.set_xlabel('学生')
            ax.set_ylabel('章节数')
            ax.legend()
            
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'生成学习时间统计失败：{str(e)}')
    
    def show_test_time_statistics(self, course_id):
        try:
            query = """
                SELECT ch.title,
                       COUNT(ts.submission_id) as submission_count,
                       AVG(ts.score) as avg_score
                FROM Course_Chapters ch
                LEFT JOIN Test_Submissions ts ON ch.chapter_id = ts.chapter_id
                WHERE ch.course_id = %s
                GROUP BY ch.title, ch.sequence_number
                ORDER BY ch.sequence_number
            """
            results = Database.execute_query(query, (course_id,))
            
            if not results:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, '暂无测试数据', 
                       horizontalalignment='center',
                       verticalalignment='center')
                self.canvas.draw()
                return
            
            # 清除旧图
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            chapters = [r[0] for r in results]
            submissions = [r[1] for r in results]
            scores = [r[2] if r[2] is not None else 0 for r in results]
            
            x = range(len(chapters))
            width = 0.35
            
            # 绘制提交次数和平均分的对比柱状图
            ax1 = ax
            ax2 = ax1.twinx()
            
            bars1 = ax1.bar([i - width/2 for i in x], submissions, width,
                           color='skyblue', label='提交次数')
            bars2 = ax2.bar([i + width/2 for i in x], scores, width,
                           color='lightgreen', label='平均分')
            
            # 设置标签
            ax1.set_xticks(x)
            ax1.set_xticklabels(chapters, rotation=45)
            
            # 在柱子上显示具体数值
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}' if isinstance(height, int) 
                            else f'{height:.1f}',
                            ha='center', va='bottom')
            
            # 设置标题和标签
            ax1.set_title('章节测试统计')
            ax1.set_xlabel('章节')
            ax1.set_ylabel('提交次数')
            ax2.set_ylabel('平均分')
            
            # 合并图例
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
            
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'生成测试统计失败：{str(e)}')