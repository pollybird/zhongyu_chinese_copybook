import { drawPageToCanvas, calculatePages, renderPage, PAGE_W, PAGE_H } from './engine/copybook.js'
import { createT } from '../../shared/i18n.js'

// 隐藏渲染窗口无可见界面，仅同步文档标题语言
window.api.getLocale().then((locale) => {
  document.title = createT(locale)('print.title')
})

/**
 * 打印渲染窗口：
 * 接收主进程转发的工程数据 -> 按 A4 2 倍分辨率渲染所有页 -> 通知主进程（printToPDF / print）
 */

const PRINT_DPR = 2

window.api.onPrintData(async (settings) => {
  try {
    await document.fonts.ready

    const totalPages = calculatePages(settings.text || '', settings.grid_type, settings.mode)
    const container = document.getElementById('pages')
    container.innerHTML = ''

    for (let i = 0; i < totalPages; i++) {
      const pageDiv = document.createElement('div')
      pageDiv.className = 'pdf-page'
      const canvas = document.createElement('canvas')
      canvas.width = PAGE_W * PRINT_DPR
      canvas.height = PAGE_H * PRINT_DPR
      const ctx = canvas.getContext('2d')
      ctx.setTransform(PRINT_DPR, 0, 0, PRINT_DPR, 0, 0)
      renderPage(ctx, settings, i, totalPages)
      pageDiv.appendChild(canvas)
      container.appendChild(pageDiv)
    }

    await new Promise((resolve) =>
      requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
    )
    await document.fonts.ready

    window.api.printRendered()
  } catch (err) {
    console.error('PDF 页面渲染失败', err)
  }
})
