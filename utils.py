# 全局变量定义
# 米字格、田字格、回宫格参数
GRID_SIZE_STANDARD = 40  # 标准格子大小
ROWS_PER_PAGE_STANDARD = 12  # 标准每页行数
COLS_PER_PAGE_STANDARD = 12  # 标准每页列数

# 方格参数
GRID_SIZE_SQUARE = 24  # 方格大小
ROWS_PER_PAGE_SQUARE = 20  # 方格每页行数
COLS_PER_PAGE_SQUARE = 20  # 方格每页列数

# 其他参数
GRID_SIZE_OTHER = 40  # 其他格子大小
ROWS_PER_PAGE_OTHER = 8  # 其他每页行数
COLS_PER_PAGE_OTHER = 6  # 其他每页列数

def calculate_pages(text, grid_type, mode):
    """
    计算字帖页数
    :param text: 输入文本
    :param grid_type: 线格类型
    :param mode: 模式（描红、抄写、描红+抄写、纯字帖）
    :return: 页数
    """
    # 根据线格类型计算每页字符数和每行字符数
    if grid_type in ["米字格", "田字格", "回宫格"]:
        rows_per_page = ROWS_PER_PAGE_STANDARD
        cols_per_page = COLS_PER_PAGE_STANDARD
    elif grid_type == "作文纸":
        rows_per_page = ROWS_PER_PAGE_SQUARE
        cols_per_page = COLS_PER_PAGE_SQUARE
    else:
        rows_per_page = ROWS_PER_PAGE_OTHER
        cols_per_page = COLS_PER_PAGE_OTHER
    
    # 按照用户需求的逻辑计算页数
    # 1. 字数大于 cols_per_page 或者出现 \n，文字行数+1
    # 2. 文字行数大于 rows_per_page，页数+1
    lines = text.split('\n')
    text_rows = 0
    
    for line in lines:
        if line:
            # 计算该行需要的行数
            line_rows = (len(line) + cols_per_page - 1) // cols_per_page
            # 抄写模式和描红+抄写模式下，每写完1行后留1个空行
            if mode in ["抄写", "描红+抄写"]:
                line_rows *= 2
            text_rows += line_rows
        else:
            # 空行也占用一行的空间
            text_rows += 1
    
    # 计算页数
    if text_rows == 0:
        return 1
    
    # 文字行数大于 rows_per_page，页数+1
    pages = (text_rows + rows_per_page - 1) // rows_per_page
    
    return pages