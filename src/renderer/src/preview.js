import { calculatePages, renderPage, PAGE_W, PAGE_H } from './engine/copybook.js'
import { createT, getLang } from '../../shared/i18n.js'

/**
 * 打印预览窗口：
 * 接收主进程转发的工程数据 -> 按 A4 2 倍分辨率渲染所有页 -> 通知主进程显示窗口
 * 支持缩放（适应页宽 / 40%~200%）、页码跟随滚动，可直接弹出系统打印对话框
 */

let lang = 'zh'
let t = (key) => key

const PRINT_DPR = 2
const A4_W_PX = 794
const ZOOM_MIN = 0.4
const ZOOM_MAX = 2
const ZOOM_STEP = 0.1

const scroll = document.getElementById('scroll')
const pagesEl = document.getElementById('pages')
const btnPrint = document.getElementById('btn-print')
const zoomLabel = document.getElementById('zoom-label')
const pageIndicator = document.getElementById('page-indicator')

let totalPages = 0
let zoom = 1
let fitWidth = true

function applyZoom() {
  if (fitWidth) {
    zoom = Math.min(2, Math.max(ZOOM_MIN, (scroll.clientWidth - 48) / A4_W_PX))
  }
  pagesEl.style.zoom = zoom
  zoomLabel.textContent = `${Math.round(zoom * 100)}%`
  updateIndicator()
}

function updateIndicator() {
  if (!totalPages) return
  const center = scroll.scrollTop + scroll.clientHeight * 0.35
  const scrollTop = scroll.getBoundingClientRect().top
  let current = 1
  Array.prototype.forEach.call(pagesEl.children, (page, i) => {
    const top = page.getBoundingClientRect().top - scrollTop + scroll.scrollTop
    if (top <= center) current = i + 1
  })
  pageIndicator.textContent = t('preview.page', { current, total: totalPages })
}

function applyStaticI18n() {
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en'
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n)
  })
  document.querySelectorAll('[data-i18n-title]').forEach((el) => {
    el.title = t(el.dataset.i18nTitle)
  })
  document.title = t('preview.title')
}

// 先拿到系统语言再渲染，保证页码等动态文案首帧即正确
const localeReady = window.api.getLocale().then((locale) => {
  lang = getLang(locale)
  t = createT(locale)
  applyStaticI18n()
})

window.api.onPrintData(async (settings) => {
  try {
    await localeReady
    await document.fonts.ready

    const pages = calculatePages(settings.text || '', settings.grid_type, settings.mode)
    pagesEl.innerHTML = ''
    totalPages = pages

    for (let i = 0; i < pages; i++) {
      const pageDiv = document.createElement('div')
      pageDiv.className = 'pdf-page'
      const canvas = document.createElement('canvas')
      canvas.width = PAGE_W * PRINT_DPR
      canvas.height = PAGE_H * PRINT_DPR
      const ctx = canvas.getContext('2d')
      ctx.setTransform(PRINT_DPR, 0, 0, PRINT_DPR, 0, 0)
      renderPage(ctx, settings, i, pages)
      pageDiv.appendChild(canvas)
      pagesEl.appendChild(pageDiv)
    }

    await new Promise((resolve) =>
      requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
    )
    await document.fonts.ready

    scroll.scrollTop = 0
    applyZoom()
    window.api.printRendered()
  } catch (err) {
    console.error('打印预览页面渲染失败', err)
  }
})

btnPrint.onclick = () => {
  btnPrint.disabled = true
  window.api.previewPrint()
  setTimeout(() => {
    btnPrint.disabled = false
  }, 1000)
}

document.getElementById('zoom-in').onclick = () => {
  fitWidth = false
  zoom = Math.min(ZOOM_MAX, Math.round((zoom + ZOOM_STEP) * 10) / 10)
  applyZoom()
}

document.getElementById('zoom-out').onclick = () => {
  fitWidth = false
  zoom = Math.max(ZOOM_MIN, Math.round((zoom - ZOOM_STEP) * 10) / 10)
  applyZoom()
}

document.getElementById('zoom-fit').onclick = () => {
  fitWidth = true
  applyZoom()
}

scroll.addEventListener('scroll', updateIndicator)
window.addEventListener('resize', () => {
  if (fitWidth) applyZoom()
})

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    window.close()
  } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'p') {
    e.preventDefault()
    btnPrint.click()
  }
})
