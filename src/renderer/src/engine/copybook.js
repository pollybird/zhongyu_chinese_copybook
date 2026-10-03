/**
 * 汉字字帖排版与渲染引擎（由 PyQt6 版 main.py / renderers.py / utils.py 移植）
 *
 * 页面坐标系与原版完全一致：595 x 842（A4 点）
 * - 绘制区域 margin = 50
 * - 内容区 y ∈ [80, 810)
 * - 格子大小：米字格/田字格/回宫格 40x40，作文纸 24x24
 * - 行间距：标准 22，作文纸 13
 */

export const PAGE_W = 595
export const PAGE_H = 842

const MARGIN = 50
const CONTENT_TOP = 80
const CONTENT_BOTTOM = 810

const GRID_SIZE_STANDARD = 40
const ROWS_PER_PAGE_STANDARD = 12
const COLS_PER_PAGE_STANDARD = 12

const GRID_SIZE_SQUARE = 24
const ROWS_PER_PAGE_SQUARE = 20
const COLS_PER_PAGE_SQUARE = 20

const LINE_SPACING_STANDARD = 22
const LINE_SPACING_SQUARE = 13

const GRID_COLOR = '#008000' // 绿色
const TRACE_COLOR = '#ffc0c0' // 淡红色
const BLACK = '#000000'

const GRID_TYPES = ['米字格', '田字格', '回宫格', '作文纸']
const COPY_MODES = ['抄写', '描红+抄写']
const TRACE_MODES = ['描红', '描红+抄写']

/** 根据线格类型获取参数 */
export function getGridParams(gridType) {
  if (gridType === '作文纸') {
    return {
      gridSize: GRID_SIZE_SQUARE,
      rowsPerPage: ROWS_PER_PAGE_SQUARE,
      colsPerPage: COLS_PER_PAGE_SQUARE,
      lineSpacing: LINE_SPACING_SQUARE
    }
  }
  return {
    gridSize: GRID_SIZE_STANDARD,
    rowsPerPage: ROWS_PER_PAGE_STANDARD,
    colsPerPage: COLS_PER_PAGE_STANDARD,
    lineSpacing: LINE_SPACING_STANDARD
  }
}

/**
 * 计算字帖页数（与原版 utils.py calculate_pages 逻辑一致）
 */
export function calculatePages(text, gridType, mode) {
  const { rowsPerPage, colsPerPage } = getGridParams(gridType)

  const lines = text.split('\n')
  let textRows = 0

  for (const line of lines) {
    if (line) {
      let lineRows = Math.ceil(line.length / colsPerPage)
      if (COPY_MODES.includes(mode)) {
        lineRows *= 2
      }
      textRows += lineRows
    } else {
      textRows += 1
    }
  }

  if (textRows === 0) return 1
  return Math.ceil(textRows / rowsPerPage)
}

/**
 * 排版单页：将文本按行分配到格子中
 * 返回 { rows: [{ y, cells: [{ x, char, color }] }], nextLine, nextChar }
 */
export function layoutPage(text, gridType, mode, pageIndex, offsetX, offsetY, fontSize, fontName) {
  const { gridSize, rowsPerPage, colsPerPage, lineSpacing } = getGridParams(gridType)

  const lines = text.split('\n')
  const startRow = pageIndex * rowsPerPage
  const endRow = startRow + rowsPerPage

  // 预计算每行文本占用的行数
  const lineInfos = []
  let currentRow = 0
  for (const line of lines) {
    if (line) {
      let lineRows = Math.ceil(line.length / colsPerPage)
      if (COPY_MODES.includes(mode)) {
        lineRows *= 2
      }
      lineInfos.push({ line, lineRows, startRow: currentRow })
      currentRow += lineRows
    } else {
      lineInfos.push({ line: '', lineRows: 1, startRow: currentRow })
      currentRow += 1
    }
  }

  const rows = []
  let nextLine = 0
  let nextChar = 0

  for (let i = 0; i < rowsPerPage; i++) {
    const globalRow = startRow + i
    const y = CONTENT_TOP + i * (gridSize + lineSpacing)
    const cells = []

    // 找到当前行对应的文本行
    for (let li = 0; li < lineInfos.length; li++) {
      const info = lineInfos[li]
      if (globalRow >= info.startRow && globalRow < info.startRow + info.lineRows) {
        const rowInLine = globalRow - info.startRow
        // 抄写/描红+抄写模式下，奇数行为空行
        if (COPY_MODES.includes(mode) && rowInLine % 2 === 1) {
          break
        }
        const charsPerRow = colsPerPage
        const startCharIdx = COPY_MODES.includes(mode)
          ? Math.floor(rowInLine / 2) * charsPerRow
          : rowInLine * charsPerRow

        for (let j = 0; j < charsPerRow; j++) {
          const charIdx = startCharIdx + j
          if (charIdx >= info.line.length) break
          const x = MARGIN + j * gridSize + offsetX
          const charY = y + offsetY
          const color = TRACE_MODES.includes(mode) ? TRACE_COLOR : BLACK
          cells.push({ x, y: charY, char: info.line[charIdx], color })
        }
        nextLine = li
        nextChar = startCharIdx + charsPerRow
        break
      }
    }
    rows.push({ y, cells })
  }

  return { rows, nextLine, nextChar }
}

/** 绘制米字格 */
function drawMiZiGe(ctx, x, y, size) {
  ctx.strokeStyle = GRID_COLOR
  ctx.lineWidth = 0.5
  // 外框
  ctx.strokeRect(x, y, size, size)
  // 十字虚线
  ctx.setLineDash([2, 2])
  ctx.beginPath()
  ctx.moveTo(x, y + size / 2)
  ctx.lineTo(x + size, y + size / 2)
  ctx.moveTo(x + size / 2, y)
  ctx.lineTo(x + size / 2, y + size)
  ctx.stroke()
  // 对角线虚线
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + size, y + size)
  ctx.moveTo(x + size, y)
  ctx.lineTo(x, y + size)
  ctx.stroke()
  ctx.setLineDash([])
}

/** 绘制田字格 */
function drawTianZiGe(ctx, x, y, size) {
  ctx.strokeStyle = GRID_COLOR
  ctx.lineWidth = 0.5
  ctx.strokeRect(x, y, size, size)
  ctx.setLineDash([2, 2])
  ctx.beginPath()
  ctx.moveTo(x, y + size / 2)
  ctx.lineTo(x + size, y + size / 2)
  ctx.moveTo(x + size / 2, y)
  ctx.lineTo(x + size / 2, y + size)
  ctx.stroke()
  ctx.setLineDash([])
}

/** 绘制回宫格 */
function drawHuiGongGe(ctx, x, y, size) {
  ctx.strokeStyle = GRID_COLOR
  ctx.lineWidth = 0.5
  ctx.strokeRect(x, y, size, size)
  ctx.setLineDash([2, 2])
  const innerHeight = size * 0.6
  const innerWidth = innerHeight * 0.618
  const innerX = x + (size - innerWidth) / 2
  const innerY = y + (size - innerHeight) / 2
  ctx.strokeRect(innerX, innerY, innerWidth, innerHeight)
  ctx.setLineDash([])
}

/** 绘制作文纸格子 */
function drawZuoWenZhi(ctx, x, y, size) {
  ctx.strokeStyle = GRID_COLOR
  ctx.lineWidth = 0.5
  ctx.strokeRect(x, y, size, size)
}

/** 绘制格子 */
function drawGrid(ctx, x, y, size, gridType) {
  switch (gridType) {
    case '米字格':
      drawMiZiGe(ctx, x, y, size)
      break
    case '田字格':
      drawTianZiGe(ctx, x, y, size)
      break
    case '回宫格':
      drawHuiGongGe(ctx, x, y, size)
      break
    case '作文纸':
      drawZuoWenZhi(ctx, x, y, size)
      break
  }
}

/** 数字转中文 */
function numToChinese(num) {
  const chineseNums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
  if (num <= 10) return chineseNums[num]
  if (num < 20) return `十${chineseNums[num % 10]}`
  return `${chineseNums[Math.floor(num / 10)]}十${chineseNums[num % 10]}`
}

/** 获取页码文本 */
function getPageText(format, currentPage, totalPages) {
  switch (format) {
    case '第1页':
      return `第${currentPage}页`
    case '第一页':
      return `第${numToChinese(currentPage)}页`
    case '第1页 共x页':
      return `第${currentPage}页 共${totalPages}页`
    case '第一页 共X页':
      return `第${numToChinese(currentPage)}页 共${numToChinese(totalPages)}页`
    default:
      return ''
  }
}

/**
 * 在指定 ctx 上渲染一页
 * @param {CanvasRenderingContext2D} ctx 已按 dpr 缩放的上下文
 * @param {object} settings 工程设置
 * @param {number} pageIndex 从 0 开始
 * @param {number} totalPages 总页数
 */
export function renderPage(ctx, settings, pageIndex, totalPages) {
  const { gridSize, rowsPerPage, colsPerPage, lineSpacing } = getGridParams(settings.grid_type)

  ctx.save()
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, PAGE_W, PAGE_H)

  // 绘制头部字段
  const fields = settings.fields || []
  ctx.fillStyle = BLACK
  ctx.font = '11px sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'alphabetic'
  let fieldX = MARGIN
  const fieldY = 20
  for (const field of fields) {
    if (field) {
      ctx.fillText(field, fieldX, fieldY)
      fieldX += 200
    }
  }

  // 字段下方横线
  ctx.strokeStyle = BLACK
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(MARGIN, 30)
  ctx.lineTo(PAGE_W - MARGIN, 30)
  ctx.stroke()

  // 标题
  if (settings.title) {
    ctx.font = 'bold 14px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(settings.title, PAGE_W / 2, 52)
  }

  // 绘制格子
  for (let row = 0; row < rowsPerPage; row++) {
    for (let col = 0; col < colsPerPage; col++) {
      const x = MARGIN + col * gridSize
      const y = CONTENT_TOP + row * (gridSize + lineSpacing)
      drawGrid(ctx, x, y, gridSize, settings.grid_type)
    }
  }

  // 绘制字符
  const lines = (settings.text || '').split('\n')
  const startRow = pageIndex * rowsPerPage
  let currentRow = 0

  ctx.font = `${settings.font_size}px "${settings.font_name}"`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  for (const line of lines) {
    if (!line) {
      currentRow += 1
      continue
    }

    let lineRows = Math.ceil(line.length / colsPerPage)
    if (COPY_MODES.includes(settings.mode)) {
      lineRows *= 2
    }

    if (currentRow + lineRows <= startRow) {
      currentRow += lineRows
      continue
    }
    if (currentRow >= startRow + rowsPerPage) break

    const lineStartRow = Math.max(currentRow, startRow)
    const lineEndRow = Math.min(currentRow + lineRows, startRow + rowsPerPage)

    const startCharIdx = COPY_MODES.includes(settings.mode)
      ? Math.floor((lineStartRow - currentRow) / 2) * colsPerPage
      : (lineStartRow - currentRow) * colsPerPage

    let charIdx = startCharIdx
    for (let i = lineStartRow - startRow; i < lineEndRow - startRow; i++) {
      if (COPY_MODES.includes(settings.mode) && i % 2 === 1) continue

      for (let j = 0; j < colsPerPage; j++) {
        if (charIdx >= line.length) break
        const x = MARGIN + j * gridSize + settings.offset_x + gridSize / 2
        const y = CONTENT_TOP + i * (gridSize + lineSpacing) + settings.offset_y + gridSize / 2
        ctx.fillStyle = TRACE_MODES.includes(settings.mode) ? TRACE_COLOR : BLACK
        ctx.fillText(line[charIdx], x, y)
        charIdx++
      }
    }
    currentRow += lineRows
  }

  // 绘制页码
  if (settings.page_format && settings.page_format !== '不显示') {
    const pageText = getPageText(settings.page_format, pageIndex + 1, totalPages)
    if (pageText) {
      ctx.fillStyle = BLACK
      ctx.font = '11px sans-serif'
      ctx.textAlign = 'left'
      ctx.textBaseline = 'alphabetic'
      const textWidth = ctx.measureText(pageText).width
      let x, y
      switch (settings.page_position) {
        case '底部靠左':
          x = MARGIN
          y = PAGE_H - 20
          break
        case '底部靠右':
          x = PAGE_W - MARGIN - textWidth
          y = PAGE_H - 20
          break
        default: // 底部居中
          x = (PAGE_W - textWidth) / 2
          y = PAGE_H - 20
      }
      ctx.fillText(pageText, x, y)
    }
  }

  ctx.restore()
}

/** 便捷方法：排版 + 渲染某一页到 canvas */
export function drawPageToCanvas(canvas, settings, pageIndex, dpr = 1) {
  const totalPages = calculatePages(settings.text || '', settings.grid_type, settings.mode)
  const safeIndex = Math.min(Math.max(0, pageIndex), totalPages - 1)
  canvas.width = PAGE_W * dpr
  canvas.height = PAGE_H * dpr
  const ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  renderPage(ctx, settings, safeIndex, totalPages)
  return { totalPages, pageIndex: safeIndex }
}
