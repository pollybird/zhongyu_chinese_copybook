from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("钟毓汉字字帖生成器")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 版本
        version_label = QLabel("版本：1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 描述
        desc_label = QLabel("钟毓汉字字帖生成器是一款专业的汉字书写练习工具，专注于生成标准的汉字字帖，帮助学生和汉字学习者提高书写水平。")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 功能特点
        features_label = QLabel("功能特点：\n- 多种线格类型：米字格、田字格、回宫格、作文纸\n- 多种生成模式：描红、抄写、描红+抄写、纯字帖\n- 丰富的自定义选项\n- PDF导出功能\n- 分页预览\n- 多文件标签功能")
        features_label.setWordWrap(True)
        layout.addWidget(features_label)
        
        # 作者信息
        author_label = QLabel("作者：泰州姜堰钟毓信息技术有限公司")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)
        
        # 许可证
        license_label = QLabel("许可证：Apache 2.0")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)