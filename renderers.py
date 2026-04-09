from PyQt6.QtGui import QPainter, QPen, QFont, QPixmap, QColor, QFontDatabase
from PyQt6.QtCore import Qt, QRect
import fitz  # 导入PyMuPDF库
from utils import (
    GRID_SIZE_STANDARD, ROWS_PER_PAGE_STANDARD, COLS_PER_PAGE_STANDARD,
    GRID_SIZE_SQUARE, ROWS_PER_PAGE_SQUARE, COLS_PER_PAGE_SQUARE
)

# 获取系统默认字体，优先级：等线>微软雅黑>宋体
def get_default_font():
    font_families = QFontDatabase.families()
    if "等线" in font_families:
        return "等线"
    elif "微软雅黑" in font_families:
        return "微软雅黑"
    elif "宋体" in font_families:
        return "宋体"
    else:
        return "楷体"

class GridRenderer:
    def __init__(self, grid_type):
        self.grid_type = grid_type
        self.page_width = 595  # A4宽度（点）
        self.page_height = 842  # A4高度（点）
        self.margin = 50  # 页面边距
        
        # 根据线格类型设置不同的参数
        if grid_type in ["米字格", "田字格", "回宫格"]:
            self.grid_size = GRID_SIZE_STANDARD  # 格子大小
            self.rows_per_page = ROWS_PER_PAGE_STANDARD  # 每页行数
            self.cols_per_page = COLS_PER_PAGE_STANDARD  # 每页列数
        elif grid_type == "作文纸":
            self.grid_size = GRID_SIZE_SQUARE  # 作文纸使用较小的格子大小
            self.rows_per_page = ROWS_PER_PAGE_SQUARE  # 标准作文纸18行
            self.cols_per_page = COLS_PER_PAGE_SQUARE  # 标准作文纸20列
    
    def render_pdf(self, file_path, data):
        # 创建PDF文档
        doc = fitz.open()
        
        # 计算总页数
        total_pages = data.get("total_pages", 1)
        
        for page_num in range(total_pages):
            # 创建新页面
            page = doc.new_page(width=self.page_width, height=self.page_height)
            
            # 设置当前页面和总页数用于预览
            data["current_page"] = page_num + 1
            data["total_pages"] = total_pages
            
            # 渲染当前页面的预览（使用高分辨率）
            # 创建高分辨率的QPixmap（4倍分辨率）
            high_res_pixmap = QPixmap(595 * 4, 842 * 4)
            high_res_pixmap.fill(QColor(255, 255, 255))
            
            # 创建画家
            painter = QPainter(high_res_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # 缩放画家
            painter.scale(4, 4)
            
            # 绘制内容
            # 使用系统默认字体
            default_font = get_default_font()
            
            # 绘制字段（页眉）
            fields = data.get("fields", [])
            font = QFont(default_font, 11)  # 11磅字
            painter.setFont(font)
            
            field_y = 20  # 页眉位置
            field_x = 50
            
            for field in fields:
                if field:
                    painter.drawText(field_x, field_y, field)
                    field_x += 200
            
            # 在字段下方绘制横线
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawLine(50, 30, 545, 30)  # 横线位置，几乎贴着字段的下方
            
            # 绘制标题（横线下方）
            title = data.get("title", "")
            if title:
                font = QFont(default_font, 14, QFont.Weight.Bold)  # 14磅字
                painter.setFont(font)
                painter.drawText(
                    QRect(0, 45, 595, 15),  # 横线下方位置，y=45
                    Qt.AlignmentFlag.AlignCenter,
                    title
                )
            
            # 绘制格子和字符
            text = data.get("text", "")
            font_size = data.get("font_size", 36)
            line_spacing = data.get("line_spacing", 14)
            offset_x = data.get("offset_x", 0)
            offset_y = data.get("offset_y", 0)
            mode = data.get("mode", "描红")
            current_page = data.get("current_page", 1)
            
            # 首先，绘制所有格子（整页）
            # 根据页面高度和行数计算行间距，确保最后一行在y=810左右结束
            if self.grid_type in ["米字格", "田字格", "回宫格"]:
                # 米字格、田字格、回宫格：每页12行，顶部y=80，底部y=810
                # 最后一行的底部位置 = 80 + (12-1) * (40 + line_spacing) + 40 <= 810
                # 11 * (40 + line_spacing) <= 690
                # line_spacing <= 22.7，使用22
                calculated_line_spacing = 22
            elif self.grid_type == "作文纸":
                # 作文纸：每页20行，顶部y=80，底部y=810
                # 最后一行的底部位置 = 80 + (20-1) * (24 + line_spacing) + 24 <= 810
                # 19 * (24 + line_spacing) <= 706
                # line_spacing <= 13.1，使用13
                calculated_line_spacing = 13
            else:
                calculated_line_spacing = line_spacing
            
            for row in range(self.rows_per_page):
                for col in range(self.cols_per_page):
                    # 计算位置（横向无间距，保持纵向间距）
                    x = 50 + col * self.grid_size
                    y = 80 + row * (self.grid_size + calculated_line_spacing)  # 调整到标题下方，y=80
                    
                    # 绘制格子
                    self._draw_grid_qt(painter, x, y)
            
            # 然后，绘制字符（如果有）
            # 计算每页总行数
            total_rows_per_page = self.rows_per_page
            
            # 计算当前页面的起始和结束行
            start_row = (current_page - 1) * total_rows_per_page
            end_row = start_row + total_rows_per_page
            current_row = 0
            
            # 将文本分割成行
            lines = text.split('\n')
            
            # 处理每一行
            for line in lines:
                # 计算该行需要的行数
                if line:
                    line_rows = (len(line) + self.cols_per_page - 1) // self.cols_per_page
                    # 抄写模式和描红+抄写模式下，每写完1行后留1个空行
                    if mode in ["抄写", "描红+抄写"]:
                        line_rows *= 2  # 每个内容行后加一个空行
                else:
                    line_rows = 1
                
                # 检查该行是否与当前页面重叠
                if current_row + line_rows <= start_row:
                    # 行在当前页面之前，跳过
                    current_row += line_rows
                    continue
                elif current_row >= end_row:
                    # 行在当前页面之后，停止
                    break
                
                # 行与当前页面重叠，处理它
                if line:
                    # 计算每行的字符数
                    chars_per_row = self.cols_per_page
                    
                    # 计算在当前页面内的起始和结束行
                    line_start_row = max(current_row, start_row)
                    line_end_row = min(current_row + line_rows, end_row)
                    
                    # 计算起始字符索引
                    start_char_idx = (line_start_row - current_row) // 2 * chars_per_row if mode in ["抄写", "描红+抄写"] else (line_start_row - current_row) * chars_per_row
                    
                    # 绘制字符
                    char_idx = start_char_idx
                    for i in range(line_start_row - start_row, line_end_row - start_row):
                        # 抄写模式和描红+抄写模式下，只在奇数行绘制字符，偶数行为空行
                        if mode in ["抄写", "描红+抄写"] and i % 2 == 1:
                            continue
                        
                        for j in range(chars_per_row):
                            if char_idx >= len(line):
                                break
                            
                            # 计算位置，使用与格子相同的行间距
                            x = 50 + j * self.grid_size + offset_x
                            y = 80 + i * (self.grid_size + calculated_line_spacing) + offset_y  # 调整到标题下方，y=80
                            
                            # 绘制字符
                            if mode in ["描红", "描红+抄写"]:
                                font_name = data.get("font_name", "楷体")
                                font = QFont(font_name, font_size)
                                painter.setFont(font)
                                painter.setPen(QPen(QColor(255, 192, 192)))  # 淡红色
                                painter.drawText(
                                    QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                    Qt.AlignmentFlag.AlignCenter,
                                    line[char_idx]
                                )
                            elif mode in ["抄写", "纯字帖"]:
                                font_name = data.get("font_name", "楷体")
                                font = QFont(font_name, font_size)
                                painter.setFont(font)
                                painter.setPen(QPen(QColor(0, 0, 0)))  # 黑色
                                painter.drawText(
                                    QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                    Qt.AlignmentFlag.AlignCenter,
                                    line[char_idx]
                                )
                            
                            char_idx += 1
                else:
                    # 空行，如果在当前页面内则绘制
                    if current_row >= start_row and current_row < end_row:
                        # 空行，只需移动到下一行
                        pass
                
                # 更新当前行
                current_row += line_rows
            
            # 绘制页码（如果需要）
            page_format = data.get("page_format", "不显示")
            page_position = data.get("page_position", "底部居中")
            current_page = data.get("current_page", 1)
            total_pages = data.get("total_pages", 1)
            
            if page_format != "不显示":
                # 计算页码文本
                if page_format == "第1页":
                    page_text = f"第{current_page}页"
                elif page_format == "第一页":
                    # 将数字转换为中文
                    def num_to_chinese(num):
                        chinese_nums = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
                        if num <= 10:
                            return chinese_nums[num]
                        elif num < 20:
                            return f"十{chinese_nums[num % 10]}"
                        else:
                            return f"{chinese_nums[num // 10]}十{chinese_nums[num % 10]}"
                    page_text = f"第{num_to_chinese(current_page)}页"
                elif page_format == "第1页 共x页":
                    page_text = f"第{current_page}页 共{total_pages}页"
                elif page_format == "第一页 共X页":
                    page_text = f"第{num_to_chinese(current_page)}页 共{num_to_chinese(total_pages)}页"
                
                # 计算位置
                font = QFont(default_font, 11)  # 11磅字，与字段一致
                painter.setFont(font)
                painter.setPen(QPen(QColor(0, 0, 0)))
                
                text_rect = painter.boundingRect(QRect(0, 0, 595, 20), Qt.AlignmentFlag.AlignLeft, page_text)
                text_width = text_rect.width()
                text_height = text_rect.height()
                
                if page_position == "底部居中":
                    x = (595 - text_width) / 2
                    y = 842 - 20  # 下移一些，与字段对称
                elif page_position == "底部靠左":
                    x = 50
                    y = 842 - 20  # 下移一些，与字段对称
                elif page_position == "底部靠右":
                    x = 595 - 50 - text_width
                    y = 842 - 20  # 下移一些，与字段对称
                
                painter.drawText(int(x), int(y), page_text)
            
            painter.end()
            
            # 保存预览到临时文件（使用高分辨率）
            temp_file = f"temp_page_{page_num}.png"
            high_res_pixmap.save(temp_file, "PNG", 100)  # 100%质量
            
            # 将图片插入PDF页面
            rect = fitz.Rect(0, 0, self.page_width, self.page_height)
            page.insert_image(rect, filename=temp_file)
        
        # 保存PDF
        doc.save(file_path)
        doc.close()
        
        # 清理临时文件
        import os
        for page_num in range(total_pages):
            temp_file = f"temp_page_{page_num}.png"
            if os.path.exists(temp_file):
                os.remove(temp_file)
    

    
    def render_preview(self, data):
        # 创建A4大小的画布
        # A4尺寸：595x842点
        pixmap = QPixmap(595, 842)
        
        # 填充白色背景
        pixmap.fill(QColor(255, 255, 255))
        
        # 创建画家
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制字段（页眉）
        fields = data.get("fields", [])
        default_font = get_default_font()
        font = QFont(default_font, 11)  # 11磅字
        painter.setFont(font)
        
        field_y = 20  # 页眉位置
        field_x = 50
        
        for field in fields:
            if field:
                painter.drawText(field_x, field_y, field)
                field_x += 200
        
        # 在字段下方绘制横线
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawLine(50, 30, 545, 30)  # 横线位置，几乎贴着字段的下方
        
        # 绘制标题（横线下方）
        title = data.get("title", "")
        if title:
            font = QFont(default_font, 14, QFont.Weight.Bold)  # 14磅字
            painter.setFont(font)
            painter.drawText(
                QRect(0, 45, 595, 15),  # 横线下方位置，y=45
                Qt.AlignmentFlag.AlignCenter,
                title
            )
        
        # 绘制格子和字符
        # 调整位置以适应A4尺寸
        text = data.get("text", "")
        font_size = data.get("font_size", 36)
        char_spacing = data.get("char_spacing", 10)
        line_spacing = data.get("line_spacing", 14)
        offset_x = data.get("offset_x", 0)
        offset_y = data.get("offset_y", 0)
        mode = data.get("mode", "描红")
        current_page = data.get("current_page", 1)
        
        # 首先，绘制所有格子（整页）
        # 根据页面高度和行数计算行间距，确保最后一行在y=810左右结束
        if self.grid_type in ["米字格", "田字格", "回宫格"]:
            # 米字格、田字格、回宫格：每页12行，顶部y=80，底部y=810
            # 最后一行的底部位置 = 80 + (12-1) * (40 + line_spacing) + 40 <= 810
            # 11 * (40 + line_spacing) <= 690
            # line_spacing <= 22.7，使用22
            calculated_line_spacing = 22
        elif self.grid_type == "作文纸":
            # 作文纸：每页20行，顶部y=80，底部y=810
            # 最后一行的底部位置 = 80 + (20-1) * (24 + line_spacing) + 24 <= 810
            # 19 * (24 + line_spacing) <= 706
            # line_spacing <= 13.1，使用13
            calculated_line_spacing = 13
        else:
            calculated_line_spacing = line_spacing
        
        for row in range(self.rows_per_page):
            for col in range(self.cols_per_page):
                # 计算位置（横向无间距，保持纵向间距）
                x = 50 + col * self.grid_size
                y = 80 + row * (self.grid_size + calculated_line_spacing)  # 调整到标题下方，y=80
                
                # 绘制格子
                self._draw_grid_qt(painter, x, y)
        
        # 然后，绘制字符（如果有）
        row = 0
        col = 0
        
        # 计算每页总行数
        total_rows_per_page = self.rows_per_page
        
        # 计算当前页面的起始和结束行
        start_row = (current_page - 1) * total_rows_per_page
        end_row = start_row + total_rows_per_page
        current_row = 0
        
        # 将文本分割成行
        lines = text.split('\n')
        
        # 处理每一行
        for line in lines:
            # 计算该行需要的行数
            if line:
                line_rows = (len(line) + self.cols_per_page - 1) // self.cols_per_page
                # 抄写模式和描红+抄写模式下，每写完1行后留1个空行
                if mode in ["抄写", "描红+抄写"]:
                    line_rows *= 2  # 每个内容行后加一个空行
            else:
                line_rows = 1
            
            # 检查该行是否与当前页面重叠
            if current_row + line_rows <= start_row:
                # 行在当前页面之前，跳过
                current_row += line_rows
                continue
            elif current_row >= end_row:
                # 行在当前页面之后，停止
                break
            
            # 行与当前页面重叠，处理它
            if line:
                # 计算每行的字符数
                chars_per_row = self.cols_per_page
                
                # 计算在当前页面内的起始和结束行
                line_start_row = max(current_row, start_row)
                line_end_row = min(current_row + line_rows, end_row)
                
                # 计算起始字符索引
                start_char_idx = (line_start_row - current_row) // 2 * chars_per_row if mode in ["抄写", "描红+抄写"] else (line_start_row - current_row) * chars_per_row
                
                # 绘制字符
                char_idx = start_char_idx
                for i in range(line_start_row - start_row, line_end_row - start_row):
                    # 抄写模式和描红+抄写模式下，只在奇数行绘制字符，偶数行为空行
                    if mode in ["抄写", "描红+抄写"] and i % 2 == 1:
                        continue
                    
                    for j in range(chars_per_row):
                        if char_idx >= len(line):
                            break
                        
                        # 计算位置，使用与格子相同的行间距
                        x = 50 + j * self.grid_size + offset_x
                        y = 80 + i * (self.grid_size + calculated_line_spacing) + offset_y  # 调整到标题下方，y=80
                        
                        # 绘制字符
                        if mode in ["描红", "描红+抄写"]:
                            font_name = data.get("font_name", "楷体")
                            font = QFont(font_name, font_size)
                            painter.setFont(font)
                            painter.setPen(QPen(QColor(255, 192, 192)))  # 淡红色
                            painter.drawText(
                                QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                Qt.AlignmentFlag.AlignCenter,
                                line[char_idx]
                            )
                        elif mode == "抄写":
                            font_name = data.get("font_name", "楷体")
                            font = QFont(font_name, font_size)
                            painter.setFont(font)
                            painter.setPen(QPen(QColor(0, 0, 0)))  # 黑色
                            painter.drawText(
                                QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                Qt.AlignmentFlag.AlignCenter,
                                line[char_idx]
                            )
                        elif mode == "纯字帖":
                            font_name = data.get("font_name", "楷体")
                            font = QFont(font_name, font_size)
                            painter.setFont(font)
                            painter.setPen(QPen(QColor(0, 0, 0)))  # 黑色
                            painter.drawText(
                                QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                Qt.AlignmentFlag.AlignCenter,
                                line[char_idx]
                            )
                        
                        char_idx += 1
            else:
                # 空行，如果在当前页面内则绘制
                if current_row >= start_row and current_row < end_row:
                    # 空行，只需移动到下一行
                    pass
            
            # 更新当前行
            current_row += line_rows
        
        # 绘制页码（如果需要）
        page_format = data.get("page_format", "不显示")
        page_position = data.get("page_position", "底部居中")
        current_page = data.get("current_page", 1)
        total_pages = data.get("total_pages", 1)
        
        if page_format != "不显示":
            # 计算页码文本
            if page_format == "第1页":
                page_text = f"第{current_page}页"
            elif page_format == "第一页":
                # 将数字转换为中文
                def num_to_chinese(num):
                    chinese_nums = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
                    if num <= 10:
                        return chinese_nums[num]
                    elif num < 20:
                        return f"十{chinese_nums[num % 10]}"
                    else:
                        return f"{chinese_nums[num // 10]}十{chinese_nums[num % 10]}"
                page_text = f"第{num_to_chinese(current_page)}页"
            elif page_format == "第1页 共x页":
                page_text = f"第{current_page}页 共{total_pages}页"
            elif page_format == "第一页 共X页":
                page_text = f"第{num_to_chinese(current_page)}页 共{num_to_chinese(total_pages)}页"
            
            # 计算位置
            default_font = get_default_font()
            font = QFont(default_font, 11)  # 11磅字
            painter.setFont(font)
            painter.setPen(QPen(QColor(0, 0, 0)))
            
            text_rect = painter.boundingRect(QRect(0, 0, 595, 20), Qt.AlignmentFlag.AlignLeft, page_text)
            text_width = text_rect.width()
            text_height = text_rect.height()
            
            if page_position == "底部居中":
                x = (595 - text_width) / 2
                y = 842 - 20  # 下移一些，与字段对称
            elif page_position == "底部靠左":
                x = 50
                y = 842 - 20  # 下移一些，与字段对称
            elif page_position == "底部靠右":
                x = 595 - 50 - text_width
                y = 842 - 20  # 下移一些，与字段对称
            
            painter.drawText(int(x), int(y), page_text)
        
        painter.end()
        return pixmap
    

    
    def _draw_grid_and_chars(self, page, data, page_num):
        # 获取数据
        text = data.get("text", "")
        font_size = data.get("font_size", 36)
        char_spacing = data.get("char_spacing", 10)
        line_spacing = data.get("line_spacing", 14)
        offset_x = data.get("offset_x", 0)
        offset_y = data.get("offset_y", 0)
        mode = data.get("mode", "描红")
        
        # 首先，绘制所有格子（整页）
        # 根据页面高度和行数计算行间距，确保最后一行在y=810左右结束
        if self.grid_type in ["米字格", "田字格", "回宫格"]:
            # 米字格、田字格、回宫格：每页12行，顶部y=80，底部y=810
            # 最后一行的底部位置 = 80 + (12-1) * (40 + line_spacing) + 40 <= 810
            # 11 * (40 + line_spacing) <= 690
            # line_spacing <= 22.7，使用22
            calculated_line_spacing = 22
        elif self.grid_type == "作文纸":
            # 作文纸：每页20行，顶部y=80，底部y=810
            # 最后一行的底部位置 = 80 + (20-1) * (24 + line_spacing) + 24 <= 810
            # 19 * (24 + line_spacing) <= 706
            # line_spacing <= 13.1，使用13
            calculated_line_spacing = 13
        else:
            calculated_line_spacing = line_spacing
        
        for row in range(self.rows_per_page):
            for col in range(self.cols_per_page):
                # 计算位置（横向无间距，保持纵向间距）
                x = 50 + col * self.grid_size
                y = 80 + row * (self.grid_size + calculated_line_spacing)  # 调整到标题下方，y=80
                
                # 绘制格子
                self._draw_grid(page, x, y)
        
        # 然后，绘制字符（如果有）
        row = 0
        col = 0
        
        # 计算每页总行数
        total_rows_per_page = self.rows_per_page
        
        # 计算当前页面的起始和结束行
        start_row = page_num * total_rows_per_page
        end_row = start_row + total_rows_per_page
        current_row = 0
        
        # 将文本分割成行
        lines = text.split('\n')
        
        # 处理每一行
        for line in lines:
            # 计算该行需要的行数
            if line:
                line_rows = (len(line) + self.cols_per_page - 1) // self.cols_per_page
                # 抄写模式和描红+抄写模式下，每写完1行后留1个空行
                if mode in ["抄写", "描红+抄写"]:
                    line_rows *= 2  # 每个内容行后加一个空行
            else:
                line_rows = 1
            
            # 检查该行是否与当前页面重叠
            if current_row + line_rows <= start_row:
                # 行在当前页面之前，跳过
                current_row += line_rows
                continue
            elif current_row >= end_row:
                # 行在当前页面之后，停止
                break
            
            # 行与当前页面重叠，处理它
            if line:
                # 计算每行的字符数
                chars_per_row = self.cols_per_page
                
                # 计算在当前页面内的起始和结束行
                line_start_row = max(current_row, start_row)
                line_end_row = min(current_row + line_rows, end_row)
                
                # 计算起始字符索引
                start_char_idx = (line_start_row - current_row) // 2 * chars_per_row if mode in ["抄写", "描红+抄写"] else (line_start_row - current_row) * chars_per_row
                
                # 绘制字符
                char_idx = start_char_idx
                for i in range(line_start_row - start_row, line_end_row - start_row):
                    # 抄写模式和描红+抄写模式下，只在奇数行绘制字符，偶数行为空行
                    if mode in ["抄写", "描红+抄写"] and i % 2 == 1:
                        continue
                    
                    for j in range(chars_per_row):
                        if char_idx >= len(line):
                            break
                        
                        # 计算位置，使用与格子相同的行间距
                        x = 50 + j * self.grid_size + offset_x
                        y = 80 + i * (self.grid_size + calculated_line_spacing) + offset_y  # 调整到标题下方，y=80
                        
                        # 绘制字符
                        if mode in ["描红", "描红+抄写"]:
                            font_name = data.get("font_name", "楷体")
                            # 使用用户选择的字体，如果不可用则使用默认字体
                            try:
                                # 计算字符宽度，用于居中对齐
                                char_width = fitz.get_text_length(line[char_idx], fontname=font_name, fontsize=font_size)
                                # 调整位置以实现居中对齐
                                char_x = x + (self.grid_size - char_width) / 2
                                char_y = y + self.grid_size / 2
                                page.insert_text(
                                    (char_x, char_y),
                                    line[char_idx],
                                    fontname=font_name,
                                    fontsize=font_size,
                                    color=(1.0, 0.75, 0.75)  # 淡红色 RGB(255, 192, 192)
                                )
                            except:
                                # 如果用户选择的字体不可用，使用默认字体
                                # 计算字符宽度，用于居中对齐
                                char_width = fitz.get_text_length(line[char_idx], fontname="china-s", fontsize=font_size)
                                # 调整位置以实现居中对齐
                                char_x = x + (self.grid_size - char_width) / 2
                                char_y = y + self.grid_size / 2
                                page.insert_text(
                                    (char_x, char_y),
                                    line[char_idx],
                                    fontname="china-s",
                                    fontsize=font_size,
                                    color=(1.0, 0.75, 0.75)  # 淡红色 RGB(255, 192, 192)
                                )
                        elif mode in ["抄写", "纯字帖"]:
                            font_name = data.get("font_name", "楷体")
                            # 使用用户选择的字体，如果不可用则使用默认字体
                            try:
                                # 计算字符宽度，用于居中对齐
                                char_width = fitz.get_text_length(line[char_idx], fontname=font_name, fontsize=font_size)
                                # 调整位置以实现居中对齐
                                char_x = x + (self.grid_size - char_width) / 2
                                char_y = y + self.grid_size / 2
                                page.insert_text(
                                    (char_x, char_y),
                                    line[char_idx],
                                    fontname=font_name,
                                    fontsize=font_size,
                                    color=(0, 0, 0)  # 黑色
                                )
                            except:
                                # 如果用户选择的字体不可用，使用默认字体
                                # 计算字符宽度，用于居中对齐
                                char_width = fitz.get_text_length(line[char_idx], fontname="china-s", fontsize=font_size)
                                # 调整位置以实现居中对齐
                                char_x = x + (self.grid_size - char_width) / 2
                                char_y = y + self.grid_size / 2
                                page.insert_text(
                                    (char_x, char_y),
                                    line[char_idx],
                                    fontname="china-s",
                                    fontsize=font_size,
                                    color=(0, 0, 0)  # 黑色
                                )
                        
                        char_idx += 1
            else:
                # 空行，如果在当前页面内则绘制
                if current_row >= start_row and current_row < end_row:
                    # 空行，只需移动到下一行
                    pass
            
            # 更新当前行
            current_row += line_rows
    
    def _draw_grid_and_chars_qt(self, painter, data):
        # 获取数据
        text = data.get("text", "")
        font_size = data.get("font_size", 36)
        char_spacing = data.get("char_spacing", 10)
        line_spacing = data.get("line_spacing", 14)
        offset_x = data.get("offset_x", 0)
        offset_y = data.get("offset_y", 0)
        mode = data.get("mode", "描红")
        current_page = data.get("current_page", 1)
        
        # 首先，绘制所有格子（整页）
        # 根据页面高度和行数计算行间距，确保最后一行在y=810左右结束
        if self.grid_type in ["米字格", "田字格", "回宫格"]:
            # 米字格、田字格、回宫格：每页12行，顶部y=80，底部y=810
            # 最后一行的底部位置 = 80 + (12-1) * (40 + line_spacing) + 40 <= 810
            # 11 * (40 + line_spacing) <= 690
            # line_spacing <= 22.7，使用22
            calculated_line_spacing = 22
        elif self.grid_type == "作文纸":
            # 作文纸：每页20行，顶部y=80，底部y=810
            # 最后一行的底部位置 = 80 + (20-1) * (24 + line_spacing) + 24 <= 810
            # 19 * (24 + line_spacing) <= 706
            # line_spacing <= 13.1，使用13
            calculated_line_spacing = 13
        else:
            calculated_line_spacing = line_spacing
        
        for row in range(self.rows_per_page):
            for col in range(self.cols_per_page):
                # 计算位置（横向无间距，保持纵向间距）
                x = 50 + col * self.grid_size
                y = 80 + row * (self.grid_size + calculated_line_spacing)  # 调整到标题下方，y=80
                
                # 绘制格子
                self._draw_grid_qt(painter, x, y)
        
        # 然后，绘制字符（如果有）
        row = 0
        col = 0
        
        # 计算每页总行数
        total_rows_per_page = self.rows_per_page
        
        # 计算当前页面的起始和结束行
        start_row = (current_page - 1) * total_rows_per_page
        end_row = start_row + total_rows_per_page
        current_row = 0
        
        # 将文本分割成行
        lines = text.split('\n')
        
        # 处理每一行
        for line in lines:
            # 计算该行需要的行数
            if line:
                line_rows = (len(line) + self.cols_per_page - 1) // self.cols_per_page
                # 抄写模式和描红+抄写模式下，每写完1行后留1个空行
                if mode in ["抄写", "描红+抄写"]:
                    line_rows *= 2  # 每个内容行后加一个空行
            else:
                line_rows = 1
            
            # 检查该行是否与当前页面重叠
            if current_row + line_rows <= start_row:
                # 行在当前页面之前，跳过
                current_row += line_rows
                continue
            elif current_row >= end_row:
                # 行在当前页面之后，停止
                break
            
            # 行与当前页面重叠，处理它
            if line:
                # 计算每行的字符数
                chars_per_row = self.cols_per_page
                
                # 计算在当前页面内的起始和结束行
                line_start_row = max(current_row, start_row)
                line_end_row = min(current_row + line_rows, end_row)
                
                # 计算起始字符索引
                start_char_idx = (line_start_row - current_row) // 2 * chars_per_row if mode in ["抄写", "描红+抄写"] else (line_start_row - current_row) * chars_per_row
                
                # 绘制字符
                char_idx = start_char_idx
                for i in range(line_start_row - start_row, line_end_row - start_row):
                    # 抄写模式和描红+抄写模式下，只在奇数行绘制字符，偶数行为空行
                    if mode in ["抄写", "描红+抄写"] and i % 2 == 1:
                        continue
                    
                    for j in range(chars_per_row):
                        if char_idx >= len(line):
                            break
                        
                        # 计算位置，使用与格子相同的行间距
                        x = 50 + j * self.grid_size + offset_x
                        y = 80 + i * (self.grid_size + calculated_line_spacing) + offset_y  # 调整到标题下方，y=80
                        
                        # 绘制字符
                        if mode in ["描红", "描红+抄写"]:
                            font_name = data.get("font_name", "楷体")
                            font = QFont(font_name, font_size)
                            painter.setFont(font)
                            painter.setPen(QPen(QColor(255, 192, 192)))  # 淡红色
                            painter.drawText(
                                QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                Qt.AlignmentFlag.AlignCenter,
                                line[char_idx]
                            )
                        elif mode == "抄写":
                            font_name = data.get("font_name", "楷体")
                            font = QFont(font_name, font_size)
                            painter.setFont(font)
                            painter.setPen(QPen(QColor(0, 0, 0)))  # 黑色
                            painter.drawText(
                                QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                Qt.AlignmentFlag.AlignCenter,
                                line[char_idx]
                            )
                        elif mode == "纯字帖":
                            font_name = data.get("font_name", "楷体")
                            font = QFont(font_name, font_size)
                            painter.setFont(font)
                            painter.setPen(QPen(QColor(0, 0, 0)))  # 黑色
                            painter.drawText(
                                QRect(int(x), int(y), int(self.grid_size), int(self.grid_size)),
                                Qt.AlignmentFlag.AlignCenter,
                                line[char_idx]
                            )
                        
                        char_idx += 1
            else:
                # 空行，如果在当前页面内则绘制
                if current_row >= start_row and current_row < end_row:
                    # 空行，只需移动到下一行
                    pass
            
            # 更新当前行
            current_row += line_rows
    
    def _draw_grid(self, page, x, y):
        # 根据类型绘制格子
        if self.grid_type == "米字格":
            # 绘制正方形
            page.draw_rect(
                fitz.Rect(x, y, x + self.grid_size, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5
            )
            # 绘制十字线（虚线）
            page.draw_line(
                (x, y + self.grid_size / 2),
                (x + self.grid_size, y + self.grid_size / 2),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            page.draw_line(
                (x + self.grid_size / 2, y),
                (x + self.grid_size / 2, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            # 绘制对角线（虚线）
            page.draw_line(
                (x, y),
                (x + self.grid_size, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            page.draw_line(
                (x + self.grid_size, y),
                (x, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
        elif self.grid_type == "田字格":
            # 绘制正方形
            page.draw_rect(
                fitz.Rect(x, y, x + self.grid_size, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5
            )
            # 绘制十字线（虚线）
            page.draw_line(
                (x, y + self.grid_size / 2),
                (x + self.grid_size, y + self.grid_size / 2),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            page.draw_line(
                (x + self.grid_size / 2, y),
                (x + self.grid_size / 2, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
        elif self.grid_type == "回宫格":
            # 绘制外正方形
            page.draw_rect(
                fitz.Rect(x, y, x + self.grid_size, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5
            )
            # 绘制内矩形（虚线），宽高比1:0.618
            inner_height = self.grid_size * 0.6
            inner_width = inner_height * 0.618  # 1:0.618 宽高比
            inner_x = x + (self.grid_size - inner_width) / 2
            inner_y = y + (self.grid_size - inner_height) / 2
            # 对于虚线矩形，我们需要绘制四条虚线
            # 顶部线
            page.draw_line(
                (inner_x, inner_y),
                (inner_x + inner_width, inner_y),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            # 右侧线
            page.draw_line(
                (inner_x + inner_width, inner_y),
                (inner_x + inner_width, inner_y + inner_height),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            # 底部线
            page.draw_line(
                (inner_x + inner_width, inner_y + inner_height),
                (inner_x, inner_y + inner_height),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
            # 左侧线
            page.draw_line(
                (inner_x, inner_y + inner_height),
                (inner_x, inner_y),
                color=(0, 0.5, 0),  # 绿色
                width=0.5,
                dashes=[2, 2]
            )
        elif self.grid_type == "作文纸":
            # 绘制正方形
            page.draw_rect(
                fitz.Rect(x, y, x + self.grid_size, y + self.grid_size),
                color=(0, 0.5, 0),  # 绿色
                width=0.5
            )

    
    def _draw_grid_qt(self, painter, x, y):
        # 根据类型绘制格子
        if self.grid_type == "米字格":
            # 绘制正方形
            painter.setPen(QPen(QColor(0, 128, 0), 0.5))  # 绿色
            painter.drawRect(int(x), int(y), int(self.grid_size), int(self.grid_size))
            # 绘制十字线（虚线）
            dashed_pen = QPen(QColor(0, 128, 0), 0.5)  # 绿色
            dashed_pen.setDashPattern([2, 2])
            painter.setPen(dashed_pen)
            painter.drawLine(
                int(x), int(y + self.grid_size / 2),
                int(x + self.grid_size), int(y + self.grid_size / 2)
            )
            painter.drawLine(
                int(x + self.grid_size / 2), int(y),
                int(x + self.grid_size / 2), int(y + self.grid_size)
            )
            # 绘制对角线（虚线）
            painter.drawLine(
                int(x), int(y),
                int(x + self.grid_size), int(y + self.grid_size)
            )
            painter.drawLine(
                int(x + self.grid_size), int(y),
                int(x), int(y + self.grid_size)
            )
        elif self.grid_type == "田字格":
            # 绘制正方形
            painter.setPen(QPen(QColor(0, 128, 0), 0.5))  # 绿色
            painter.drawRect(int(x), int(y), int(self.grid_size), int(self.grid_size))
            # 绘制十字线（虚线）
            dashed_pen = QPen(QColor(0, 128, 0), 0.5)  # 绿色
            dashed_pen.setDashPattern([2, 2])
            painter.setPen(dashed_pen)
            painter.drawLine(
                int(x), int(y + self.grid_size / 2),
                int(x + self.grid_size), int(y + self.grid_size / 2)
            )
            painter.drawLine(
                int(x + self.grid_size / 2), int(y),
                int(x + self.grid_size / 2), int(y + self.grid_size)
            )
        elif self.grid_type == "回宫格":
            # 绘制外正方形
            painter.setPen(QPen(QColor(0, 128, 0), 0.5))  # 绿色
            painter.drawRect(int(x), int(y), int(self.grid_size), int(self.grid_size))
            # 绘制内矩形（虚线），宽高比1:0.618
            dashed_pen = QPen(QColor(0, 128, 0), 0.5)  # 绿色
            dashed_pen.setDashPattern([2, 2])
            painter.setPen(dashed_pen)
            inner_height = self.grid_size * 0.6
            inner_width = inner_height * 0.618  # 1:0.618 宽高比
            inner_x = x + (self.grid_size - inner_width) / 2
            inner_y = y + (self.grid_size - inner_height) / 2
            painter.drawRect(int(inner_x), int(inner_y), int(inner_width), int(inner_height))
        elif self.grid_type == "作文纸":
            # 绘制正方形
            painter.setPen(QPen(QColor(0, 128, 0), 0.5))  # 绿色
            painter.drawRect(int(x), int(y), int(self.grid_size), int(self.grid_size))
