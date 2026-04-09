import sys
import os
import pickle
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
    QTabWidget, QFileDialog, QMessageBox, QSplitter, QGroupBox,
    QCheckBox, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QFontDatabase, QIcon

from renderers import GridRenderer
from utils import calculate_pages
from dialogs import AboutDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("钟毓汉字字帖生成器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置程序图标
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)  # 启用标签关闭按钮
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # 连接关闭信号
        self.setCentralWidget(self.tab_widget)
        
        # 新建标签页
        self.new_tab()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 程序打开时默认最大化
        self.showMaximized()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 新建
        new_action = file_menu.addAction("新建(&N)")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_tab)
        
        # 打开
        open_action = file_menu.addAction("打开(&O)")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        
        # 保存
        save_action = file_menu.addAction("保存(&S)")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        
        # 另存为
        save_as_action = file_menu.addAction("另存为(&A)")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        
        file_menu.addSeparator()
        
        # 导出PDF
        export_action = file_menu.addAction("导出PDF(&E)")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_pdf)
        
        file_menu.addSeparator()
        
        # 关闭
        exit_action = file_menu.addAction("关闭(&C)")
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        # 剪切
        cut_action = edit_menu.addAction("剪切(&T)")
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut_text)
        
        # 复制
        copy_action = edit_menu.addAction("复制(&C)")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_text)
        
        # 粘贴
        paste_action = edit_menu.addAction("粘贴(&P)")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_text)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 帮助
        help_action = help_menu.addAction("帮助(&H)")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        
        # 关于
        about_action = help_menu.addAction("关于(&A)")
        about_action.triggered.connect(self.show_about)
    
    def new_tab(self):
        # 计算新标签页标题
        untitled_count = 0
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i).startswith("Untitled"):
                untitled_count += 1
        
        if untitled_count == 0:
            tab_title = "Untitled"
        else:
            tab_title = f"Untitled{untitled_count}"
        
        # 创建新标签页
        tab = QWidget()
        tab_layout = QVBoxLayout()
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧控制面板
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # 输入内容
        input_group = QGroupBox("输入内容")
        input_layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("请输入要生成字帖的汉字...")
        input_layout.addWidget(text_edit)
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        # 调整设置
        settings_group = QGroupBox("调整设置")
        settings_layout = QGridLayout()
        
        # 字体选择
        settings_layout.addWidget(QLabel("字体:"), 0, 0)
        font_combo = QComboBox()
        
        # 优先加载font/目录下的字体
        font_dir = os.path.join(os.path.dirname(__file__), "font")
        font_families = []
        
        if os.path.exists(font_dir):
            for file_name in os.listdir(font_dir):
                if file_name.endswith(".ttf") or file_name.endswith(".otf"):
                    font_path = os.path.join(font_dir, file_name)
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        font_families.extend(QFontDatabase.applicationFontFamilies(font_id))
        
        # 加载系统字体
        system_fonts = QFontDatabase.families()
        # 去重
        font_families = list(set(font_families))
        # 按字母顺序排序
        font_families.sort()
        # 添加系统字体（排除已添加的）
        for font in system_fonts:
            if font not in font_families:
                font_families.append(font)
        
        # 添加到下拉菜单
        font_combo.addItems(font_families)
        
        # 默认选择
        default_font = "楷体"
        if os.path.exists(font_dir) and "方正硬笔楷书简体" in font_families:
            default_font = "方正硬笔楷书简体"
        elif "楷体" in font_families:
            default_font = "楷体"
        elif "KaiTi" in font_families:
            default_font = "KaiTi"
        
        font_combo.setCurrentText(default_font)
        settings_layout.addWidget(font_combo, 0, 1)
        
        # 字体大小
        settings_layout.addWidget(QLabel("字体大小:"), 0, 2)
        font_size_spin = QSpinBox()
        font_size_spin.setRange(10, 100)
        font_size_spin.setValue(24)
        settings_layout.addWidget(font_size_spin, 0, 3)
        
        # 位置偏移
        settings_layout.addWidget(QLabel("位置偏移 X:"), 1, 0)
        offset_x_spin = QSpinBox()
        offset_x_spin.setRange(-50, 50)
        offset_x_spin.setValue(0)
        settings_layout.addWidget(offset_x_spin, 1, 1)
        
        settings_layout.addWidget(QLabel("位置偏移 Y:"), 1, 2)
        offset_y_spin = QSpinBox()
        offset_y_spin.setRange(-50, 50)
        offset_y_spin.setValue(0)
        settings_layout.addWidget(offset_y_spin, 1, 3)
        
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)
        
        # 线格类型
        grid_group = QGroupBox("线格类型")
        grid_layout = QVBoxLayout()
        grid_combo = QComboBox()
        grid_combo.addItems(["米字格", "田字格", "回宫格", "作文纸"])
        grid_layout.addWidget(grid_combo)
        grid_group.setLayout(grid_layout)
        left_layout.addWidget(grid_group)
        
        # 生成模式
        mode_group = QGroupBox("生成模式")
        mode_layout = QVBoxLayout()
        mode_combo = QComboBox()
        mode_combo.addItems(["描红", "抄写", "描红+抄写", "纯字帖"])
        mode_layout.addWidget(mode_combo)
        mode_group.setLayout(mode_layout)
        left_layout.addWidget(mode_group)
        
        # 标题设置
        title_group = QGroupBox("标题设置")
        title_layout = QVBoxLayout()
        title_edit = QLineEdit()
        title_edit.setText("汉字字帖")
        title_layout.addWidget(title_edit)
        title_group.setLayout(title_layout)
        left_layout.addWidget(title_group)
        
        # 自定义头部
        header_group = QGroupBox("自定义头部")
        header_layout = QVBoxLayout()
        
        # 字段1
        field1_layout = QHBoxLayout()
        field1_layout.addWidget(QLabel("字段1:"))
        field1_edit = QLineEdit()
        field1_edit.setText("班级")
        field1_layout.addWidget(field1_edit)
        header_layout.addLayout(field1_layout)
        
        # 字段2
        field2_layout = QHBoxLayout()
        field2_layout.addWidget(QLabel("字段2:"))
        field2_edit = QLineEdit()
        field2_edit.setText("姓名")
        field2_layout.addWidget(field2_edit)
        header_layout.addLayout(field2_layout)
        
        # 字段3
        field3_layout = QHBoxLayout()
        field3_layout.addWidget(QLabel("字段3:"))
        field3_edit = QLineEdit()
        field3_edit.setText("学号")
        field3_layout.addWidget(field3_edit)
        header_layout.addLayout(field3_layout)
        
        header_group.setLayout(header_layout)
        left_layout.addWidget(header_group)
        
        # 页码设置
        page_number_group = QGroupBox("页码设置")
        page_number_layout = QHBoxLayout()
        
        # 页码格式
        page_format_layout = QHBoxLayout()
        page_format_layout.addWidget(QLabel("页码格式:"))
        page_format_combo = QComboBox()
        page_format_combo.addItems(["不显示", "第1页", "第一页", "第1页 共x页", "第一页 共X页"])
        page_format_layout.addWidget(page_format_combo)
        page_number_layout.addLayout(page_format_layout)
        
        # 页码位置
        page_position_layout = QHBoxLayout()
        page_position_layout.addWidget(QLabel("页码位置:"))
        page_position_combo = QComboBox()
        page_position_combo.addItems(["底部居中", "底部靠左", "底部靠右"])
        page_position_layout.addWidget(page_position_combo)
        page_number_layout.addLayout(page_position_layout)
        
        page_number_group.setLayout(page_number_layout)
        left_layout.addWidget(page_number_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        save_project_button = QPushButton("保存工程")
        save_project_button.clicked.connect(self.save_project)
        button_layout.addWidget(save_project_button)
        
        export_button = QPushButton("导出PDF")
        export_button.clicked.connect(self.export_pdf)
        button_layout.addWidget(export_button)
        
        left_layout.addLayout(button_layout)
        
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)
        
        # 右侧预览面板
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # 预览区域（带滚动条）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        preview_label = QLabel("预览区域")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setMinimumSize(600, 800)
        
        scroll_area.setWidget(preview_label)
        right_layout.addWidget(scroll_area)
        
        # 页码导航
        nav_layout = QHBoxLayout()
        prev_button = QPushButton("上一页")
        prev_button.clicked.connect(self.prev_page)
        nav_layout.addWidget(prev_button)
        
        page_label = QLabel("1 / 1")
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(page_label)
        
        next_button = QPushButton("下一页")
        next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(next_button)
        
        right_layout.addLayout(nav_layout)
        
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
        
        tab_layout.addWidget(splitter)
        tab.setLayout(tab_layout)
        
        # 添加标签页
        tab_index = self.tab_widget.addTab(tab, tab_title)
        self.tab_widget.setCurrentIndex(tab_index)
        
        # 存储标签页数据和控件
        tab.data = {
            "text": "",
            "font_name": "楷体",
            "font_size": 24,
            "line_spacing": 10,
            "offset_x": 0,
            "offset_y": 0,
            "grid_type": "米字格",
            "mode": "描红",
            "title": "汉字字帖",
            "fields": ["班级", "姓名", "学号"],
            "page_format": "不显示",
            "page_position": "底部居中",
            "current_page": 1,
            "total_pages": 1,
            "file_path": None,
            "modified": False
        }
        
        # 存储控件引用
        tab.controls = {
            "text_edit": text_edit,
            "font_combo": font_combo,
            "font_size_spin": font_size_spin,
            "offset_x_spin": offset_x_spin,
            "offset_y_spin": offset_y_spin,
            "grid_combo": grid_combo,
            "mode_combo": mode_combo,
            "title_edit": title_edit,
            "field1_edit": field1_edit,
            "field2_edit": field2_edit,
            "field3_edit": field3_edit,
            "page_format_combo": page_format_combo,
            "page_position_combo": page_position_combo,
            "save_project_button": save_project_button,
            "export_button": export_button,
            "preview_label": preview_label,
            "prev_button": prev_button,
            "page_label": page_label,
            "next_button": next_button
        }
        
        # 连接信号，实现所见即所得
        text_edit.textChanged.connect(self.on_content_changed)
        font_combo.currentTextChanged.connect(self.on_content_changed)
        font_size_spin.valueChanged.connect(self.on_content_changed)
        offset_x_spin.valueChanged.connect(self.on_content_changed)
        offset_y_spin.valueChanged.connect(self.on_content_changed)
        grid_combo.currentTextChanged.connect(self._on_grid_type_changed)
        grid_combo.currentTextChanged.connect(self.on_content_changed)
        mode_combo.currentTextChanged.connect(self.on_content_changed)
        title_edit.textChanged.connect(self.on_content_changed)
        field1_edit.textChanged.connect(self.on_content_changed)
        field2_edit.textChanged.connect(self.on_content_changed)
        field3_edit.textChanged.connect(self.on_content_changed)
        page_format_combo.currentTextChanged.connect(self.on_content_changed)
        page_position_combo.currentTextChanged.connect(self.on_content_changed)
        
        # 程序打开后预览区域默认先显示米字格
        self.preview()
    
    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开工程文件", "", "钟毓汉字字帖工程 (*.zyzcb)"
        )
        
        if file_path:
            try:
                # 读取工程文件（二进制格式）
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                # 确保所有必要的键存在
                default_data = {
                    "text": "",
                    "font_name": "楷体",
                    "font_size": 24,
                    "char_spacing": 10,
                    "line_spacing": 10,
                    "offset_x": 0,
                    "offset_y": 0,
                    "grid_type": "米字格",
                    "mode": "描红",
                    "title": "汉字字帖",
                    "fields": ["班级", "姓名", "学号"],
                    "page_format": "不显示",
                    "page_position": "底部居中",
                    "current_page": 1,
                    "total_pages": 1,
                    "file_path": file_path,
                    "modified": False
                }
                
                # 合并默认数据和读取的数据
                for key, value in default_data.items():
                    if key not in data:
                        data[key] = value
                
                # 更新文件路径
                data["file_path"] = file_path
                data["modified"] = False
                
                # 新建标签页
                self.new_tab()
                current_tab = self.tab_widget.currentWidget()
                
                # 填充数据
                current_tab.data = data
                
                # 更新界面
                controls = current_tab.controls
                
                # 临时断开信号连接，避免触发不必要的更新
                controls["text_edit"].blockSignals(True)
                controls["font_combo"].blockSignals(True)
                controls["font_size_spin"].blockSignals(True)
                controls["offset_x_spin"].blockSignals(True)
                controls["offset_y_spin"].blockSignals(True)
                controls["grid_combo"].blockSignals(True)
                controls["mode_combo"].blockSignals(True)
                controls["title_edit"].blockSignals(True)
                controls["field1_edit"].blockSignals(True)
                controls["field2_edit"].blockSignals(True)
                controls["field3_edit"].blockSignals(True)
                controls["page_format_combo"].blockSignals(True)
                controls["page_position_combo"].blockSignals(True)
                
                try:
                    # 设置文本内容
                    controls["text_edit"].setText(data["text"])
                    
                    # 设置字体
                    font_name = data.get("font_name", "楷体")
                    font_index = controls["font_combo"].findText(font_name)
                    if font_index != -1:
                        controls["font_combo"].setCurrentIndex(font_index)
                    
                    # 设置字体大小
                    controls["font_size_spin"].setValue(data.get("font_size", 24))
                    
                    # 设置位置偏移
                    controls["offset_x_spin"].setValue(data.get("offset_x", 0))
                    controls["offset_y_spin"].setValue(data.get("offset_y", 0))
                    
                    # 设置线格类型
                    grid_type = data.get("grid_type", "米字格")
                    grid_index = controls["grid_combo"].findText(grid_type)
                    if grid_index != -1:
                        controls["grid_combo"].setCurrentIndex(grid_index)
                    
                    # 设置生成模式
                    mode_value = data.get("mode", "描红")
                    mode_index = controls["mode_combo"].findText(mode_value)
                    if mode_index != -1:
                        controls["mode_combo"].setCurrentIndex(mode_index)
                    
                    # 设置标题
                    controls["title_edit"].setText(data.get("title", "汉字字帖"))
                    
                    # 设置自定义头部
                    fields = data.get("fields", ["班级", "姓名", "学号"])
                    if len(fields) > 0:
                        controls["field1_edit"].setText(fields[0])
                    if len(fields) > 1:
                        controls["field2_edit"].setText(fields[1])
                    if len(fields) > 2:
                        controls["field3_edit"].setText(fields[2])
                    
                    # 设置页码格式
                    page_format_value = data.get("page_format", "不显示")
                    page_format_index = controls["page_format_combo"].findText(page_format_value)
                    if page_format_index != -1:
                        controls["page_format_combo"].setCurrentIndex(page_format_index)
                    
                    # 设置页码位置
                    page_position_value = data.get("page_position", "底部居中")
                    page_position_index = controls["page_position_combo"].findText(page_position_value)
                    if page_position_index != -1:
                        controls["page_position_combo"].setCurrentIndex(page_position_index)
                finally:
                    # 恢复信号连接
                    controls["text_edit"].blockSignals(False)
                    controls["font_combo"].blockSignals(False)
                    controls["font_size_spin"].blockSignals(False)
                    controls["offset_x_spin"].blockSignals(False)
                    controls["offset_y_spin"].blockSignals(False)
                    controls["grid_combo"].blockSignals(False)
                    controls["mode_combo"].blockSignals(False)
                    controls["title_edit"].blockSignals(False)
                    controls["field1_edit"].blockSignals(False)
                    controls["field2_edit"].blockSignals(False)
                    controls["field3_edit"].blockSignals(False)
                    controls["page_format_combo"].blockSignals(False)
                    controls["page_position_combo"].blockSignals(False)
                
                # 更新标签标题
                tab_title = os.path.basename(file_path)
                tab_index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(tab_index, tab_title)
                
                # 根据工程文件内容生成预览
                self.preview()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开工程文件失败: {str(e)}")
    
    def save_project(self):
        current_tab = self.tab_widget.currentWidget()
        data = current_tab.data
        
        if data["file_path"]:
            file_path = data["file_path"]
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存工程文件", "", "钟毓汉字字帖工程 (*.zyzcb)"
            )
        
        if file_path:
            try:
                # 收集数据
                controls = current_tab.controls
                data["text"] = controls["text_edit"].toPlainText()
                data["font_name"] = controls["font_combo"].currentText()
                data["font_size"] = controls["font_size_spin"].value()
                # 行间距固定为10，无需用户调整
                data["line_spacing"] = 10
                data["offset_x"] = controls["offset_x_spin"].value()
                data["offset_y"] = controls["offset_y_spin"].value()
                data["grid_type"] = controls["grid_combo"].currentText()
                data["mode"] = controls["mode_combo"].currentText()
                data["title"] = controls["title_edit"].text()
                data["fields"] = [
                    controls["field1_edit"].text(),
                    controls["field2_edit"].text(),
                    controls["field3_edit"].text()
                ]
                data["page_format"] = controls["page_format_combo"].currentText()
                data["page_position"] = controls["page_position_combo"].currentText()
                data["file_path"] = file_path
                data["modified"] = False
                
                # 写入文件（二进制格式）
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
                
                # 更新标签标题（清除*标记）
                tab_title = os.path.basename(file_path)
                tab_index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(tab_index, tab_title)
                
                QMessageBox.information(self, "成功", "工程文件保存成功")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存工程文件失败: {str(e)}")
    
    def save_project_as(self):
        """另存为工程文件"""
        current_tab = self.tab_widget.currentWidget()
        data = current_tab.data
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为工程文件", "", "钟毓汉字字帖工程 (*.zyzcb)"
        )
        
        if file_path:
            try:
                # 收集数据
                controls = current_tab.controls
                data["text"] = controls["text_edit"].toPlainText()
                data["font_name"] = controls["font_combo"].currentText()
                data["font_size"] = controls["font_size_spin"].value()
                data["line_spacing"] = 10
                data["offset_x"] = controls["offset_x_spin"].value()
                data["offset_y"] = controls["offset_y_spin"].value()
                data["grid_type"] = controls["grid_combo"].currentText()
                data["mode"] = controls["mode_combo"].currentText()
                data["title"] = controls["title_edit"].text()
                data["fields"] = [
                    controls["field1_edit"].text(),
                    controls["field2_edit"].text(),
                    controls["field3_edit"].text()
                ]
                data["page_format"] = controls["page_format_combo"].currentText()
                data["page_position"] = controls["page_position_combo"].currentText()
                data["file_path"] = file_path
                data["modified"] = False
                
                # 写入文件（二进制格式）
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
                
                # 更新标签标题（清除*标记）
                tab_title = os.path.basename(file_path)
                tab_index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(tab_index, tab_title)
                
                QMessageBox.information(self, "成功", "工程文件另存为成功")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"工程文件另存为失败: {str(e)}")
    
    def cut_text(self):
        """剪切文本"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            controls = current_tab.controls
            text_edit = controls["text_edit"]
            text_edit.cut()
    
    def copy_text(self):
        """复制文本"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            controls = current_tab.controls
            text_edit = controls["text_edit"]
            text_edit.copy()
    
    def paste_text(self):
        """粘贴文本"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            controls = current_tab.controls
            text_edit = controls["text_edit"]
            text_edit.paste()
    
    def show_help(self):
        """显示帮助"""
        help_text = """
<h2>钟毓汉字字帖生成器 帮助</h2>

<h3>基本操作</h3>
<ul>
<li><b>新建 (Ctrl+N)</b>: 创建新的字帖工程</li>
<li><b>打开 (Ctrl+O)</b>: 打开已有的字帖工程</li>
<li><b>保存 (Ctrl+S)</b>: 保存当前工程</li>
<li><b>另存为 (Ctrl+Shift+S)</b>: 将当前工程另存为新文件</li>
<li><b>导出PDF (Ctrl+E)</b>: 将字帖导出为PDF文件</li>
</ul>

<h3>编辑操作</h3>
<ul>
<li><b>剪切 (Ctrl+X)</b>: 剪切选中的文本</li>
<li><b>复制 (Ctrl+C)</b>: 复制选中的文本</li>
<li><b>粘贴 (Ctrl+V)</b>: 粘贴文本</li>
</ul>

<h3>线格类型</h3>
<ul>
<li><b>米字格</b>: 适合初学者练习汉字结构</li>
<li><b>田字格</b>: 适合练习汉字笔画</li>
<li><b>回宫格</b>: 适合练习汉字比例</li>
<li><b>作文纸</b>: 适合练习作文书写</li>
</ul>

<h3>生成模式</h3>
<ul>
<li><b>描红</b>: 淡红色字体，适合临摹</li>
<li><b>抄写</b>: 黑色字体，每行后留空行</li>
<li><b>描红+抄写</b>: 淡红色字体，每行后留空行</li>
<li><b>纯字帖</b>: 黑色字体，无空行</li>
</ul>

<h3>快捷键</h3>
<ul>
<li><b>F1</b>: 显示帮助</li>
<li><b>Alt+F4</b>: 关闭程序</li>
</ul>
        """
        QMessageBox.information(self, "帮助", help_text)
    
    def export_pdf(self):
        current_tab = self.tab_widget.currentWidget()
        data = current_tab.data
        
        # 收集数据
        controls = current_tab.controls
        data["text"] = controls["text_edit"].toPlainText()
        data["font_name"] = controls["font_combo"].currentText()
        data["font_size"] = controls["font_size_spin"].value()
        # 14点行间距
        data["line_spacing"] = 14
        data["offset_x"] = controls["offset_x_spin"].value()
        data["offset_y"] = controls["offset_y_spin"].value()
        data["grid_type"] = controls["grid_combo"].currentText()
        data["mode"] = controls["mode_combo"].currentText()
        data["title"] = controls["title_edit"].text()
        data["fields"] = [
            controls["field1_edit"].text(),
            controls["field2_edit"].text(),
            controls["field3_edit"].text()
        ]
        data["page_format"] = controls["page_format_combo"].currentText()
        data["page_position"] = controls["page_position_combo"].currentText()
        
        # 检查输入内容
        if not data["text"]:
            QMessageBox.warning(self, "警告", "请输入要生成字帖的汉字")
            return
        
        # 生成默认文件名
        if data["file_path"]:
            default_name = os.path.splitext(os.path.basename(data["file_path"]))[0] + ".pdf"
        else:
            default_name = "字帖.pdf"
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出PDF", default_name, "PDF文件 (*.pdf)"
        )
        
        if file_path:
            try:
                # 计算页数
                data["total_pages"] = calculate_pages(data["text"], data["grid_type"], data["mode"])
                
                # 渲染PDF
                renderer = GridRenderer(data["grid_type"])
                renderer.render_pdf(file_path, data)
                
                QMessageBox.information(self, "成功", "PDF导出成功")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"PDF导出失败: {str(e)}")
    
    def _on_grid_type_changed(self, grid_type):
        """处理线格类型变化时自动调整字体大小"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            controls = current_tab.controls
            if grid_type in ["米字格", "田字格", "回宫格"]:
                controls["font_size_spin"].setValue(24)
            elif grid_type == "作文纸":
                controls["font_size_spin"].setValue(16)  # Smaller font for square grid
    
    def on_content_changed(self):
        """内容或配置发生更改时的处理"""
        self.mark_as_modified()
        self.preview()
    
    def mark_as_modified(self):
        """标记当前标签为已修改，在标题右侧显示*"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            # 检查是否已经标记为修改
            if not current_tab.data.get("modified", False):
                current_tab.data["modified"] = True
                # 更新标签标题，添加*标记
                tab_index = self.tab_widget.currentIndex()
                current_title = self.tab_widget.tabText(tab_index)
                if not current_title.endswith("*"):
                    self.tab_widget.setTabText(tab_index, current_title + "*")
    
    def preview(self):
        current_tab = self.tab_widget.currentWidget()
        data = current_tab.data
        controls = current_tab.controls
        
        # 收集数据
        data["text"] = controls["text_edit"].toPlainText()
        data["font_name"] = controls["font_combo"].currentText()
        data["font_size"] = controls["font_size_spin"].value()
        # 14点行间距
        data["line_spacing"] = 14
        data["offset_x"] = controls["offset_x_spin"].value()
        data["offset_y"] = controls["offset_y_spin"].value()
        data["grid_type"] = controls["grid_combo"].currentText()
        data["mode"] = controls["mode_combo"].currentText()
        data["title"] = controls["title_edit"].text()
        data["fields"] = [
            controls["field1_edit"].text(),
            controls["field2_edit"].text(),
            controls["field3_edit"].text()
        ]
        data["page_format"] = controls["page_format_combo"].currentText()
        data["page_position"] = controls["page_position_combo"].currentText()
        
        # 计算页数
        data["total_pages"] = calculate_pages(data["text"], data["grid_type"], data["mode"])
        # 保持当前页面，不重置为第1页
        # 如果当前页面大于总页数，将其设置为总页数
        if data["current_page"] > data["total_pages"]:
            data["current_page"] = data["total_pages"] if data["total_pages"] > 0 else 1
        
        # 更新页码显示
        controls["page_label"].setText(f"{data['current_page']} / {data['total_pages']}")
        
        # 渲染预览
        renderer = GridRenderer(data["grid_type"])
        preview_image = renderer.render_preview(data)
        
        if preview_image:
            controls["preview_label"].setPixmap(preview_image)
    
    def prev_page(self):
        current_tab = self.tab_widget.currentWidget()
        data = current_tab.data
        controls = current_tab.controls
        
        if data["current_page"] > 1:
            data["current_page"] -= 1
            controls["page_label"].setText(f"{data['current_page']} / {data['total_pages']}")
            
            # 渲染预览
            renderer = GridRenderer(data["grid_type"])
            preview_image = renderer.render_preview(data)
            
            if preview_image:
                controls["preview_label"].setPixmap(preview_image)
    
    def next_page(self):
        current_tab = self.tab_widget.currentWidget()
        data = current_tab.data
        controls = current_tab.controls
        
        if data["current_page"] < data["total_pages"]:
            data["current_page"] += 1
            controls["page_label"].setText(f"{data['current_page']} / {data['total_pages']}")
            
            # 渲染预览
            renderer = GridRenderer(data["grid_type"])
            preview_image = renderer.render_preview(data)
            
            if preview_image:
                controls["preview_label"].setPixmap(preview_image)
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()
    
    def close_tab(self, index):
        """关闭标签页"""
        tab = self.tab_widget.widget(index)
        if tab:
            # 检查是否已修改
            if tab.data.get("modified", False):
                tab_title = self.tab_widget.tabText(index)
                # 移除*标记以获取原始标题
                original_title = tab_title.rstrip("*")
                reply = QMessageBox.question(
                    self, "提示", f"'{original_title}' 有未保存的更改，是否保存？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Cancel:
                    return
                elif reply == QMessageBox.StandardButton.Yes:
                    # 切换到该标签页并保存
                    self.tab_widget.setCurrentIndex(index)
                    self.save_project()
                    # 如果保存后仍然标记为修改（保存失败），则不关闭
                    if tab.data.get("modified", False):
                        return
            
            # 关闭标签页
            self.tab_widget.removeTab(index)
            
            # 如果没有标签页了，创建一个新的
            if self.tab_widget.count() == 0:
                self.new_tab()
    
    def closeEvent(self, event):
        """程序退出时检查未保存的标签页"""
        # 检查是否有未保存的标签页
        unsaved_tabs = []
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.data.get("modified", False):
                tab_title = self.tab_widget.tabText(i).rstrip("*")
                unsaved_tabs.append(tab_title)
        
        if unsaved_tabs:
            if len(unsaved_tabs) == 1:
                message = f"'{unsaved_tabs[0]}' 有未保存的更改，是否保存？"
            else:
                message = f"有 {len(unsaved_tabs)} 个工程未保存，是否保存所有更改？"
            
            reply = QMessageBox.question(
                self, "提示", message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                # 保存所有未保存的标签页
                for i in range(self.tab_widget.count()):
                    tab = self.tab_widget.widget(i)
                    if tab.data.get("modified", False):
                        self.tab_widget.setCurrentIndex(i)
                        self.save_project()
                        # 如果保存后仍然标记为修改（保存失败），则取消退出
                        if tab.data.get("modified", False):
                            event.ignore()
                            return
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())